"""Tests for specialist relevance and output quality hardening."""

import json
from pathlib import Path

import main


def test_clean_summary_text_strips_json_wrapper():
    text = 'json {"summary": "Concrete actionable summary."}'
    assert main._clean_summary_text(text) == "Concrete actionable summary."


def test_clean_summary_text_rejects_simulation_language():
    text = "Simulated data engineering review based on assumed changed files."
    assert main._clean_summary_text(text) == ""


def test_specialist_relevance_for_data_engineering_matches_sql_changes(tmp_path, monkeypatch):
    workspace = Path(main.__file__).parent / "workspace"
    workspace.mkdir(exist_ok=True)
    diff_json = workspace / "diff.json"
    diff_json.write_text(json.dumps({"file_list": ["data/sql/orders.sql"]}))

    monkeypatch.setattr(main, "_CHANGED_FILE_CANDIDATES", None)
    relevant, reason = main._specialist_relevance("data_engineering")
    assert relevant is True
    assert "Matched" in reason


def test_specialist_relevance_for_data_engineering_ignores_unrelated_changes(monkeypatch):
    monkeypatch.setattr(main, "_CHANGED_FILE_CANDIDATES", ["src/ui/button.tsx"])
    relevant, _reason = main._specialist_relevance("data_engineering")
    assert relevant is False


def test_build_no_relevant_output_is_explicit():
    data = main._build_no_relevant_output("data_engineering", "No SQL/schema files changed.")
    assert data["findings"] == []
    assert data["severity_counts"]["critical"] == 0
    assert "did not detect relevant changed files" in data["summary"].lower()
