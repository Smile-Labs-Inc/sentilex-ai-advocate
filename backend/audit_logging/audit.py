"""
Audit Logging System

For court admissibility, every agent interaction must be logged with:
- Timestamp
- Agent name
- Input data
- Output data
- Execution time
- Metadata

This creates an immutable audit trail that can be presented in court.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import contextmanager
import time

from schemas.messages import AuditLogEntry


class AuditLogger:
    """
    Audit logger for legal AI system.

    Creates structured logs of all agent interactions for court admissibility.
    """

    def __init__(self, log_dir: str = "logs", log_to_file: bool = True):
        """
        Initialize audit logger.

        Args:
            log_dir: Directory for log files
            log_to_file: Whether to write logs to file (vs. just in-memory)
        """
        self.log_dir = Path(log_dir)
        self.log_to_file = log_to_file
        self.session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.entries = []

        # Create log directory if it doesn't exist
        if self.log_to_file:
            self.log_dir.mkdir(parents=True, exist_ok=True)

            # Initialize session log file
            self.session_log_file = self.log_dir / \
                f"session_{self.session_id}.jsonl"

        # Set up standard Python logger
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)

        # Add handler if not already added
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            )
            self.logger.addHandler(handler)

    def log_agent_execution(
        self,
        agent: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        execution_time_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLogEntry:
        """
        Log an agent execution.

        Args:
            agent: Name of the agent
            input_data: Input data dictionary
            output_data: Output data dictionary
            execution_time_ms: Execution time in milliseconds (optional)
            metadata: Additional metadata (optional)

        Returns:
            The created AuditLogEntry
        """
        exec_time = execution_time_ms or 0.0

        entry = AuditLogEntry(
            timestamp=datetime.utcnow().isoformat(),
            agent=agent,
            input_data=input_data,
            output_data=output_data,
            execution_time_ms=exec_time,
            metadata=metadata or {}
        )

        # Store in memory
        self.entries.append(entry)

        # Write to file if enabled
        if self.log_to_file:
            self._write_entry_to_file(entry)

        # Log to standard logger
        self.logger.info(
            f"Agent '{agent}' executed in {exec_time:.2f}ms"
        )

        return entry

    @contextmanager
    def log_execution(
        self,
        agent: str,
        input_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Context manager for automatic execution time tracking.

        Usage:
            with audit_logger.log_execution("planner", input_data) as log:
                # Execute agent
                output_data = planner.invoke(input_data)
                log.set_output(output_data)

        Args:
            agent: Name of the agent
            input_data: Input data dictionary
            metadata: Additional metadata (optional)
        """
        start_time = time.time()
        log_context = {"output_data": None}

        class LogContext:
            def set_output(self, output_data: Dict[str, Any]):
                log_context["output_data"] = output_data

        try:
            yield LogContext()
        finally:
            execution_time_ms = (time.time() - start_time) * 1000
            output_data = log_context["output_data"] or {}

            self.log_agent_execution(
                agent=agent,
                input_data=input_data,
                output_data=output_data,
                execution_time_ms=execution_time_ms,
                metadata=metadata
            )

    def _write_entry_to_file(self, entry: AuditLogEntry):
        """
        Write a single audit entry to the session log file.

        Uses JSONL format (JSON Lines) for append-only logging.
        """
        try:
            with open(self.session_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry.dict(), ensure_ascii=False) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to write audit log: {str(e)}")

    def get_session_logs(self) -> list[AuditLogEntry]:
        """
        Get all audit logs for the current session.

        Returns:
            List of AuditLogEntry objects
        """
        return self.entries.copy()

    def export_session_logs(self, output_file: Optional[str] = None) -> str:
        """
        Export session logs to a JSON file.

        Args:
            output_file: Optional custom output file path

        Returns:
            Path to the exported file
        """
        if output_file is None:
            output_file = self.log_dir / f"export_{self.session_id}.json"
        else:
            output_file = Path(output_file)

        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Export as pretty-printed JSON
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                [entry.dict() for entry in self.entries],
                f,
                indent=2,
                ensure_ascii=False
            )

        self.logger.info(
            f"Exported {len(self.entries)} audit logs to {output_file}")
        return str(output_file)

    def generate_audit_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate a human-readable audit report.

        This report can be presented to auditors or in court.

        Args:
            output_file: Optional custom output file path

        Returns:
            Path to the generated report
        """
        if output_file is None:
            output_file = self.log_dir / f"report_{self.session_id}.md"
        else:
            output_file = Path(output_file)

        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Generate markdown report
        report_lines = [
            "# Legal AI System Audit Report",
            f"\n**Session ID:** {self.session_id}",
            f"\n**Generated:** {datetime.utcnow().isoformat()}",
            f"\n**Total Agent Executions:** {len(self.entries)}",
            "\n---\n",
            "\n## Execution Timeline\n"
        ]

        for idx, entry in enumerate(self.entries, 1):
            report_lines.append(f"\n### {idx}. Agent: {entry.agent}")
            report_lines.append(f"\n**Timestamp:** {entry.timestamp}")
            report_lines.append(
                f"\n**Execution Time:** {entry.execution_time_ms:.2f}ms")
            report_lines.append(f"\n**Input:**")
            report_lines.append(
                f"\n```json\n{json.dumps(entry.input_data, indent=2)}\n```")
            report_lines.append(f"\n**Output:**")
            report_lines.append(
                f"\n```json\n{json.dumps(entry.output_data, indent=2)}\n```")
            report_lines.append("\n---\n")

        # Write report
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

        self.logger.info(f"Generated audit report at {output_file}")
        return str(output_file)

    def clear_session(self):
        """Clear all in-memory logs for the current session."""
        self.entries = []
        self.logger.info("Cleared session audit logs")


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """
    Get the global audit logger instance.

    Returns:
        AuditLogger instance
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def configure_audit_logger(
    log_dir: str = "logs",
    log_to_file: bool = True
) -> AuditLogger:
    """
    Configure the global audit logger with custom settings.

    Args:
        log_dir: Directory for log files
        log_to_file: Whether to write logs to file

    Returns:
        Configured AuditLogger instance
    """
    global _audit_logger
    _audit_logger = AuditLogger(log_dir=log_dir, log_to_file=log_to_file)
    return _audit_logger
