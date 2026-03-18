"""Unit tests for internal service functions."""

import pytest

from backend.services.legal_assistant import _select_demo_response, DEMO_RESPONSES
from backend.services.document_analyzer import (
    _extract_key_points,
    _detect_risk_factors,
    _generate_recommendations,
)
from backend.services.case_researcher import _select_case_data, CASE_DATABASE


# ---------------------------------------------------------------------------
# Legal assistant
# ---------------------------------------------------------------------------


def test_select_demo_response_contract():
    result = _select_demo_response("What is a contract?")
    assert result == DEMO_RESPONSES["contract"]


def test_select_demo_response_employment():
    result = _select_demo_response("Tell me about employment law")
    assert result == DEMO_RESPONSES["employment"]


def test_select_demo_response_property():
    result = _select_demo_response("property lease question")
    assert result == DEMO_RESPONSES["property"]


def test_select_demo_response_criminal():
    result = _select_demo_response("criminal charges and defence")
    assert result == DEMO_RESPONSES["criminal"]


def test_select_demo_response_family():
    result = _select_demo_response("family law divorce custody")
    assert result == DEMO_RESPONSES["family"]


def test_select_demo_response_default():
    result = _select_demo_response("some completely unrelated question")
    assert result == DEMO_RESPONSES["default"]


# ---------------------------------------------------------------------------
# Document analyser
# ---------------------------------------------------------------------------

SAMPLE_TEXT = (
    "The Employee shall maintain confidentiality of all trade secrets. "
    "The Employer must pay salary by the 1st of each month. "
    "Either party agrees to arbitration for dispute resolution. "
    "The Employee warrants that they have no conflicting obligations."
)


def test_extract_key_points_finds_obligations():
    points = _extract_key_points(SAMPLE_TEXT)
    assert len(points) > 0
    combined = " ".join(points).lower()
    assert any(kw in combined for kw in ["shall", "must", "agrees", "warrant"])


def test_detect_risk_factors_finds_confidentiality():
    risks = _detect_risk_factors(SAMPLE_TEXT)
    combined = " ".join(risks).lower()
    assert "confidentiality" in combined or "arbitration" in combined


def test_detect_risk_factors_no_risks():
    risks = _detect_risk_factors("This is a friendly letter with no legal obligations.")
    assert len(risks) >= 1  # Should return the fallback message


def test_generate_recommendations_non_compete():
    risks = ["Non-compete clause detected — may restrict future employment or business."]
    recs = _generate_recommendations(risks)
    assert any("non-compete" in r.lower() for r in recs)


def test_generate_recommendations_arbitration():
    risks = ["Arbitration clause found — disputes may be resolved outside court."]
    recs = _generate_recommendations(risks)
    assert any("arbitration" in r.lower() for r in recs)


def test_generate_recommendations_always_includes_lawyer():
    recs = _generate_recommendations([])
    assert any("lawyer" in r.lower() or "legal" in r.lower() for r in recs)


# ---------------------------------------------------------------------------
# Case researcher
# ---------------------------------------------------------------------------


def test_select_case_data_contract():
    data = _select_case_data("breach of contract claim", "all")
    assert data == CASE_DATABASE["contract"]


def test_select_case_data_tort():
    data = _select_case_data("negligence tort claim", "tort")
    assert data == CASE_DATABASE["tort"]


def test_select_case_data_employment():
    data = _select_case_data("wrongful termination", "employment")
    assert data == CASE_DATABASE["employment"]


def test_select_case_data_property():
    data = _select_case_data("property boundary dispute", "all")
    assert data == CASE_DATABASE["property"]


def test_select_case_data_criminal():
    data = _select_case_data("criminal charge defence", "all")
    assert data == CASE_DATABASE["criminal"]


def test_select_case_data_default():
    data = _select_case_data("some obscure topic nobody knows about", "all")
    assert data == CASE_DATABASE["default"]


def test_case_database_structure():
    for key, value in CASE_DATABASE.items():
        assert "principles" in value, f"Missing 'principles' in {key}"
        assert "arguments" in value, f"Missing 'arguments' in {key}"
        assert "related" in value, f"Missing 'related' in {key}"
        assert len(value["principles"]) > 0
        assert len(value["arguments"]) > 0
