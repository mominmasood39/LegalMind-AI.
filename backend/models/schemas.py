"""Pydantic schemas for request and response models."""

from pydantic import BaseModel, Field
from typing import Optional


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class LegalQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="Legal question or query")
    history: list[ChatMessage] = Field(default_factory=list, description="Conversation history")
    jurisdiction: Optional[str] = Field(default="general", description="Legal jurisdiction context")


class LegalQueryResponse(BaseModel):
    answer: str
    disclaimer: str
    sources: list[str] = Field(default_factory=list)


class DocumentAnalysisRequest(BaseModel):
    document_text: str = Field(..., min_length=1, max_length=50000)
    analysis_type: str = Field(default="general", description="Type: general, contract, clause")


class DocumentAnalysisResponse(BaseModel):
    summary: str
    key_points: list[str]
    risk_factors: list[str]
    recommendations: list[str]


class CaseResearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    jurisdiction: Optional[str] = Field(default="general")
    case_type: Optional[str] = Field(default="all")


class CaseResearchResponse(BaseModel):
    relevant_principles: list[str]
    suggested_arguments: list[str]
    related_areas: list[str]
    research_notes: str


class HealthResponse(BaseModel):
    status: str
    version: str
    demo_mode: bool
