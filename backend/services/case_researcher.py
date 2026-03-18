"""Case research service — provides relevant legal principles and arguments."""

from backend.config import settings

CASE_DATABASE = {
    "contract": {
        "principles": [
            "Offer and acceptance must be clear and unambiguous.",
            "Consideration must be of value, though need not be adequate.",
            "Parties must have capacity to contract (adult, sane, not under duress).",
            "Contracts induced by fraud or misrepresentation are voidable.",
            "The parol evidence rule limits introduction of prior oral agreements.",
        ],
        "arguments": [
            "Establish breach by showing non-performance of a material term.",
            "Demonstrate damages flowing directly from the breach.",
            "Assert promissory estoppel if no formal contract exists but reliance occurred.",
            "Challenge enforceability based on unconscionability or public policy.",
        ],
        "related": ["Commercial Law", "Consumer Protection", "Agency Law"],
    },
    "tort": {
        "principles": [
            "Negligence requires duty, breach, causation, and damages (DBCD).",
            "The 'reasonable person' standard applies in negligence cases.",
            "Strict liability applies in certain product liability and abnormally dangerous activity cases.",
            "Intentional torts require proof of intent to commit the act.",
            "Comparative/contributory negligence may reduce or bar recovery.",
        ],
        "arguments": [
            "Establish duty of care owed by defendant to plaintiff.",
            "Show the defendant's conduct fell below the reasonable person standard.",
            "Prove actual and proximate causation linking breach to harm.",
            "Quantify compensatory damages (economic + non-economic).",
            "Consider punitive damages for egregious or intentional misconduct.",
        ],
        "related": ["Personal Injury", "Product Liability", "Professional Negligence"],
    },
    "employment": {
        "principles": [
            "At-will employment allows termination for any lawful reason.",
            "Discrimination based on protected characteristics is prohibited.",
            "Retaliation against whistleblowers is generally unlawful.",
            "Wage theft and overtime violations carry civil and criminal penalties.",
            "Employees have a right to organise and bargain collectively.",
        ],
        "arguments": [
            "Show adverse employment action (termination, demotion, reduced pay).",
            "Establish membership in a protected class.",
            "Demonstrate causal link between protected status and adverse action.",
            "Provide comparator evidence showing disparate treatment.",
            "Use temporal proximity for retaliation claims.",
        ],
        "related": ["Labor Law", "Workers Compensation", "OSHA Compliance"],
    },
    "property": {
        "principles": [
            "Title to real property is transferred by deed.",
            "Adverse possession may transfer title after statutory period of open, hostile, continuous use.",
            "Easements give a right to use another's land for a specific purpose.",
            "Landlords must maintain habitable premises; tenants must pay rent.",
            "Zoning laws restrict permissible uses of land.",
        ],
        "arguments": [
            "Establish clear chain of title using recorded deeds.",
            "Challenge adverse possession by showing permissive use.",
            "Assert habitability defences against eviction for rent non-payment.",
            "Contest zoning violations with variance or non-conforming use arguments.",
        ],
        "related": ["Landlord-Tenant Law", "Real Estate Transactions", "Environmental Law"],
    },
    "criminal": {
        "principles": [
            "Guilt must be proven beyond a reasonable doubt.",
            "Defendants have a constitutional right to counsel.",
            "Double jeopardy prevents retrial for the same offence after acquittal.",
            "Evidence obtained in violation of 4th Amendment may be excluded.",
            "Mens rea (guilty mind) is an element of most crimes.",
        ],
        "arguments": [
            "Challenge the sufficiency of evidence on each element of the offence.",
            "Move to suppress unlawfully obtained evidence.",
            "Assert affirmative defences: self-defence, duress, insanity.",
            "Challenge chain of custody for physical evidence.",
            "Attack witness credibility through cross-examination.",
        ],
        "related": ["Constitutional Law", "Evidence", "Criminal Procedure"],
    },
    "default": {
        "principles": [
            "Legal analysis begins with identifying the applicable area of law.",
            "Statutes and regulations provide the primary legal framework.",
            "Case law (precedent) interprets and applies statutes.",
            "Procedural rules govern how claims are filed and litigated.",
            "Equitable doctrines (estoppel, laches, unclean hands) may apply.",
        ],
        "arguments": [
            "Identify all potential legal theories before filing.",
            "Research jurisdiction-specific statutes of limitations.",
            "Gather and preserve all relevant documentary evidence.",
            "Consider alternative dispute resolution before litigation.",
        ],
        "related": ["Civil Procedure", "Evidence", "Ethics"],
    },
}


def _select_case_data(query: str, case_type: str) -> dict:
    """Select the most relevant case data for the query."""
    text = (query + " " + case_type).lower()
    for key in CASE_DATABASE:
        if key != "default" and key in text:
            return CASE_DATABASE[key]
    return CASE_DATABASE["default"]


async def research_case(
    query: str,
    jurisdiction: str = "general",
    case_type: str = "all",
) -> dict:
    """Return relevant legal principles and arguments for a research query."""
    if settings.demo_mode or not settings.openai_api_key:
        data = _select_case_data(query, case_type)
        notes = (
            f"Research query: '{query}' | Jurisdiction: {jurisdiction} | "
            "Note: This research is generated for educational purposes. Always verify "
            "case law and statutes in your jurisdiction before relying on them in practice."
        )
        return {
            "relevant_principles": data["principles"],
            "suggested_arguments": data["arguments"],
            "related_areas": data["related"],
            "research_notes": notes,
        }

    # Live OpenAI path
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)

        prompt = (
            f"Research the following legal question: '{query}'\n"
            f"Jurisdiction: {jurisdiction}\n"
            f"Case type: {case_type}\n\n"
            "Provide: relevant legal principles, suggested arguments, related practice areas, "
            "and research notes."
        )

        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are an expert legal researcher."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1200,
            temperature=0.3,
        )

        content = response.choices[0].message.content
        return {
            "relevant_principles": [content[:600]],
            "suggested_arguments": [],
            "related_areas": [],
            "research_notes": "Generated by OpenAI. Verify before use in practice.",
        }
    except Exception as exc:
        return {
            "relevant_principles": [],
            "suggested_arguments": [],
            "related_areas": [],
            "research_notes": f"Research failed: {exc}",
        }
