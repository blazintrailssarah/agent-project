"""Persistent review memory with local JSON and optional mem0 Cloud backend.

This module provides a unified memory interface for the CrewAI review system.
By default, memories are stored as JSON files in .crewai/memory/ and committed
to the repository — making review preferences version-controlled and portable.

For teams that want richer semantic search across memories, set USE_MEM0_CLOUD=true
and MEM0_API_KEY in your environment to use mem0 Cloud as the backend.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

MEMORY_DIR = (Path(__file__).parent.parent / "memory").resolve()
SUPPRESSIONS_FILE = MEMORY_DIR / "suppressions.json"
MEMORY_FILE = MEMORY_DIR / "memory.json"


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"Could not load {path.name}: {e}")
        return {}


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


class MemoryManager:
    """Unified memory interface — local JSON with optional mem0 Cloud."""

    def __init__(self):
        self._suppressions = _load_json(SUPPRESSIONS_FILE)
        self._memory = _load_json(MEMORY_FILE)
        self._mem0_client: Optional[Any] = None
        self._dirty = False

        if os.getenv("USE_MEM0_CLOUD", "").lower() == "true":
            self._init_mem0()

    def _init_mem0(self) -> None:
        api_key = os.getenv("MEM0_API_KEY")
        if not api_key:
            logger.warning("USE_MEM0_CLOUD=true but MEM0_API_KEY not set — falling back to local")
            return
        try:
            from mem0 import MemoryClient

            self._mem0_client = MemoryClient(api_key=api_key)
            logger.info("✅ mem0 Cloud connected")
        except ImportError:
            logger.warning(
                "mem0 package not installed — pip install mem0ai — falling back to local"
            )
        except Exception as e:
            logger.warning(f"mem0 init failed: {e} — falling back to local")

    def is_suppressed(self, finding_title: str, file_path: str = "") -> bool:
        for sup in self._suppressions.get("suppressions", []):
            if not sup.get("active", True):
                continue

            if sup.get("expires"):
                try:
                    if datetime.fromisoformat(sup["expires"]) < datetime.now():
                        continue
                except ValueError:
                    pass

            pattern = sup.get("pattern", "").lower()
            if pattern and pattern in finding_title.lower():
                file_glob = sup.get("file_glob", "")
                if not file_glob or fnmatch(file_path, file_glob):
                    logger.info(f"Suppressed: '{finding_title}' (rule: {sup['id']})")
                    return True

        return False

    def filter_findings(self, findings: list[dict]) -> tuple[list[dict], int]:
        kept = []
        suppressed_count = 0
        for finding in findings:
            title = finding.get("title", "")
            file_path = finding.get("file", "")
            if self.is_suppressed(title, file_path):
                suppressed_count += 1
            else:
                kept.append(finding)
        return kept, suppressed_count

    def add_suppression(
        self,
        pattern: str,
        reason: str,
        file_glob: str = "",
        added_by: str = "crewai",
        expires: Optional[str] = None,
    ) -> str:
        suppressions = self._suppressions.setdefault("suppressions", [])
        existing_ids = [s.get("id", "") for s in suppressions]
        next_num = 1
        while f"sup-{next_num:03d}" in existing_ids:
            next_num += 1
        sup_id = f"sup-{next_num:03d}"

        suppressions.append(
            {
                "id": sup_id,
                "pattern": pattern,
                "file_glob": file_glob,
                "reason": reason,
                "added_by": added_by,
                "added_date": datetime.now().strftime("%Y-%m-%d"),
                "expires": expires,
                "active": True,
            }
        )
        self._dirty = True
        logger.info(f"Added suppression {sup_id}: '{pattern}'")

        if self._mem0_client:
            try:
                self._mem0_client.add(
                    f"Suppress finding: {pattern}. Reason: {reason}. Files: {file_glob or 'all'}",
                    user_id="crewai-review",
                    metadata={"type": "suppression", "id": sup_id},
                )
            except Exception as e:
                logger.warning(f"mem0 add failed: {e}")

        return sup_id

    def add_learned_pattern(
        self,
        observation: str,
        source: str = "review",
        confidence: float = 0.8,
    ) -> None:
        patterns = self._memory.setdefault("learned_patterns", [])
        existing_ids = [p.get("id", "") for p in patterns]
        next_num = 1
        while f"pat-{next_num:03d}" in existing_ids:
            next_num += 1

        patterns.append(
            {
                "id": f"pat-{next_num:03d}",
                "observation": observation,
                "confidence": confidence,
                "source": source,
                "learned_date": datetime.now().strftime("%Y-%m-%d"),
            }
        )
        self._dirty = True

        if self._mem0_client:
            try:
                self._mem0_client.add(
                    f"Learned pattern: {observation} (confidence: {confidence})",
                    user_id="crewai-review",
                    metadata={"type": "learned_pattern", "source": source},
                )
            except Exception as e:
                logger.warning(f"mem0 add failed: {e}")

    def record_review(self, pr_number: str, findings_count: int) -> None:
        history = self._memory.setdefault("review_history", {})
        history["total_reviews"] = history.get("total_reviews", 0) + 1
        history["last_review"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        trend = history.setdefault("findings_trend", [])
        trend.append(
            {
                "pr": pr_number,
                "findings": findings_count,
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
        )
        if len(trend) > 50:
            trend[:] = trend[-50:]

        self._dirty = True

    def get_context_for_review(self) -> str:
        lines = []

        patterns = self._memory.get("learned_patterns", [])
        if patterns:
            lines.append("## Learned Patterns About This Codebase")
            for p in patterns[-10:]:
                lines.append(f"- {p['observation']} (confidence: {p.get('confidence', 'N/A')})")
            lines.append("")

        suppressions = self._suppressions.get("suppressions", [])
        active = [s for s in suppressions if s.get("active", True)]
        if active:
            lines.append("## Active Review Suppressions")
            lines.append("Do NOT flag these patterns — the team has marked them acceptable:")
            for s in active:
                scope = f" (files: {s['file_glob']})" if s.get("file_glob") else ""
                lines.append(f"- {s['pattern']}{scope} — {s.get('reason', 'no reason given')}")
            lines.append("")

        if self._mem0_client:
            try:
                results = self._mem0_client.search(
                    "codebase patterns and review preferences",
                    user_id="crewai-review",
                    limit=10,
                )
                if results:
                    lines.append("## mem0 Cloud Memories")
                    for mem in results:
                        lines.append(f"- {mem.get('memory', mem.get('text', str(mem)))}")
                    lines.append("")
            except Exception as e:
                logger.warning(f"mem0 search failed: {e}")

        return "\n".join(lines) if lines else ""

    def save(self) -> bool:
        if not self._dirty:
            return False
        _save_json(SUPPRESSIONS_FILE, self._suppressions)
        _save_json(MEMORY_FILE, self._memory)
        logger.info("💾 Memory saved to disk")
        return True


_instance: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    global _instance
    if _instance is None:
        _instance = MemoryManager()
    return _instance
