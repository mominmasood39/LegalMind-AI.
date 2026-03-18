"""Document analysis service — summarises and risk-checks legal documents."""

import re
from backend.config import settings


RISK_KEYWORDS = [
    "indemnif",
    "arbitration",
    "limitation of liability",
    "liquidated damages",
    "non-compete",
    "automatic renewal",
    "termination for convenience",
    "intellectual property assignment",
    "governing law",
    "force majeure",
    "confidentiality",
    "warranty disclaimer",
]


def _extract_key_points(text: str) -> list[str]:
    """Extract notable sentences from a document heuristically."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    key = []
    triggers = [
        "shall",
        "must",
        "agrees",
        "obligat",
        "liab",
        "terminat",
        "payment",
        "warrant",
        "indemnif",
        "confidential",
    ]
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20:
            continue
        if any(t in sentence.lower() for t in triggers):
            key.append(sentence[:250])
        if len(key) >= 8:
            break
    if not key:
        # Fall back: return first 5 sentences
        key = [s.strip()[:250] for s in sentences[:5] if len(s.strip()) > 20]
    return key


def _detect_risk_factors(text: str) -> list[str]:
    """Identify clauses that commonly carry legal risk."""
    text_lower = text.lower()
    risks = []
    descriptions = {
        "indemnif": "Indemnification clause detected — review scope and limits carefully.",
        "arbitration": "Arbitration clause found — disputes may be resolved outside court.",
        "limitation of liability": "Limitation of liability clause — check caps and exclusions.",
        "liquidated damages": "Liquidated damages clause — pre-agreed damages on breach.",
        "non-compete": "Non-compete clause — may restrict future employment or business.",
        "automatic renewal": "Automatic renewal clause — contract may renew without action.",
        "termination for convenience": "Termination for convenience — either party may exit without cause.",
        "intellectual property assignment": "IP assignment clause — ownership of created work may transfer.",
        "governing law": "Governing law clause — check which jurisdiction's law applies.",
        "force majeure": "Force majeure clause — review what events excuse performance.",
        "confidentiality": "Confidentiality / NDA clause — review scope and duration.",
        "warranty disclaimer": "Warranty disclaimer — review what protections are waived.",
    }
    for keyword, desc in descriptions.items():
        if keyword in text_lower:
            risks.append(desc)
    if not risks:
        risks.append("No obvious high-risk clauses detected. A full legal review is still recommended.")
    return risks


def _generate_recommendations(risk_factors: list[str]) -> list[str]:
    """Generate recommendations based on detected risks."""
    recs = [
        "Have a qualified lawyer review this document before signing.",
        "Keep a signed copy of the document for your records.",
    ]
    if any("non-compete" in r.lower() for r in risk_factors):
        recs.append("Negotiate the scope and duration of the non-compete clause.")
    if any("arbitration" in r.lower() for r in risk_factors):
        recs.append("Understand the arbitration rules and costs before agreeing.")
    if any("indemnif" in r.lower() for r in risk_factors):
        recs.append("Ensure indemnification obligations are mutual or appropriately limited.")
    if any("ip assignment" in r.lower() for r in risk_factors):
        recs.append("Clarify ownership of pre-existing IP that you bring to the engagement.")
    return recs


async def analyse_document(document_text: str, analysis_type: str = "general") -> dict:
    """Analyse a legal document and return a structured summary."""
    if settings.demo_mode or not settings.openai_api_key:
        # Heuristic analysis
        words = document_text.split()
        word_count = len(words)
        summary = (
            f"This document contains approximately {word_count} words. "
            "It appears to be a legal document. The following analysis highlights "
            "key obligations, risk areas, and recommendations based on a review of "
            "the document's content."
        )

        key_points = _extract_key_points(document_text)
        risk_factors = _detect_risk_factors(document_text)
        recommendations = _generate_recommendations(risk_factors)

        return {
            "summary": summary,
            "key_points": key_points,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
        }

    # Live OpenAI path
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)

        prompt = (
            f"Analyse the following legal document ({analysis_type} analysis). "
            "Provide: 1) A brief summary, 2) Key obligations and clauses, "
            "3) Risk factors, 4) Recommendations.\n\n"
            f"Document:\n{document_text[:8000]}"
        )

        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are an expert legal document analyser."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.2,
        )

        content = response.choices[0].message.content
        # Return a simplified parsed response
        return {
            "summary": content[:500],
            "key_points": [content[500:1000]] if len(content) > 500 else [],
            "risk_factors": ["See full analysis above"],
            "recommendations": ["Consult a legal professional for personalised advice."],
        }
    except Exception as exc:
        return {
            "summary": f"Analysis failed: {exc}",
            "key_points": [],
            "risk_factors": [],
            "recommendations": [],
        }
