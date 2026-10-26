import json
import os
from datetime import datetime
from knowledge_base import COURSE_INFO

BOOKINGS_FILE = os.path.join(os.path.dirname(__file__), "student_bookings.json")


def load_bookings():
    try:
        with open(BOOKINGS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def save_booking(booking):
    bookings = load_bookings()
    bookings.append(booking)
    try:
        with open(BOOKINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(bookings, file, ensure_ascii=False, indent=2)
    except OSError as error:
        raise RuntimeError(f"Could not save booking: {error}") from error
    return booking


def create_booking(student_name, student_phone, course_name, demo_date, demo_time):
    now = datetime.now()
    return save_booking({
        "student_name": student_name,
        "student_phone": student_phone,
        "course_name": course_name,
        "demo_date": demo_date,
        "demo_time": demo_time,
        "booking_date": now.strftime("%Y-%m-%d"),
        "booking_time": now.strftime("%H:%M:%S"),
        "booking_status": "confirmed",
    })


def get_bookings_for_date(demo_date):
    return [booking for booking in load_bookings() if booking.get("demo_date") == demo_date]


def get_student_booking(student_phone):
    matches = [booking for booking in load_bookings() if booking.get("student_phone") == student_phone]
    return matches[-1] if matches else None


def get_course_info(course_name):
    return COURSE_INFO.get(course_name)
