"""Discharge upgrade legal resources connector.

Imports legal clinics, pro bono attorneys, VA accredited claims agents,
and educational resources for veterans seeking military discharge upgrades.

Veterans with less-than-honorable discharges face significant barriers to
VA benefits, healthcare, and employment. Legal assistance is critical for
navigating the discharge upgrade process through Discharge Review Boards (DRB)
and Boards for Correction of Military Records (BCMR).

Sources:
- Veterans Consortium Pro Bono Program
- National Veterans Legal Services Program (NVLSP)
- ABA Military & Veterans Legal Services Initiative
- State legal aid directories
- VA OGC Accreditation database
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from connectors.base import BaseConnector, ResourceCandidate, SourceMetadata

# Resource type to description mapping
RESOURCE_TYPE_DESCRIPTIONS = {
    "legal_clinic": "Legal clinic providing direct representation",
    "referral_network": "Network connecting veterans to legal providers",
    "online_resource": "Online legal information and assistance",
    "directory": "Directory of legal resources and representatives",
    "professional_organization": "Organization of legal professionals",
    "educational_resource": "Educational materials and self-help guides",
    "grant_program": "Grant-funded legal assistance program",
    "va_program": "VA-operated program",
    "government_board": "Military discharge review board",
}


class DischargeUpgradeConnector(BaseConnector):
    """Connector for discharge upgrade legal resources.

    Parses curated JSON file containing legal clinics, pro bono programs,
    VA accredited representatives, and educational resources that help
    veterans upgrade their military discharge characterization.

    These resources help veterans with:
    - Discharge Review Board (DRB) applications and representation
    - Board for Correction of Military Records (BCMR) cases
    - Understanding grounds for upgrade (PTSD, MST, TBI, DADT, etc.)
    - Finding VA-accredited attorneys and claims agents
    - Self-help resources for pro se applications
    """

    # Path to data file relative to project root
    DEFAULT_DATA_PATH = "data/reference/discharge_upgrade_resources.json"

    def __init__(self, data_path: str | Path | None = None):
        """Initialize the connector.

        Args:
            data_path: Path to JSON file. Falls back to DEFAULT_DATA_PATH.
        """
        if data_path is None:
            root = self._find_project_root()
            self.data_path = root / self.DEFAULT_DATA_PATH
        else:
            self.data_path = Path(data_path)

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
            name="Discharge Upgrade Legal Resources",
            url="https://www.vetsprobono.org/",
            tier=2,  # Established nonprofit/curated directory
            frequency="monthly",  # Updated monthly as programs change
            terms_url="https://www.vetsprobono.org/",
            requires_auth=False,
        )

    def run(self) -> list[ResourceCandidate]:
        """Parse discharge upgrade resources from JSON file.

        Returns:
            List of normalized ResourceCandidate objects.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"Discharge upgrade data file not found: {self.data_path}")

        with open(self.data_path) as f:
            data = json.load(f)

        resources: list[ResourceCandidate] = []
        now = datetime.now(UTC)

        for resource in data.get("resources", []):
            candidate = self._parse_resource(resource, fetched_at=now)
            resources.append(candidate)

        return resources

    def _parse_resource(
        self,
        resource: dict,
        fetched_at: datetime,
    ) -> ResourceCandidate:
        """Parse a resource entry into a ResourceCandidate.

        Args:
            resource: Resource data dictionary from JSON
            fetched_at: Timestamp when data was fetched

        Returns:
            ResourceCandidate for this resource.
        """
        resource_id = resource.get("id", "")
        name = resource["name"]
        resource_type = resource.get("type", "legal_clinic")
        description = resource.get("description", "")
        services = resource.get("services", [])
        eligibility = resource.get("eligibility")
        website = resource.get("website")
        intake_url = resource.get("intake_url")
        phone = resource.get("phone")
        email = resource.get("email")
        address = resource.get("address")
        city = resource.get("city")
        state = resource.get("state")
        zip_code = resource.get("zip_code")
        scope = resource.get("scope", "national")
        is_free = resource.get("free", True)
        notes = resource.get("notes")

        # Build title
        title = self._build_title(name, resource_type, state)

        # Build full description
        full_description = self._build_description(
            name=name,
            description=description,
            resource_type=resource_type,
            services=services,
            is_free=is_free,
            notes=notes,
        )

        # Build tags
        tags = self._build_tags(resource_type, services, scope, is_free, state)

        # Build how to apply
        how_to_apply = self._build_how_to_apply(
            name=name,
            website=website,
            intake_url=intake_url,
            phone=phone,
            email=email,
        )

        # Build eligibility text
        eligibility_text = self._build_eligibility(eligibility, is_free)

        return ResourceCandidate(
            title=title,
            description=full_description,
            source_url=website or "https://www.vetsprobono.org/",
            org_name=name,
            org_website=website,
            categories=["legal"],
            tags=tags,
            eligibility=eligibility_text,
            how_to_apply=how_to_apply,
            scope=scope,
            states=[state] if state else None,
            state=state,
            address=address,
            city=city,
            zip_code=zip_code,
            phone=self._normalize_phone(phone),
            email=email,
            raw_data={
                "resource_id": resource_id,
                "resource_type": resource_type,
                "services": services,
                "is_free": is_free,
                "intake_url": intake_url,
                "notes": notes,
            },
            fetched_at=fetched_at,
        )

    def _build_title(
        self,
        name: str,
        resource_type: str,
        state: str | None,
    ) -> str:
        """Build resource title.

        Args:
            name: Organization/resource name
            resource_type: Type of resource
            state: State code if applicable

        Returns:
            Formatted title string.
        """
        if resource_type == "educational_resource":
            return f"Discharge Upgrade Guide - {name}"
        elif resource_type == "directory":
            return f"Discharge Upgrade Directory - {name}"
        elif resource_type == "government_board":
            return name
        elif state:
            return f"Discharge Upgrade Legal Help - {name}"
        else:
            return f"Discharge Upgrade Legal Help - {name}"

    def _build_description(
        self,
        name: str,
        description: str,
        resource_type: str,
        services: list[str],
        is_free: bool,
        notes: str | None,
    ) -> str:
        """Build full resource description.

        Args:
            name: Organization name
            description: Base description
            resource_type: Type of resource
            services: List of services provided
            is_free: Whether services are free
            notes: Additional notes

        Returns:
            Formatted description string.
        """
        parts = [description]

        # Add type context
        type_desc = RESOURCE_TYPE_DESCRIPTIONS.get(resource_type)
        if type_desc and type_desc.lower() not in description.lower():
            parts.append(f"This is a {type_desc.lower()}.")

        # Add service highlights for legal clinics
        if resource_type == "legal_clinic" and services:
            service_highlights = []
            if "drb-representation" in services:
                service_highlights.append("Discharge Review Board representation")
            if "bcmr-representation" in services:
                service_highlights.append("Board for Correction of Military Records representation")
            if "pro-bono" in services:
                service_highlights.append("pro bono legal services")
            if service_highlights:
                parts.append(f"Services include {', '.join(service_highlights)}.")

        # Add cost information
        if is_free:
            parts.append("Services are provided free of charge to qualifying veterans.")
        else:
            parts.append("Note: This resource may charge fees for services.")

        # Add notes if present
        if notes:
            parts.append(notes)

        return " ".join(parts)

    def _build_eligibility(
        self,
        eligibility: str | None,
        is_free: bool,
    ) -> str:
        """Build eligibility text.

        Args:
            eligibility: Specific eligibility criteria
            is_free: Whether services are free

        Returns:
            Eligibility description string.
        """
        if eligibility:
            base = eligibility
        else:
            base = (
                "Veterans seeking to upgrade their military discharge characterization. "
                "Most programs focus on veterans with Other Than Honorable (OTH), "
                "Bad Conduct, or Undesirable discharges."
            )

        if is_free:
            return (
                f"{base} Services are free. Many programs prioritize veterans with "
                "PTSD, TBI, military sexual trauma (MST), or other mental health "
                "conditions that may have contributed to misconduct."
            )
        else:
            return (
                f"{base} This resource may charge fees. Consider contacting free "
                "pro bono programs first, such as the Veterans Consortium or NVLSP."
            )

    def _build_how_to_apply(
        self,
        name: str,
        website: str | None,
        intake_url: str | None,
        phone: str | None,
        email: str | None,
    ) -> str:
        """Build how-to-apply text.

        Args:
            name: Organization name
            website: Main website
            intake_url: Specific intake/application URL
            phone: Contact phone
            email: Contact email

        Returns:
            How to apply description string.
        """
        parts = [f"Contact {name} directly to request assistance."]

        if intake_url:
            parts.append(f"Apply online at {intake_url}.")
        elif website:
            parts.append(f"Visit {website} for intake information.")

        if phone:
            parts.append(f"Call {phone} to speak with someone.")

        if email:
            parts.append(f"Email {email} for assistance.")

        parts.append(
            "Before applying, gather your DD-214, service records, and any "
            "documentation of mental health conditions or mitigating circumstances."
        )

        return " ".join(parts)

    def _build_tags(
        self,
        resource_type: str,
        services: list[str],
        scope: str,
        is_free: bool,
        state: str | None,
    ) -> list[str]:
        """Build tags list.

        Args:
            resource_type: Type of resource
            services: List of services
            scope: Geographic scope
            is_free: Whether services are free
            state: State code if applicable

        Returns:
            List of tag strings.
        """
        tags = [
            "discharge-upgrade",
            "military-law",
            "legal",
        ]

        # Add pro-bono tag if free
        if is_free:
            tags.append("pro-bono")
            tags.append("free-legal-services")

        # Add resource type tags
        if resource_type == "legal_clinic":
            tags.append("legal-clinic")
        elif resource_type == "educational_resource":
            tags.append("self-help")
            tags.append("educational")
        elif resource_type == "directory":
            tags.append("directory")
        elif resource_type == "referral_network":
            tags.append("referral-network")

        # Add service-specific tags
        service_tag_map = {
            "drb-representation": "drb",
            "bcmr-representation": "bcmr",
            "va-benefits": "va-benefits",
            "va-appeals": "va-appeals",
            "trauma-informed": "trauma-informed",
            "women-veterans": "women-veterans",
            "accredited-representatives": "va-accredited",
        }

        for service in services:
            if service in service_tag_map:
                tags.append(service_tag_map[service])
            elif service == "discharge-upgrade":
                continue  # Already added
            else:
                # Add service as tag if not mapped
                safe_tag = service.lower().replace("_", "-")
                if safe_tag not in tags:
                    tags.append(safe_tag)

        # Add state tag
        if state:
            tags.append(f"state-{state.lower()}")

        # Add scope tag
        if scope == "national":
            tags.append("nationwide")

        return tags
