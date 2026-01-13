"""ETL pipeline for Vibe4Vets veteran resource database.

This module provides:
- Normalization of ResourceCandidate data
- Deduplication across sources
- Enrichment with geocoding and trust scores
- Loading into the database with conflict handling
"""

from etl.models import ETLResult, NormalizedResource
from etl.pipeline import ETLPipeline

__all__ = [
    "ETLPipeline",
    "ETLResult",
    "NormalizedResource",
]
