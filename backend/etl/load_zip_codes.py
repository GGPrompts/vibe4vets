"""Load US zip code centroids from Census ZCTA Gazetteer data.

Downloads the Census Bureau's ZCTA (ZIP Code Tabulation Area) Gazetteer file
and loads zip code centroids into the database for lat/lng lookup.

Usage:
    cd backend
    source .venv/bin/activate
    python -m etl.load_zip_codes
"""

import io
import logging
import zipfile
from pathlib import Path

import httpx
import pandas as pd
from sqlalchemy import text
from sqlmodel import Session

from app.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Census Bureau ZCTA Gazetteer file URL
CENSUS_ZCTA_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_zcta_national.zip"

# Local cache path
CACHE_DIR = Path(__file__).parent.parent / ".cache"
CACHE_FILE = CACHE_DIR / "2023_Gaz_zcta_national.txt"


def download_zcta_data() -> pd.DataFrame:
    """Download Census ZCTA Gazetteer file.

    Returns:
        DataFrame with GEOID, INTPTLAT, INTPTLONG columns.
    """
    # Check cache first
    if CACHE_FILE.exists():
        logger.info(f"Loading from cache: {CACHE_FILE}")
        return pd.read_csv(CACHE_FILE, sep="\t", dtype={"GEOID": str})

    logger.info(f"Downloading Census ZCTA data from {CENSUS_ZCTA_URL}")

    # Download the zip file
    response = httpx.get(CENSUS_ZCTA_URL, timeout=60.0, follow_redirects=True)
    response.raise_for_status()

    # Extract the text file from the zip
    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        # Find the .txt file in the archive
        txt_files = [n for n in zf.namelist() if n.endswith(".txt")]
        if not txt_files:
            raise ValueError("No .txt file found in ZCTA zip archive")

        logger.info(f"Extracting {txt_files[0]}")
        content = zf.read(txt_files[0])

    # Parse the tab-delimited file
    df = pd.read_csv(io.BytesIO(content), sep="\t", dtype={"GEOID": str})

    # Cache for future runs
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "wb") as f:
        f.write(content)
    logger.info(f"Cached to {CACHE_FILE}")

    return df


def _has_geog_column(session: Session) -> bool:
    """Check if zip_codes table has the geog (PostGIS) column."""
    result = session.execute(
        text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'zip_codes' AND column_name = 'geog'
        """)
    )
    return result.fetchone() is not None


def load_zip_codes(df: pd.DataFrame) -> int:
    """Load zip codes into the database.

    Args:
        df: DataFrame with GEOID, INTPTLAT, INTPTLONG columns.

    Returns:
        Number of rows inserted.
    """
    # Strip whitespace from column names (Census file has trailing spaces)
    df.columns = df.columns.str.strip()

    # Rename columns to match our schema
    # Census columns: GEOID (5-digit zip), INTPTLAT (latitude), INTPTLONG (longitude)
    # Also has ALAND, AWATER, ALAND_SQMI, AWATER_SQMI (areas)
    df = df.rename(
        columns={
            "GEOID": "zip_code",
            "INTPTLAT": "latitude",
            "INTPTLONG": "longitude",
        }
    )

    # Select only the columns we need
    # Note: Census file doesn't have city/state - we could enrich from another source
    df = df[["zip_code", "latitude", "longitude"]].copy()

    # Ensure zip_code is 5 characters (pad with leading zeros)
    df["zip_code"] = df["zip_code"].str.zfill(5)

    # Remove any rows with missing coordinates
    df = df.dropna(subset=["latitude", "longitude"])

    logger.info(f"Loading {len(df)} zip codes into database")

    with Session(engine) as session:
        # Check if PostGIS geography column exists
        has_geog = _has_geog_column(session)
        if has_geog:
            logger.info("PostGIS geog column detected, using spatial inserts")
        else:
            logger.info("No PostGIS geog column, using lat/lng only")

        # Clear existing data
        session.execute(text("TRUNCATE TABLE zip_codes"))

        # Insert in batches using raw SQL for performance
        batch_size = 5000
        inserted = 0

        for i in range(0, len(df), batch_size):
            batch = df.iloc[i : i + batch_size]

            if has_geog:
                # Build VALUES clause with PostGIS geography
                values = []
                for _, row in batch.iterrows():
                    values.append(
                        f"('{row['zip_code']}', {row['latitude']}, {row['longitude']}, "
                        f"ST_MakePoint({row['longitude']}, {row['latitude']})::geography)"
                    )

                sql = f"""
                    INSERT INTO zip_codes (zip_code, latitude, longitude, geog)
                    VALUES {", ".join(values)}
                    ON CONFLICT (zip_code) DO UPDATE SET
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        geog = EXCLUDED.geog
                """
            else:
                # Build VALUES clause without PostGIS (lat/lng only)
                values = []
                for _, row in batch.iterrows():
                    values.append(
                        f"('{row['zip_code']}', {row['latitude']}, {row['longitude']})"
                    )

                sql = f"""
                    INSERT INTO zip_codes (zip_code, latitude, longitude)
                    VALUES {", ".join(values)}
                    ON CONFLICT (zip_code) DO UPDATE SET
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude
                """

            session.execute(text(sql))
            inserted += len(batch)
            logger.info(f"Inserted {inserted}/{len(df)} zip codes")

        session.commit()

    return inserted


def verify_data() -> None:
    """Verify loaded data with spot checks."""
    test_zips = {
        "10001": ("New York", 40.75, -73.99),  # Manhattan
        "90210": ("Beverly Hills", 34.09, -118.41),  # Famous zip
        "20500": ("Washington DC", 38.89, -77.03),  # White House
    }

    with Session(engine) as session:
        # Check if PostGIS geography column exists
        has_geog = _has_geog_column(session)

        # Count total
        result = session.execute(text("SELECT COUNT(*) FROM zip_codes"))
        count = result.scalar()
        logger.info(f"Total zip codes loaded: {count}")

        # Spot check known zips
        for zip_code, (name, expected_lat, expected_lng) in test_zips.items():
            result = session.execute(
                text("SELECT latitude, longitude FROM zip_codes WHERE zip_code = :zip"),
                {"zip": zip_code},
            )
            row = result.fetchone()
            if row:
                lat, lng = row
                # Check within ~10 miles (0.15 degrees)
                if abs(lat - expected_lat) < 0.15 and abs(lng - expected_lng) < 0.15:
                    logger.info(f"[OK] {zip_code} ({name}): {lat:.4f}, {lng:.4f}")
                else:
                    logger.warning(
                        f"[WARN] {zip_code} ({name}): got ({lat:.4f}, {lng:.4f}), "
                        f"expected ({expected_lat:.4f}, {expected_lng:.4f})"
                    )
            else:
                logger.warning(f"[WARN] {zip_code} ({name}): not found")

        # Test spatial query (only if PostGIS is available)
        if has_geog:
            result = session.execute(
                text("""
                    SELECT zip_code, ST_Distance(geog, ST_MakePoint(-77.03, 38.89)::geography) as dist_m
                    FROM zip_codes
                    ORDER BY geog <-> ST_MakePoint(-77.03, 38.89)::geography
                    LIMIT 3
                """)
            )
            logger.info("Nearest zip codes to White House (38.89, -77.03):")
            for row in result:
                logger.info(f"  {row.zip_code}: {row.dist_m:.0f}m away")
        else:
            # Haversine-based query for non-PostGIS databases
            # Use approximate distance calculation
            result = session.execute(
                text("""
                    SELECT zip_code,
                           (6371000 * acos(
                               cos(radians(38.89)) * cos(radians(latitude)) *
                               cos(radians(longitude) - radians(-77.03)) +
                               sin(radians(38.89)) * sin(radians(latitude))
                           )) as dist_m
                    FROM zip_codes
                    ORDER BY dist_m
                    LIMIT 3
                """)
            )
            logger.info("Nearest zip codes to White House (38.89, -77.03) [Haversine]:")
            for row in result:
                logger.info(f"  {row.zip_code}: {row.dist_m:.0f}m away")


def main() -> None:
    """Main entry point."""
    logger.info("Loading US zip code centroids from Census ZCTA data")

    # Download data
    df = download_zcta_data()
    logger.info(f"Downloaded {len(df)} ZCTAs")

    # Load into database
    count = load_zip_codes(df)
    logger.info(f"Loaded {count} zip codes")

    # Verify
    verify_data()


if __name__ == "__main__":
    main()
