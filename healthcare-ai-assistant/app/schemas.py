from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class Message(BaseModel):
    role: str
    content: str


class AskRequest(BaseModel):
    question: str
    history: Optional[List[Message]] = []


class SourceChunk(BaseModel):
    document: str
    chunk: str


class AskResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    confidence: str
    routed_to: str  # "rag" or "appointment"


class AppointmentBooking(BaseModel):
    department: str
    date: str
    slot: str
    patient_name: str
    status: str  # "confirmed" or "pending"


class AppointmentRequest(BaseModel):
    department: str
    date: str
    slot: str
    patient_name: str


class HealthResponse(BaseModel):
    status: str
    version: str
    documents_ingested: bool


class IngestResponse(BaseModel):
    message: str
    chunks: int
