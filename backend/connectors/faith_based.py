"""Faith-Based Veteran Service Organizations connector.

Imports curated data about faith-based organizations providing veteran services
including housing, food assistance, financial aid, and support services.

Organizations included:
- The Salvation Army (emergency shelters, transitional housing, SSVF)
- Catholic Charities USA (SSVF, housing, support services)
- Volunteers of America (housing, employment, mental health)
- Lutheran Services in America (housing, support)
- Jewish War Veterans of the USA (benefits counseling, peer support)
- Convoy of Hope (food distribution, disaster relief)
- St. Vincent de Paul Society (emergency assistance)
- Episcopal Relief & Development (disaster response)
- UMCOR (disaster recovery, housing)
- Team Rubicon (disaster response, veteran volunteering)
- Samaritan's Purse (marriage retreats, disaster relief)

Source: Curated from official organization websites and VA resources
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata


class FaithBasedConnector(BaseConnector):
    """Connector for faith-based veteran service organizations.

    Loads curated data about national faith-based organizations that provide
    housing, food, financial assistance, and support services to veterans.

    These are tier 2 (established nonprofits) programs that often partner
    with the VA through SSVF, GPD, and other federal programs.
    """

    # Data file path relative to project root
    DATA_PATH = "data/reference/faith_based_veteran_services.json"

    def __init__(self, data_path: str | Path | None = None):
        """Initialize the connector.

        Args:
            data_path: Path to data JSON. Falls back to DATA_PATH.
        """
        root = self._find_project_root()
        self.data_path = Path(data_path) if data_path else root / self.DATA_PATH

    def _find_project_root(self) -> Path:
        """Find project root (directory containing 'data' folder)."""
        current = Path(__file__).resolve().parent
        while current != current.parent:
            if (current / "data").is_dir():
                return current
            current = current.parent
        return Path(__file__).resolve().parent.parent

    @property
    def metadata(self) -> SourceMetadata:
        """Return source metadata."""
        return SourceMetadata(
            name="Faith-Based Veteran Service Organizations",
            url="https://www.va.gov/homeless/nationalcallcenter.asp",
            tier=2,  # Established nonprofits
            frequency="monthly",  # Programs change infrequently
            terms_url=None,
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse and return faith-based veteran programs.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        now = datetime.now(UTC)

        data = self._load_data()
        if not data:
            return []

        resources: list[ResourceCandidate] = []

        for program in data.get("programs", []):
            candidate = self._parse_program(program, fetched_at=now)
            resources.append(candidate)

        return resources

    def _load_data(self) -> dict:
        """Load program data from JSON file."""
        if not self.data_path.exists():
            return {}

        with open(self.data_path) as f:
            return json.load(f)

    def _parse_program(
        self,
        program: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a program entry into a ResourceCandidate.

        Args:
            program: Dictionary containing program data.
            fetched_at: Timestamp when data was fetched.

        Returns:
            ResourceCandidate for this faith-based program.
        """
        org_name = program.get("org_name", "Unknown Organization")
        program_name = program.get("program_name", "Veteran Services")
        website = program.get("website")
        phone = program.get("phone")
        email = program.get("email")

        title = self._build_title(org_name, program_name)
        description = self._build_description(program)
        eligibility = self._build_eligibility(program)
        how_to_apply = self._build_how_to_apply(program)
        tags = self._build_tags(program)
        categories = self._get_categories(program)

        # Determine scope
        scope = program.get("scope", "national")
        states = program.get("states")

        return ResourceCandidate(
            title=title,
            description=description,
            source_url=website or "https://www.va.gov/homeless/nationalcallcenter.asp",
            org_name=org_name,
            org_website=website,
            categories=categories,
            tags=tags,
            phone=self._normalize_phone(phone),
            email=email,
            eligibility=eligibility,
            how_to_apply=how_to_apply,
            scope=scope,
            states=states,
            raw_data=program,
            fetched_at=fetched_at,
        )

    def _build_title(self, org_name: str, program_name: str) -> str:
        """Build resource title."""
        # Use common abbreviations for well-known organizations
        abbrevs = {
            "The Salvation Army": "Salvation Army",
            "Catholic Charities USA": "Catholic Charities",
            "Volunteers of America": "VOA",
            "Lutheran Services in America": "Lutheran Services",
            "Lutheran Immigration and Refugee Service (LIRS)": "LIRS",
            "Jewish War Veterans of the USA": "Jewish War Veterans",
            "St. Vincent de Paul Society": "St. Vincent de Paul",
            "Episcopal Relief & Development": "Episcopal Relief",
            "United Methodist Committee on Relief (UMCOR)": "UMCOR",
            "Samaritan's Purse": "Samaritan's Purse",
        }
        org_short = abbrevs.get(org_name, org_name)
        return f"{org_short} - {program_name}"

    def _build_description(self, program: dict) -> str:
        """Build resource description with key program details."""
        parts = []

        # Use the curated description if available
        description = program.get("description")
        if description:
            parts.append(description)

        # Add services summary if not already covered
        services = program.get("services", [])
        if services and not description:
            org_name = program.get("org_name", "This organization")
            program_name = program.get("program_name", "")
            readable_services = self._format_services(services[:5])
            parts.append(
                f"{org_name}'s {program_name} provides {readable_services} for veterans."
            )

        return " ".join(parts)

    def _format_services(self, services: list[str]) -> str:
        """Format services into readable list."""
        service_labels = {
            "emergency_shelter": "emergency shelter",
            "transitional_housing": "transitional housing",
            "permanent_supportive_housing": "permanent supportive housing",
            "rapid_rehousing": "rapid rehousing",
            "homelessness_prevention": "homelessness prevention",
            "food_assistance": "food assistance",
            "food_distribution": "food distribution",
            "food_pantry": "food pantry",
            "case_management": "case management",
            "job_training": "job training",
            "job_placement": "job placement",
            "employment_training": "employment training",
            "employment_services": "employment services",
            "employment_assistance": "employment assistance",
            "career_counseling": "career counseling",
            "resume_assistance": "resume assistance",
            "interview_preparation": "interview preparation",
            "skills_training": "skills training",
            "substance_abuse_treatment": "substance abuse treatment",
            "substance_abuse_counseling": "substance abuse counseling",
            "mental_health_services": "mental health services",
            "mental_health_counseling": "mental health counseling",
            "emergency_financial_assistance": "emergency financial assistance",
            "rental_assistance": "rental assistance",
            "rent_assistance": "rent assistance",
            "utility_assistance": "utility assistance",
            "claims_assistance": "VA claims assistance",
            "benefits_counseling": "benefits counseling",
            "legal_services": "legal services",
            "legal_referrals": "legal referrals",
            "immigration_assistance": "immigration assistance",
            "disaster_relief": "disaster relief",
            "disaster_response": "disaster response",
            "recovery_assistance": "recovery assistance",
            "emergency_supplies": "emergency supplies",
            "community_support": "community support",
            "peer_support": "peer support",
            "mentorship": "mentorship",
            "life_skills_training": "life skills training",
            "life_skills": "life skills training",
            "job_readiness": "job readiness",
            "residential_treatment": "residential treatment",
            "hospital_visitation": "hospital visitation",
            "memorial_services": "memorial services",
            "community_outreach": "community outreach",
            "resource_connection": "resource connections",
            "furniture_assistance": "furniture assistance",
            "thrift_stores": "thrift store vouchers",
            "community_resilience": "community resilience",
            "referral_services": "referral services",
            "recovery_case_management": "recovery case management",
            "housing_repair": "housing repair",
            "home_repair": "home repair",
            "volunteer_opportunities": "volunteer opportunities",
            "veteran_community": "veteran community",
            "skills_development": "skills development",
            "purpose_through_service": "purpose through service",
            "marriage_retreat": "marriage retreats",
            "spiritual_counseling": "spiritual counseling",
            "outdoor_activities": "outdoor activities",
            "aftercare_program": "aftercare programs",
            "debris_removal": "debris removal",
            "social_events": "social events",
            "veteran_outreach": "veteran outreach",
            "family_reunification": "family reunification",
            "employer_partnerships": "employer partnerships",
        }

        readable = []
        for s in services:
            readable.append(service_labels.get(s, s.replace("_", " ")))

        if len(readable) > 3:
            return ", ".join(readable[:-1]) + ", and " + readable[-1]
        elif len(readable) == 2:
            return " and ".join(readable)
        else:
            return readable[0] if readable else "support services"

    def _build_eligibility(self, program: dict) -> str:
        """Build eligibility description."""
        eligibility = program.get("eligibility", {})
        parts = []

        # Main eligibility summary
        summary = eligibility.get("summary")
        if summary:
            parts.append(summary)

        # Veteran status requirement
        if eligibility.get("veteran_status_required") is True:
            if "veteran" not in summary.lower():
                parts.append("Must be a veteran or military family member.")
        elif eligibility.get("veteran_status_required") is False:
            parts.append("Open to all community members, including veterans.")

        # Income limit
        income_limit = eligibility.get("income_limit")
        if income_limit and income_limit != "Based on need":
            parts.append(f"Income requirement: {income_limit}.")

        # Documentation required
        docs = eligibility.get("documentation_required", [])
        if docs:
            doc_labels = {
                "dd214": "DD-214",
                "state_id": "state ID",
                "proof_of_income": "proof of income",
                "lease_or_eviction_notice": "lease or eviction notice",
                "va_eligibility_letter": "VA eligibility letter",
                "proof_of_need": "proof of need",
                "military_service_records": "military service records",
                "proof_of_combat_injury": "proof of combat injury",
            }
            doc_names = [doc_labels.get(d, d) for d in docs]
            if doc_names:
                parts.append(f"Required documentation: {', '.join(doc_names)}.")

        # Additional notes
        notes = eligibility.get("notes")
        if notes:
            parts.append(notes)

        return " ".join(parts) if parts else "Contact the organization for eligibility requirements."

    def _build_how_to_apply(self, program: dict) -> str:
        """Build application instructions."""
        parts = []

        # Phone
        phone = program.get("phone")
        if phone:
            parts.append(f"Phone: {phone}")

        # Email
        email = program.get("email")
        if email:
            parts.append(f"Email: {email}")

        # Website
        website = program.get("website")
        if website:
            parts.append(f"Website: {website}")

        # If no specific info, provide generic guidance
        if not parts:
            org_name = program.get("org_name", "the organization")
            parts.append(
                f"Contact {org_name} through their website or call the VA National "
                "Homeless Veterans Hotline at 1-877-4AID-VET (1-877-424-3838) for referrals."
            )

        return " ".join(parts)

    def _get_categories(self, program: dict) -> list[str]:
        """Get categories from program data."""
        categories = program.get("categories", [])

        # If no categories specified, infer from services
        if not categories:
            services = set(program.get("services", []))
            inferred = set()

            # Housing-related services
            housing_keywords = {
                "emergency_shelter",
                "transitional_housing",
                "permanent_supportive_housing",
                "rapid_rehousing",
                "homelessness_prevention",
                "rental_assistance",
                "rent_assistance",
                "housing_repair",
                "home_repair",
            }
            if housing_keywords & services:
                inferred.add("housing")

            # Food-related services
            food_keywords = {"food_assistance", "food_distribution", "food_pantry"}
            if food_keywords & services:
                inferred.add("food")

            # Financial services
            financial_keywords = {
                "emergency_financial_assistance",
                "utility_assistance",
            }
            if financial_keywords & services:
                inferred.add("financial")

            # Employment services
            employment_keywords = {
                "job_training",
                "job_placement",
                "employment_training",
                "employment_services",
                "career_counseling",
            }
            if employment_keywords & services:
                inferred.add("employment")

            # Mental health services
            mental_health_keywords = {
                "mental_health_services",
                "mental_health_counseling",
                "substance_abuse_treatment",
                "substance_abuse_counseling",
            }
            if mental_health_keywords & services:
                inferred.add("mentalHealth")

            # Support services (catch-all)
            if not inferred:
                inferred.add("supportServices")

            return sorted(inferred)

        return categories

    def _build_tags(self, program: dict) -> list[str]:
        """Build tags list."""
        tags = [
            "faith-based",
            "veteran-services",
        ]

        services = set(program.get("services", []))
        categories = program.get("categories", [])

        # Add category-based tags
        if "housing" in categories:
            tags.append("housing-assistance")
        if "food" in categories:
            tags.append("food-assistance")
        if "financial" in categories:
            tags.append("financial-assistance")
        if "employment" in categories:
            tags.append("employment-services")
        if "mentalHealth" in categories:
            tags.append("mental-health")
        if "supportServices" in categories:
            tags.append("support-services")
        if "family" in categories:
            tags.append("military-families")

        # Add service-specific tags
        if "emergency_shelter" in services or "transitional_housing" in services:
            tags.append("homeless-services")
        if "rapid_rehousing" in services or "homelessness_prevention" in services:
            tags.append("ssvf")
        if "disaster_relief" in services or "disaster_response" in services:
            tags.append("disaster-relief")
        if "claims_assistance" in services or "benefits_counseling" in services:
            tags.append("va-benefits")
        if "peer_support" in services or "community_support" in services:
            tags.append("peer-support")

        # Add organization-specific tags
        org_name = program.get("org_name", "").lower()
        if "salvation army" in org_name:
            tags.append("salvation-army")
        elif "catholic charities" in org_name:
            tags.append("catholic-charities")
        elif "volunteers of america" in org_name:
            tags.append("volunteers-of-america")
        elif "lutheran" in org_name:
            tags.append("lutheran-services")
        elif "jewish war veterans" in org_name:
            tags.append("jewish-war-veterans")
        elif "convoy of hope" in org_name:
            tags.append("convoy-of-hope")
        elif "st. vincent de paul" in org_name:
            tags.append("st-vincent-de-paul")
        elif "episcopal" in org_name:
            tags.append("episcopal")
        elif "methodist" in org_name or "umcor" in org_name:
            tags.append("umcor")
        elif "team rubicon" in org_name:
            tags.append("team-rubicon")
        elif "samaritan" in org_name:
            tags.append("samaritans-purse")

        # Add scope tag
        scope = program.get("scope", "national")
        if scope == "national":
            tags.append("nationwide")

        return tags
