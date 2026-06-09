"""
appointment_tool.py — Appointment scheduling tools for the agentic workflow.

Provides:
  - check_available_slots(department, date)
  - book_appointment(department, date, slot, patient_name)
"""

from app.logger import logger


# Mock appointment data per department
SLOTS_BY_DEPARTMENT = {
    "cardiology":  ["Monday 10:00 AM", "Wednesday 2:00 PM", "Friday 9:00 AM"],
    "dermatology": ["Tuesday 11:00 AM", "Thursday 3:00 PM", "Friday 11:00 AM"],
    "neurology":   ["Monday 2:00 PM", "Wednesday 9:00 AM", "Thursday 10:30 AM"],
    "pediatrics":  ["Tuesday 9:00 AM", "Wednesday 1:00 PM", "Friday 2:00 PM"],
    "general":     [
        "Monday 10:00 AM", "Monday 2:00 PM",
        "Tuesday 11:00 AM", "Tuesday 3:00 PM",
        "Wednesday 9:00 AM", "Wednesday 1:00 PM",
        "Thursday 10:30 AM", "Thursday 2:30 PM",
        "Friday 9:00 AM", "Friday 11:00 AM",
    ],
}

# In-memory booking store (mock database)
BOOKINGS: list[dict] = []


def check_available_slots(department: str = "general", date: str = None) -> dict:
    """
    Mock tool: returns available appointment slots for a given department.
    """
    dept_key = department.lower()
    slots = SLOTS_BY_DEPARTMENT.get(dept_key, SLOTS_BY_DEPARTMENT["general"])

    # Filter by date if specified
    if date:
        slots = [s for s in slots if date.lower() in s.lower()]
        if not slots:
            slots = [f"No slots available on {date.capitalize()}"]

    logger.info(f"[TOOL] check_available_slots — department={department}, date={date}")
    return {
        "department": department.capitalize(),
        "date_requested": date or "Any available",
        "available_slots": slots,
        "message": f"Available slots for {department.capitalize()} department."
    }


def book_appointment(department: str, date: str, slot: str, patient_name: str) -> dict:
    """
    Mock tool: books an appointment slot and returns confirmation.
    BRD requirement: book_appointment(slot: str) -> AppointmentBooking
    """
    dept_key = department.lower()
    available = SLOTS_BY_DEPARTMENT.get(dept_key, SLOTS_BY_DEPARTMENT["general"])

    # Validate slot exists
    if slot not in available:
        logger.warning(f"[TOOL] book_appointment failed — slot '{slot}' not available")
        return {
            "status": "failed",
            "message": f"Slot '{slot}' is not available for {department.capitalize()}.",
            "available_slots": available
        }

    # Check if slot already booked
    for booking in BOOKINGS:
        if (booking["department"].lower() == dept_key
                and booking["slot"] == slot
                and booking["date"].lower() == date.lower()):
            logger.warning(f"[TOOL] book_appointment failed — slot already booked")
            return {
                "status": "failed",
                "message": f"Slot '{slot}' on {date} is already booked.",
                "suggestion": "Please choose a different slot."
            }

    # Create booking
    booking = {
        "department": department.capitalize(),
        "date": date.capitalize(),
        "slot": slot,
        "patient_name": patient_name,
        "status": "confirmed"
    }
    BOOKINGS.append(booking)

    logger.info(f"[TOOL] book_appointment confirmed — {department} {date} {slot} for {patient_name}")
    return {
        "status": "confirmed",
        "message": f"Appointment booked successfully!",
        "booking": booking
    }


def get_bookings(patient_name: str = None) -> list:
    """Retrieve bookings, optionally filtered by patient name."""
    if patient_name:
        return [b for b in BOOKINGS if b["patient_name"].lower() == patient_name.lower()]
    return BOOKINGS
