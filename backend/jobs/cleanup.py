"""Database cleanup job.

Removes old records from tables that grow unbounded:
- change_logs: Field-level change history
- source_records: Raw data audit trail

Runs daily to prevent disk exhaustion.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlmodel import Session, delete, func, select, text

from app.models.review import ChangeLog
from app.models.source import SourceRecord
from jobs.base import BaseJob


class CleanupJob(BaseJob):
    """Job to clean up old records from growing tables.

    Applies retention policies:
    - change_logs: Keep last 30 days
    - source_records: Keep last 90 days
    """

    # Default retention periods in days
    CHANGE_LOG_RETENTION_DAYS = 30
    SOURCE_RECORD_RETENTION_DAYS = 90

    @property
    def name(self) -> str:
        return "cleanup"

    @property
    def description(self) -> str:
        return "Clean up old change logs and source records"

    def execute(
        self,
        session: Session,
        change_log_days: int | None = None,
        source_record_days: int | None = None,
        dry_run: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Run the cleanup job.

        Args:
            session: Database session.
            change_log_days: Days to retain change logs (default: 30).
            source_record_days: Days to retain source records (default: 90).
            dry_run: If True, count but don't delete.
            **kwargs: Additional arguments (ignored).

        Returns:
            Statistics dictionary with deleted counts.
        """
        change_log_days = change_log_days or self.CHANGE_LOG_RETENTION_DAYS
        source_record_days = source_record_days or self.SOURCE_RECORD_RETENTION_DAYS

        now = datetime.now(UTC)
        change_log_cutoff = now - timedelta(days=change_log_days)
        source_record_cutoff = now - timedelta(days=source_record_days)

        # Count records to delete
        change_log_count = self._count_old_change_logs(session, change_log_cutoff)
        source_record_count = self._count_old_source_records(session, source_record_cutoff)

        self._log(
            f"Found {change_log_count} change_logs older than {change_log_days} days, "
            f"{source_record_count} source_records older than {source_record_days} days"
        )

        deleted_change_logs = 0
        deleted_source_records = 0

        if not dry_run:
            if change_log_count > 0:
                deleted_change_logs = self._delete_old_change_logs(session, change_log_cutoff)
                self._log(f"Deleted {deleted_change_logs} old change_logs")

            if source_record_count > 0:
                deleted_source_records = self._delete_old_source_records(session, source_record_cutoff)
                self._log(f"Deleted {deleted_source_records} old source_records")

        stats: dict[str, Any] = {
            "dry_run": dry_run,
            "change_log_cutoff_days": change_log_days,
            "source_record_cutoff_days": source_record_days,
            "change_logs_found": change_log_count,
            "change_logs_deleted": deleted_change_logs,
            "source_records_found": source_record_count,
            "source_records_deleted": deleted_source_records,
        }

        return stats

    def _count_old_change_logs(self, session: Session, cutoff: datetime) -> int:
        """Count change_logs older than cutoff."""
        stmt = select(func.count(ChangeLog.id)).where(ChangeLog.timestamp < cutoff)
        result = session.exec(stmt).one()
        return result or 0

    def _count_old_source_records(self, session: Session, cutoff: datetime) -> int:
        """Count source_records older than cutoff."""
        stmt = select(func.count(SourceRecord.id)).where(SourceRecord.fetched_at < cutoff)
        result = session.exec(stmt).one()
        return result or 0

    def _delete_old_change_logs(self, session: Session, cutoff: datetime) -> int:
        """Delete change_logs older than cutoff."""
        stmt = delete(ChangeLog).where(ChangeLog.timestamp < cutoff)
        result = session.exec(stmt)  # type: ignore[call-overload]
        return result.rowcount  # type: ignore[attr-defined]

    def _delete_old_source_records(self, session: Session, cutoff: datetime) -> int:
        """Delete source_records older than cutoff."""
        stmt = delete(SourceRecord).where(SourceRecord.fetched_at < cutoff)
        result = session.exec(stmt)  # type: ignore[call-overload]
        return result.rowcount  # type: ignore[attr-defined]

    def _format_message(self, stats: dict[str, Any]) -> str:
        """Format cleanup statistics into a message."""
        if stats.get("dry_run"):
            return (
                f"Dry run: would delete {stats['change_logs_found']} change_logs, "
                f"{stats['source_records_found']} source_records"
            )

        return (
            f"Cleanup complete: deleted {stats['change_logs_deleted']} change_logs, "
            f"{stats['source_records_deleted']} source_records"
        )


class TruncateChangeLogsJob(BaseJob):
    """Emergency job to truncate change_logs table.

    Use when disk is critically full. This is faster than DELETE
    because it doesn't log individual row deletions.
    """

    @property
    def name(self) -> str:
        return "truncate_change_logs"

    @property
    def description(self) -> str:
        return "Emergency truncate of change_logs table"

    def execute(
        self,
        session: Session,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Truncate the change_logs table.

        Args:
            session: Database session.
            **kwargs: Additional arguments (ignored).

        Returns:
            Statistics dictionary.
        """
        # Count before truncate
        stmt = select(func.count(ChangeLog.id))
        count_before = session.exec(stmt).one() or 0

        self._log(f"Truncating change_logs table ({count_before} rows)")

        # TRUNCATE is much faster than DELETE for large tables
        session.exec(text("TRUNCATE TABLE change_logs"))  # type: ignore[call-overload]

        stats: dict[str, Any] = {
            "rows_before": count_before,
            "rows_after": 0,
        }

        return stats

    def _format_message(self, stats: dict[str, Any]) -> str:
        """Format truncate statistics into a message."""
        return f"Truncated change_logs: removed {stats['rows_before']} rows"
