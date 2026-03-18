"""Tests for the LegalMind-AI backend API."""

import pytest
from httpx import AsyncClient, ASGITransport

from backend.app import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "demo_mode" in data


# ---------------------------------------------------------------------------
# Legal Q&A
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_legal_query_basic(client):
    response = await client.post(
        "/api/legal-query",
        json={"query": "What is a contract?", "history": [], "jurisdiction": "general"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 0
    assert "disclaimer" in data


@pytest.mark.asyncio
async def test_legal_query_empty_raises_422(client):
    response = await client.post(
        "/api/legal-query",
        json={"query": "", "history": []},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_legal_query_employment(client):
    response = await client.post(
        "/api/legal-query",
        json={"query": "What is employment discrimination?", "history": []},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 10


@pytest.mark.asyncio
async def test_legal_query_with_history(client):
    history = [
        {"role": "user", "content": "What is a contract?"},
        {"role": "assistant", "content": "A contract is a legally binding agreement."},
    ]
    response = await client.post(
        "/api/legal-query",
        json={"query": "Can a verbal contract be enforceable?", "history": history},
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Document analysis
# ---------------------------------------------------------------------------


SAMPLE_CONTRACT = """
EMPLOYMENT AGREEMENT

This Employment Agreement ("Agreement") is entered into as of January 1, 2024,
between Acme Corporation ("Employer") and Jane Doe ("Employee").

1. POSITION. Employee shall serve as Software Engineer.

2. COMPENSATION. Employer shall pay Employee a salary of $80,000 per annum.

3. CONFIDENTIALITY. Employee agrees to keep all proprietary information
   confidential and shall not disclose it to third parties.

4. NON-COMPETE. Employee agrees not to work for a direct competitor for
   12 months following termination.

5. INDEMNIFICATION. Employee shall indemnify Employer against any claims
   arising from Employee's breach of this Agreement.

6. TERMINATION. Either party may terminate this Agreement with 30 days notice.
   Employer may terminate for cause without notice.

7. GOVERNING LAW. This Agreement is governed by the laws of the State of California.
"""


@pytest.mark.asyncio
async def test_analyse_document_basic(client):
    response = await client.post(
        "/api/analyse-document",
        json={"document_text": SAMPLE_CONTRACT, "analysis_type": "general"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "key_points" in data
    assert "risk_factors" in data
    assert "recommendations" in data
    assert isinstance(data["key_points"], list)
    assert isinstance(data["risk_factors"], list)


@pytest.mark.asyncio
async def test_analyse_document_detects_risks(client):
    response = await client.post(
        "/api/analyse-document",
        json={"document_text": SAMPLE_CONTRACT, "analysis_type": "contract"},
    )
    assert response.status_code == 200
    data = response.json()
    # Contract has non-compete, indemnification, confidentiality, and governing law clauses
    combined_risks = " ".join(data["risk_factors"]).lower()
    assert any(kw in combined_risks for kw in ["non-compete", "indemnif", "confidential", "governing"])


@pytest.mark.asyncio
async def test_analyse_document_empty_raises_422(client):
    response = await client.post(
        "/api/analyse-document",
        json={"document_text": "", "analysis_type": "general"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_upload_document_txt(client):
    txt_content = b"This is a simple confidentiality agreement. The parties agree to keep all information secret."
    response = await client.post(
        "/api/upload-document",
        files={"file": ("test.txt", txt_content, "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data


@pytest.mark.asyncio
async def test_upload_document_empty_txt(client):
    response = await client.post(
        "/api/upload-document",
        files={"file": ("empty.txt", b"   ", "text/plain")},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Case research
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_case_research_basic(client):
    response = await client.post(
        "/api/case-research",
        json={"query": "Breach of contract claim", "jurisdiction": "general"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "relevant_principles" in data
    assert "suggested_arguments" in data
    assert "related_areas" in data
    assert "research_notes" in data
    assert len(data["relevant_principles"]) > 0


@pytest.mark.asyncio
async def test_case_research_employment(client):
    response = await client.post(
        "/api/case-research",
        json={"query": "Wrongful termination employment claim", "case_type": "employment"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["relevant_principles"]) > 0
    assert len(data["suggested_arguments"]) > 0


@pytest.mark.asyncio
async def test_case_research_criminal(client):
    response = await client.post(
        "/api/case-research",
        json={"query": "Drug possession criminal charge", "case_type": "criminal"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "research_notes" in data


@pytest.mark.asyncio
async def test_case_research_empty_query_raises_422(client):
    response = await client.post(
        "/api/case-research",
        json={"query": ""},
    )
    assert response.status_code == 422
