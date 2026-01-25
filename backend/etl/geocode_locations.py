"""Geocode existing locations using Census Geocoder API.

Batch geocodes locations that have address/city/state/zip and updates
their latitude, longitude, and geography (geog) columns.

Strategy:
1. Try Census Geocoder API for full street addresses
2. Fall back to zip code centroid for addresses with zip but no match
3. Fall back to city centroid for "Citywide" or vague addresses

Usage:
    cd backend
    uv run python -m etl.geocode_locations

Options:
    --dry-run     Show what would be geocoded without making changes
    --limit N     Process only first N locations (for testing)
    --batch-size  Number of addresses per Census API batch (max 10000)
"""

import argparse
import csv
import io
import logging
import time
from dataclasses import dataclass
from uuid import UUID

import httpx
from sqlalchemy import text
from sqlmodel import Session

from app.database import engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Census Geocoder API endpoint
# Docs: https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html
CENSUS_BATCH_URL = "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"
CENSUS_BENCHMARK = "Public_AR_Current"
CENSUS_VINTAGE = "Current_Current"


@dataclass
class LocationRecord:
    """Location record for geocoding."""

    id: UUID
    address: str
    city: str
    state: str
    zip_code: str


@dataclass
class GeocodedResult:
    """Result from geocoding."""

    id: UUID
    latitude: float
    longitude: float
    match_type: str  # "exact", "zip_centroid", "city_centroid", "unmatched"
    match_quality: str | None = None  # Census match quality if available


def fetch_locations_to_geocode(limit: int | None = None) -> list[LocationRecord]:
    """Fetch locations that need geocoding."""
    with Session(engine) as session:
        sql = """
            SELECT id, address, city, state, zip_code
            FROM locations
            WHERE latitude IS NULL OR longitude IS NULL
        """
        if limit:
            sql += f" LIMIT {limit}"

        result = session.execute(text(sql))
        return [
            LocationRecord(
                id=row.id,
                address=row.address or "",
                city=row.city or "",
                state=row.state or "",
                zip_code=row.zip_code or "",
            )
            for row in result
        ]


def is_geocodable_address(loc: LocationRecord) -> bool:
    """Check if address is likely to geocode successfully.

    Returns True for street addresses, False for vague locations like
    "Citywide" or just a city name.
    """
    address_lower = loc.address.lower()

    # Skip vague/citywide addresses
    skip_patterns = [
        "citywide",
        "city-wide",
        "county-wide",
        "countywide",
        "statewide",
        "state-wide",
        "nationwide",
        "multiple locations",
        "various locations",
        "call for locations",
        "virtual",
        "online only",
        "remote",
    ]
    if any(pattern in address_lower for pattern in skip_patterns):
        return False

    # Address is just the city name
    if loc.address.lower().strip() == loc.city.lower().strip():
        return False

    # Very short address (likely just neighborhood/area name)
    if len(loc.address.strip()) < 10:
        return False

    # Has a street number (good indicator of real address)
    if any(c.isdigit() for c in loc.address[:10]):
        return True

    # Has common street suffixes
    street_suffixes = [
        "street",
        "st",
        "avenue",
        "ave",
        "road",
        "rd",
        "drive",
        "dr",
        "boulevard",
        "blvd",
        "lane",
        "ln",
        "way",
        "place",
        "pl",
        "circle",
        "court",
        "ct",
        "highway",
        "hwy",
        "parkway",
        "pkwy",
    ]
    words = address_lower.split()
    return any(suffix in words for suffix in street_suffixes)


def prepare_census_batch(locations: list[LocationRecord]) -> str:
    """Prepare CSV for Census Geocoder batch API.

    Format: Unique ID, Street address, City, State, ZIP
    """
    output = io.StringIO()
    writer = csv.writer(output)

    for loc in locations:
        # Census API expects: UniqueID, Street, City, State, ZIP
        writer.writerow([str(loc.id), loc.address, loc.city, loc.state, loc.zip_code])

    return output.getvalue()


def parse_census_response(response_text: str) -> dict[str, GeocodedResult]:
    """Parse Census Geocoder batch response.

    Response format: ID, Input Address, Match, Match Type, Matched Address,
                     Coordinates (lon,lat), TIGER Line ID, Side
    """
    results = {}
    reader = csv.reader(io.StringIO(response_text))

    for row in reader:
        if len(row) < 6:
            continue

        loc_id = row[0]
        match_status = row[2] if len(row) > 2 else ""
        match_type = row[3] if len(row) > 3 else ""
        coords = row[5] if len(row) > 5 else ""

        if match_status.lower() == "match" and coords:
            try:
                # Coords are in lon,lat format
                lon, lat = coords.split(",")
                results[loc_id] = GeocodedResult(
                    id=UUID(loc_id),
                    latitude=float(lat),
                    longitude=float(lon),
                    match_type="exact",
                    match_quality=match_type,
                )
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse coordinates for {loc_id}: {e}")

    return results


def geocode_batch_census(locations: list[LocationRecord]) -> dict[str, GeocodedResult]:
    """Geocode a batch of locations using Census Geocoder API.

    Max batch size is 10,000 addresses.
    """
    if not locations:
        return {}

    csv_data = prepare_census_batch(locations)

    try:
        response = httpx.post(
            CENSUS_BATCH_URL,
            data={
                "benchmark": CENSUS_BENCHMARK,
                "vintage": CENSUS_VINTAGE,
            },
            files={"addressFile": ("addresses.csv", csv_data, "text/csv")},
            timeout=120.0,
        )
        response.raise_for_status()
        return parse_census_response(response.text)

    except httpx.HTTPError as e:
        logger.error(f"Census API error: {e}")
        return {}


def get_zip_centroids() -> dict[str, tuple[float, float]]:
    """Load zip code centroids from database."""
    with Session(engine) as session:
        result = session.execute(text("SELECT zip_code, latitude, longitude FROM zip_codes"))
        return {row.zip_code: (row.latitude, row.longitude) for row in result}


# Major US city centroids for fallback geocoding
# These cover the most common "Citywide" entries in the database
CITY_CENTROIDS: dict[tuple[str, str], tuple[float, float]] = {
    # (city_lower, state): (lat, lon)
    ("new york", "NY"): (40.7128, -74.0060),
    ("new york city", "NY"): (40.7128, -74.0060),
    ("manhattan", "NY"): (40.7831, -73.9712),
    ("brooklyn", "NY"): (40.6782, -73.9442),
    ("queens", "NY"): (40.7282, -73.7949),
    ("bronx", "NY"): (40.8448, -73.8648),
    ("staten island", "NY"): (40.5795, -74.1502),
    ("jamaica", "NY"): (40.6915, -73.8057),
    ("st. albans", "NY"): (40.6895, -73.7632),
    ("los angeles", "CA"): (34.0522, -118.2437),
    ("san diego", "CA"): (32.7157, -117.1611),
    ("san francisco", "CA"): (37.7749, -122.4194),
    ("san jose", "CA"): (37.3382, -121.8863),
    ("santa barbara", "CA"): (34.4208, -119.6982),
    ("chicago", "IL"): (41.8781, -87.6298),
    ("houston", "TX"): (29.7604, -95.3698),
    ("dallas", "TX"): (32.7767, -96.7970),
    ("austin", "TX"): (30.2672, -97.7431),
    ("san antonio", "TX"): (29.4241, -98.4936),
    ("phoenix", "AZ"): (33.4484, -112.0740),
    ("philadelphia", "PA"): (39.9526, -75.1652),
    ("pittsburgh", "PA"): (40.4406, -79.9959),
    ("mechanicsburg", "PA"): (40.2143, -76.9986),
    ("detroit", "MI"): (42.3314, -83.0458),
    ("washington", "DC"): (38.9072, -77.0369),
    ("seattle", "WA"): (47.6062, -122.3321),
    ("denver", "CO"): (39.7392, -104.9903),
    ("boston", "MA"): (42.3601, -71.0589),
    ("atlanta", "GA"): (33.7490, -84.3880),
    ("miami", "FL"): (25.7617, -80.1918),
    ("tampa", "FL"): (27.9506, -82.4572),
    ("orlando", "FL"): (28.5383, -81.3792),
    ("jacksonville", "FL"): (30.3322, -81.6557),
    ("baltimore", "MD"): (39.2904, -76.6122),
    ("portland", "OR"): (45.5152, -122.6784),
    ("las vegas", "NV"): (36.1699, -115.1398),
    ("minneapolis", "MN"): (44.9778, -93.2650),
    ("st. louis", "MO"): (38.6270, -90.1994),
    ("kansas city", "MO"): (39.0997, -94.5786),
    ("cleveland", "OH"): (41.4993, -81.6944),
    ("columbus", "OH"): (39.9612, -82.9988),
    ("cincinnati", "OH"): (39.1031, -84.5120),
    ("indianapolis", "IN"): (39.7684, -86.1581),
    ("nashville", "TN"): (36.1627, -86.7816),
    ("memphis", "TN"): (35.1495, -90.0490),
    ("charlotte", "NC"): (35.2271, -80.8431),
    ("raleigh", "NC"): (35.7796, -78.6382),
    ("virginia beach", "VA"): (36.8529, -75.9780),
    ("norfolk", "VA"): (36.8508, -76.2859),
    ("richmond", "VA"): (37.5407, -77.4360),
    ("milwaukee", "WI"): (43.0389, -87.9065),
    ("albuquerque", "NM"): (35.0844, -106.6504),
    ("tucson", "AZ"): (32.2226, -110.9747),
    ("oklahoma city", "OK"): (35.4676, -97.5164),
    ("new orleans", "LA"): (29.9511, -90.0715),
    ("sacramento", "CA"): (38.5816, -121.4944),
    ("anchorage", "AK"): (61.2181, -149.9003),
    ("honolulu", "HI"): (21.3069, -157.8583),
}


def get_city_centroid(city: str, state: str) -> tuple[float, float] | None:
    """Look up city centroid from predefined list.

    Args:
        city: City name (case insensitive)
        state: Two-letter state code

    Returns:
        (latitude, longitude) tuple or None if not found
    """
    # Normalize city name
    city_lower = city.lower().strip()

    # Try exact match first
    if (city_lower, state) in CITY_CENTROIDS:
        return CITY_CENTROIDS[(city_lower, state)]

    # Try without common suffixes
    for suffix in [" city", " metro area", " metropolitan area", " area"]:
        if city_lower.endswith(suffix):
            base_city = city_lower[: -len(suffix)]
            if (base_city, state) in CITY_CENTROIDS:
                return CITY_CENTROIDS[(base_city, state)]

    # Try "City of X" pattern
    if city_lower.startswith("city of "):
        base_city = city_lower[8:]
        if (base_city, state) in CITY_CENTROIDS:
            return CITY_CENTROIDS[(base_city, state)]

    return None


# State centroids (approximate geographic centers)
STATE_CENTROIDS: dict[str, tuple[float, float]] = {
    "AL": (32.806671, -86.791130),
    "AK": (61.370716, -152.404419),
    "AZ": (33.729759, -111.431221),
    "AR": (34.969704, -92.373123),
    "CA": (36.116203, -119.681564),
    "CO": (39.059811, -105.311104),
    "CT": (41.597782, -72.755371),
    "DE": (39.318523, -75.507141),
    "DC": (38.897438, -77.026817),
    "FL": (27.766279, -81.686783),
    "GA": (33.040619, -83.643074),
    "HI": (21.094318, -157.498337),
    "ID": (44.240459, -114.478828),
    "IL": (40.349457, -88.986137),
    "IN": (39.849426, -86.258278),
    "IA": (42.011539, -93.210526),
    "KS": (38.526600, -96.726486),
    "KY": (37.668140, -84.670067),
    "LA": (31.169546, -91.867805),
    "ME": (44.693947, -69.381927),
    "MD": (39.063946, -76.802101),
    "MA": (42.230171, -71.530106),
    "MI": (43.326618, -84.536095),
    "MN": (45.694454, -93.900192),
    "MS": (32.741646, -89.678696),
    "MO": (38.456085, -92.288368),
    "MT": (46.921925, -110.454353),
    "NE": (41.125370, -98.268082),
    "NV": (38.313515, -117.055374),
    "NH": (43.452492, -71.563896),
    "NJ": (40.298904, -74.521011),
    "NM": (34.840515, -106.248482),
    "NY": (42.165726, -74.948051),
    "NC": (35.630066, -79.806419),
    "ND": (47.528912, -99.784012),
    "OH": (40.388783, -82.764915),
    "OK": (35.565342, -96.928917),
    "OR": (44.572021, -122.070938),
    "PA": (40.590752, -77.209755),
    "RI": (41.680893, -71.511780),
    "SC": (33.856892, -80.945007),
    "SD": (44.299782, -99.438828),
    "TN": (35.747845, -86.692345),
    "TX": (31.054487, -97.563461),
    "UT": (40.150032, -111.862434),
    "VT": (44.045876, -72.710686),
    "VA": (37.769337, -78.169968),
    "WA": (47.400902, -121.490494),
    "WV": (38.491226, -80.954453),
    "WI": (44.268543, -89.616508),
    "WY": (42.755966, -107.302490),
}


def get_state_centroid(state: str) -> tuple[float, float] | None:
    """Get state centroid for statewide resources."""
    return STATE_CENTROIDS.get(state.upper())


def geocode_with_fallbacks(
    locations: list[LocationRecord],
    zip_centroids: dict[str, tuple[float, float]],
    batch_size: int = 1000,
) -> list[GeocodedResult]:
    """Geocode locations with fallback strategy.

    1. Try Census API for geocodable addresses
    2. Fall back to zip centroid
    3. Mark as unmatched if no fallback available
    """
    results = []

    # Separate geocodable vs fallback-only addresses
    geocodable = [loc for loc in locations if is_geocodable_address(loc)]
    fallback_only = [loc for loc in locations if not is_geocodable_address(loc)]

    logger.info(f"Geocodable addresses: {len(geocodable)}")
    logger.info(f"Fallback-only addresses: {len(fallback_only)}")

    # Process geocodable addresses in batches
    census_results: dict[str, GeocodedResult] = {}
    for i in range(0, len(geocodable), batch_size):
        batch = geocodable[i : i + batch_size]
        logger.info(f"Processing Census batch {i // batch_size + 1} ({len(batch)} addresses)")

        batch_results = geocode_batch_census(batch)
        census_results.update(batch_results)

        # Rate limit: Census API recommends 1 request per second
        if i + batch_size < len(geocodable):
            time.sleep(1)

    logger.info(f"Census API matched: {len(census_results)}")

    # Process all locations with fallbacks
    for loc in locations:
        loc_id_str = str(loc.id)

        # Check Census result first
        if loc_id_str in census_results:
            results.append(census_results[loc_id_str])
            continue

        # Fallback to zip centroid
        if loc.zip_code and loc.zip_code in zip_centroids:
            lat, lon = zip_centroids[loc.zip_code]
            results.append(
                GeocodedResult(
                    id=loc.id,
                    latitude=lat,
                    longitude=lon,
                    match_type="zip_centroid",
                )
            )
            continue

        # Try partial zip match (first 3 digits)
        if loc.zip_code and len(loc.zip_code) >= 3:
            prefix = loc.zip_code[:3]
            matching_zips = [z for z in zip_centroids if z.startswith(prefix)]
            if matching_zips:
                # Use first matching zip as approximation
                lat, lon = zip_centroids[matching_zips[0]]
                results.append(
                    GeocodedResult(
                        id=loc.id,
                        latitude=lat,
                        longitude=lon,
                        match_type="zip_prefix_centroid",
                    )
                )
                continue

        # Try city centroid lookup for Citywide/vague addresses
        city_coords = get_city_centroid(loc.city, loc.state)
        if city_coords:
            lat, lon = city_coords
            results.append(
                GeocodedResult(
                    id=loc.id,
                    latitude=lat,
                    longitude=lon,
                    match_type="city_centroid",
                )
            )
            continue

        # Try state centroid for Statewide resources
        state_coords = get_state_centroid(loc.state)
        if state_coords:
            lat, lon = state_coords
            results.append(
                GeocodedResult(
                    id=loc.id,
                    latitude=lat,
                    longitude=lon,
                    match_type="state_centroid",
                )
            )
            continue

        # No match available
        logger.debug(f"No geocode for: {loc.address}, {loc.city}, {loc.state} {loc.zip_code}")

    return results


def update_locations(results: list[GeocodedResult], dry_run: bool = False) -> int:
    """Update locations with geocoded coordinates.

    Returns count of updated records.
    """
    if dry_run:
        logger.info(f"DRY RUN: Would update {len(results)} locations")
        return 0

    updated = 0
    with Session(engine) as session:
        for result in results:
            sql = """
                UPDATE locations
                SET latitude = :lat,
                    longitude = :lon,
                    geog = ST_MakePoint(:lon, :lat)::geography
                WHERE id = :id
            """
            session.execute(
                text(sql),
                {"lat": result.latitude, "lon": result.longitude, "id": result.id},
            )
            updated += 1

            if updated % 100 == 0:
                logger.info(f"Updated {updated}/{len(results)} locations")

        session.commit()

    return updated


def print_stats(results: list[GeocodedResult]) -> None:
    """Print geocoding statistics."""
    by_type = {}
    for r in results:
        by_type[r.match_type] = by_type.get(r.match_type, 0) + 1

    logger.info("Geocoding results:")
    for match_type, count in sorted(by_type.items()):
        logger.info(f"  {match_type}: {count}")


def verify_spatial_index() -> None:
    """Verify PostGIS is working with a test query."""
    with Session(engine) as session:
        # Test nearest neighbor query
        result = session.execute(
            text("""
                SELECT l.id, l.city, l.state,
                       ST_Distance(l.geog, ST_MakePoint(-77.03, 38.89)::geography) as dist_m
                FROM locations l
                WHERE l.geog IS NOT NULL
                ORDER BY l.geog <-> ST_MakePoint(-77.03, 38.89)::geography
                LIMIT 5
            """)
        )

        logger.info("Nearest locations to Washington DC (38.89, -77.03):")
        for row in result:
            dist_miles = row.dist_m / 1609.34
            logger.info(f"  {row.city}, {row.state}: {dist_miles:.1f} miles")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Geocode locations using Census API")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--limit", type=int, help="Process only first N locations")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Batch size for Census API (max 10000)",
    )
    args = parser.parse_args()

    logger.info("Geocoding locations using Census Geocoder API")

    # Fetch locations needing geocoding
    locations = fetch_locations_to_geocode(limit=args.limit)
    logger.info(f"Found {len(locations)} locations to geocode")

    if not locations:
        logger.info("No locations need geocoding")
        return

    # Load zip centroids for fallback
    zip_centroids = get_zip_centroids()
    logger.info(f"Loaded {len(zip_centroids)} zip code centroids")

    # Geocode with fallbacks
    results = geocode_with_fallbacks(locations, zip_centroids, batch_size=args.batch_size)

    # Print stats
    print_stats(results)

    # Update database
    updated = update_locations(results, dry_run=args.dry_run)
    logger.info(f"Updated {updated} locations")

    # Verify spatial queries work
    if not args.dry_run and results:
        verify_spatial_index()


if __name__ == "__main__":
    main()
