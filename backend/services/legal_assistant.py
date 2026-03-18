"""Legal AI assistant service — handles Q&A and AI responses."""

from typing import Optional
from backend.config import settings


LEGAL_DISCLAIMER = (
    "This information is for general educational purposes only and does not constitute "
    "legal advice. Please consult a qualified legal professional for advice specific to "
    "your situation."
)

# Demo-mode responses for common legal topics
DEMO_RESPONSES = {
    "contract": {
        "answer": (
            "A contract is a legally binding agreement between two or more parties. "
            "For a contract to be valid it must include: (1) an offer, (2) acceptance "
            "of that offer, (3) consideration (something of value exchanged), and "
            "(4) mutual intent to be bound. Contracts can be written or oral, although "
            "certain types — such as those involving real estate, marriage, or agreements "
            "lasting more than one year — must be in writing to be enforceable under the "
            "Statute of Frauds."
        ),
        "sources": ["Contract Law Fundamentals", "Statute of Frauds"],
    },
    "employment": {
        "answer": (
            "Employment law governs the relationship between employers and employees. "
            "Key areas include wrongful termination, discrimination, wage and hour laws, "
            "workplace safety, and benefits. In most jurisdictions employees have "
            "protections against termination based on race, gender, religion, national "
            "origin, age (40+), and disability. The EEOC (Equal Employment Opportunity "
            "Commission) handles federal employment discrimination claims in the US."
        ),
        "sources": ["Title VII of the Civil Rights Act", "EEOC Guidelines"],
    },
    "property": {
        "answer": (
            "Property law deals with the ownership, use, and transfer of real and personal "
            "property. Real property refers to land and structures; personal property covers "
            "movable items. Key concepts include: deeds (transferring ownership), mortgages "
            "(property used as security for a loan), easements (right to use another's land), "
            "and zoning regulations. Landlord-tenant law is a subcategory covering leases, "
            "security deposits, and eviction procedures."
        ),
        "sources": ["Real Property Law", "Landlord-Tenant Act"],
    },
    "criminal": {
        "answer": (
            "Criminal law involves offences against the state or society. Crimes are "
            "generally classified as misdemeanours (minor offences) or felonies (serious "
            "crimes). The prosecution must prove guilt 'beyond a reasonable doubt'. "
            "Key constitutional protections include the right to remain silent (5th Amendment), "
            "right to counsel (6th Amendment), and protection from unreasonable searches "
            "(4th Amendment). Sentences range from fines and probation to imprisonment."
        ),
        "sources": ["Criminal Code", "Constitutional Amendments"],
    },
    "family": {
        "answer": (
            "Family law covers matters such as marriage, divorce, child custody, adoption, "
            "and domestic violence. In divorce proceedings, courts divide marital property "
            "and may award alimony. Child custody decisions prioritise the 'best interests "
            "of the child', considering factors like parental fitness, stability, and the "
            "child's wishes (depending on age). Child support is calculated using state "
            "guidelines based on both parents' incomes."
        ),
        "sources": ["Family Law Act", "Child Welfare Guidelines"],
    },
    "default": {
        "answer": (
            "Thank you for your legal question. Based on general legal principles: "
            "legal matters typically require careful consideration of applicable statutes, "
            "case law, and the specific facts of your situation. Key steps include: "
            "(1) identifying the relevant area of law, (2) researching applicable statutes "
            "and precedents, (3) analysing how the law applies to your facts, and "
            "(4) considering any defences or counterclaims. I strongly recommend consulting "
            "a licensed attorney who can provide personalised advice for your specific "
            "circumstances."
        ),
        "sources": ["General Legal Principles"],
    },
}


def _select_demo_response(query: str) -> dict:
    """Return the most relevant demo response for the query."""
    query_lower = query.lower()
    for keyword, response in DEMO_RESPONSES.items():
        if keyword != "default" and keyword in query_lower:
            return response
    return DEMO_RESPONSES["default"]


async def get_legal_answer(
    query: str,
    history: list[dict],
    jurisdiction: Optional[str] = "general",
) -> dict:
    """Return an AI-generated (or demo) answer to a legal question."""
    if settings.demo_mode or not settings.openai_api_key:
        demo = _select_demo_response(query)
        return {
            "answer": demo["answer"],
            "disclaimer": LEGAL_DISCLAIMER,
            "sources": demo["sources"],
        }

    # Live OpenAI path
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)

        system_prompt = (
            "You are LegalMind AI, an expert legal assistant. You provide accurate, "
            "helpful information about legal topics. Always remind users that your "
            f"responses are for educational purposes only. Jurisdiction context: {jurisdiction}."
        )

        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-10:]:  # keep last 10 turns for context
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": query})

        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            max_tokens=1000,
            temperature=0.3,
        )

        answer = response.choices[0].message.content
        return {
            "answer": answer,
            "disclaimer": LEGAL_DISCLAIMER,
            "sources": ["OpenAI Legal AI Model"],
        }
    except Exception as exc:
        return {
            "answer": f"Unable to process your query at this time. Error: {exc}",
            "disclaimer": LEGAL_DISCLAIMER,
            "sources": [],
        }
