"""Data source connectors."""

from connectors.american_legion_posts import AmericanLegionPostsConnector
from connectors.apprenticeship import ApprenticeshipConnector
from connectors.base import BaseConnector, Connector, ResourceCandidate, SourceMetadata
from connectors.boulder_crest import BoulderCrestConnector
from connectors.careeronestop import CareerOneStopConnector
from connectors.certifications import CertificationsConnector
from connectors.cohen_veterans_network import CohenVeteransNetworkConnector
from connectors.cvso import CVSOConnector
from connectors.dav_chapters import DAVChaptersConnector
from connectors.discharge_upgrade import DischargeUpgradeConnector
from connectors.faith_based import FaithBasedConnector
from connectors.feeding_america import FeedingAmericaConnector
from connectors.final_salute import FinalSaluteConnector
from connectors.fisher_house import FisherHouseConnector
from connectors.gi_bill_schools import GIBillSchoolsConnector
from connectors.give_an_hour import GiveAnHourConnector
from connectors.gpd import GPDConnector
from connectors.headstrong import HeadstrongConnector
from connectors.home_base import HomeBaseConnector
from connectors.hrsa_health_centers import HRSAHealthCentersConnector
from connectors.hud_vash import HUDVASHConnector
from connectors.legal_aid import LegalAidConnector
from connectors.mental_health import MentalHealthConnector
from connectors.military_onesource import MilitaryOneSourceConnector
from connectors.rural_telehealth import RuralTelehealthConnector
from connectors.scholarships import ScholarshipsConnector
from connectors.skillbridge import SkillBridgeConnector
from connectors.ssvf import SSVFConnector
from connectors.stand_down_events import StandDownEventsConnector
from connectors.state_va import StateVAConnector
from connectors.state_va_offices import StateVAOfficesConnector
from connectors.sva_chapters import SVAChaptersConnector
from connectors.swords_to_plowshares import SwordsToPlowsharesConnector
from connectors.t2t_veterans_villages import T2TVeteransVillagesConnector
from connectors.team_rwb import TeamRWBConnector
from connectors.tribal_veterans import TribalVeteransConnector
from connectors.two_one_one import TwoOneOneConnector
from connectors.united_way import UnitedWayConnector
from connectors.us_vets import USVetsConnector
from connectors.va_community_care import VACommunityConnector
from connectors.va_gov import VAGovConnector
from connectors.va_patient_advocate import VAPatientAdvocateConnector
from connectors.vboc import VBOCConnector
from connectors.vcp import VCPConnector
from connectors.vet_centers import VetCentersConnector
from connectors.veteran_emergency_assistance import VeteranEmergencyAssistanceConnector
from connectors.veteran_employers import VeteranEmployersConnector
from connectors.veteran_food_assistance import VeteranFoodAssistanceConnector
from connectors.veterans_court import VeteransCourtConnector
from connectors.vfw_posts import VFWPostsConnector
from connectors.vso_post_locator import VSOPostLocatorConnector
from connectors.wounded_warrior_project import WoundedWarriorProjectConnector

# Optional: Crawl4AI-based discovery (requires crawl4ai package)
try:
    from connectors.crawl4ai_discovery import Crawl4AIDiscoveryConnector

    _CRAWL4AI_AVAILABLE = True
except ImportError:
    _CRAWL4AI_AVAILABLE = False
    Crawl4AIDiscoveryConnector = None  # type: ignore

__all__ = [
    "AmericanLegionPostsConnector",
    "ApprenticeshipConnector",
    "BaseConnector",
    "BoulderCrestConnector",
    "CareerOneStopConnector",
    "CertificationsConnector",
    "CohenVeteransNetworkConnector",
    "Connector",
    "CVSOConnector",
    "DAVChaptersConnector",
    "DischargeUpgradeConnector",
    "FaithBasedConnector",
    "FeedingAmericaConnector",
    "FinalSaluteConnector",
    "FisherHouseConnector",
    "GIBillSchoolsConnector",
    "GiveAnHourConnector",
    "GPDConnector",
    "HeadstrongConnector",
    "HomeBaseConnector",
    "HRSAHealthCentersConnector",
    "HUDVASHConnector",
    "LegalAidConnector",
    "MentalHealthConnector",
    "MilitaryOneSourceConnector",
    "ResourceCandidate",
    "RuralTelehealthConnector",
    "ScholarshipsConnector",
    "SkillBridgeConnector",
    "SourceMetadata",
    "SSVFConnector",
    "StandDownEventsConnector",
    "SwordsToPlowsharesConnector",
    "T2TVeteransVillagesConnector",
    "StateVAConnector",
    "StateVAOfficesConnector",
    "SVAChaptersConnector",
    "TeamRWBConnector",
    "TribalVeteransConnector",
    "TwoOneOneConnector",
    "UnitedWayConnector",
    "USVetsConnector",
    "VCPConnector",
    "VACommunityConnector",
    "VAGovConnector",
    "VAPatientAdvocateConnector",
    "VBOCConnector",
    "VetCentersConnector",
    "VeteranEmergencyAssistanceConnector",
    "VeteranEmployersConnector",
    "VeteranFoodAssistanceConnector",
    "VeteransCourtConnector",
    "VFWPostsConnector",
    "VSOPostLocatorConnector",
    "WoundedWarriorProjectConnector",
    # Optional (requires crawl4ai)
    "Crawl4AIDiscoveryConnector",
]
