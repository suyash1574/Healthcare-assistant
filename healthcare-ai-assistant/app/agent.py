"""
agent.py — Agentic workflow with intent-based routing.

Routes questions to:
  - appointment_tool  →  booking/scheduling intent
  - RAG pipeline      →  knowledge/information intent
"""

from app.appointment_tool import check_available_slots, book_appointment
from app.logger import logger

# ── Intent detection patterns ────────────────────────────────────────────────

# Strong booking signals — user wants to take action
BOOKING_INTENTS = [
    "book an appointment", "schedule an appointment", "book a visit",
    "schedule a visit", "make an appointment", "set up an appointment",
    "reserve a slot", "book a slot",
    "can i book", "can i schedule", "how do i book", "how do i schedule",
    "cancel my appointment", "cancel appointment", "reschedule",
    "schedule with", "book with",
    "i want to see", "i need to see", "i want to visit", "i need to visit",
    "i want an appointment", "i need an appointment",
    "can i see", "i'd like to see", "i would like to see",
    "i want", "i need",
    "schedule", "book",
]

# Availability check signals — user wants to see options
AVAILABILITY_INTENTS = [
    "available slots", "what slots", "when is the next",
    "show me available", "what times", "openings",
    "availability", "free slots",
]

# Knowledge patterns — questions about appointment process (NOT booking)
KNOWLEDGE_KEYWORDS = [
    "what documents", "what do i need", "how do i prepare",
    "before my appointment", "bring to appointment", "required documents",
    "what to bring", "how long does", "what happens during",
    "preparation", "arrival time", "check-in",
]

# Cancel/reschedule intents (no department needed)
ACTION_INTENTS = [
    "cancel my appointment", "cancel appointment", "reschedule",
]

# Departments (including specialist names)
DEPARTMENTS = [
    "cardiology", "dermatology", "neurology", "pediatrics",
    "orthopedics", "orthopedic", "ortho", "oncology",
    "gastroenterology", "ophthalmology", "ent",
    "obstetrics", "gynecology", "urology",
]

# Department aliases (body parts, specialist names, common terms)
DEPARTMENT_ALIASES = {
    # Specialist names
    "cardiologist": "cardiology",
    "dermatologist": "dermatology",
    "neurologist": "neurology",
    "pediatrician": "pediatrics",
    "orthopedist": "orthopedics",
    "oncologist": "oncology",
    "gastroenterologist": "gastroenterology",
    "ophthalmologist": "ophthalmology",
    "gynecologist": "gynecology",
    "urologist": "urology",
    # Common terms
    "ortho": "orthopedics",
    "orthopaedic": "orthopedics",
    "heart": "cardiology",
    "skin": "dermatology",
    "brain": "neurology",
    "kids": "pediatrics",
    "child": "pediatrics",
    "children": "pediatrics",
    "baby": "pediatrics",
    "cancer": "oncology",
    "tumor": "oncology",
    "stomach": "gastroenterology",
    "gut": "gastroenterology",
    "eye": "ophthalmology",
    "ear nose throat": "ent",
    "pregnancy": "obstetrics",
    "women": "gynecology",
    "bladder": "urology",
    "kidney": "urology",
    "bone": "orthopedics",
    "joint": "orthopedics",
    "spine": "orthopedics",
}


def _detect_department(question: str) -> str:
    q = question.lower()

    # Check aliases first (more specific — includes specialist names)
    for alias, dept in DEPARTMENT_ALIASES.items():
        if alias in q:
            return dept

    # Check full department names
    for dept in DEPARTMENTS:
        if dept in q:
            return dept

    return "general"


def _detect_date(question: str) -> str | None:
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for day in days:
        if day in question.lower():
            return day.capitalize()
    return None


def _is_knowledge_question(question: str) -> bool:
    """Check if the user is asking for information about appointments, not booking."""
    q_lower = question.lower()
    return any(pattern in q_lower for pattern in KNOWLEDGE_KEYWORDS)


def _is_action_intent(question: str) -> bool:
    """Check if the user wants to cancel or reschedule."""
    q_lower = question.lower()
    return any(intent in q_lower for intent in ACTION_INTENTS)


def route_question(question: str) -> dict:
    """
    Agentic router: uses intent detection, not just keyword matching.
    """
    q_lower = question.lower()

    # Step 1: Knowledge questions about appointments → RAG
    if _is_knowledge_question(question):
        logger.info("Routed to RAG — knowledge question about appointments")
        return {"type": "rag", "data": {"question": question}}

    # Step 2: Cancel/reschedule → appointment tool (no department needed)
    if _is_action_intent(question):
        tool_result = check_available_slots(department="general")
        logger.info("Routed to appointment tool (cancel/reschedule intent)")
        return {"type": "appointment", "data": tool_result}

    # Step 3: Check for booking intents
    if any(intent in q_lower for intent in BOOKING_INTENTS):
        department = _detect_department(question)
        date = _detect_date(question)
        tool_result = check_available_slots(department=department, date=date)
        logger.info(f"Routed to appointment tool (booking intent) — department={department}")
        return {"type": "appointment", "data": tool_result}

    # Step 4: Check for availability intents
    if any(intent in q_lower for intent in AVAILABILITY_INTENTS):
        department = _detect_department(question)
        date = _detect_date(question)
        tool_result = check_available_slots(department=department, date=date)
        logger.info(f"Routed to appointment tool (availability intent) — department={department}")
        return {"type": "appointment", "data": tool_result}

    # Step 5: Default → RAG pipeline
    logger.info("Routed to RAG pipeline")
    return {"type": "rag", "data": {"question": question}}
