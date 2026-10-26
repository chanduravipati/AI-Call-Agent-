import re
from datetime import datetime


class CourseBookingManager:
    DAYS = {"monday": "Monday", "tuesday": "Tuesday", "wednesday": "Wednesday", "thursday": "Thursday", "friday": "Friday"}
    TIMES = {
        "10:00 AM": ("10:00 AM", ("10 am", "10 a.m", "10 in the morning", "morning")),
        "2:00 PM": ("2:00 PM", ("2 pm", "2 p.m", "2 in the afternoon", "afternoon")),
        "4:00 PM": ("4:00 PM", ("4 pm", "4 p.m", "4 in the evening", "evening")),
    }

    def identify_course(self, text):
        value = text.lower()
        if re.search(r"\b(java|java full stack)\b", value):
            return "Java Full Stack"
        if re.search(r"\b(python|python full stack)\b", value):
            return "Python Full Stack"
        return None

    def identify_day(self, text):
        value = text.lower()
        for key, day in self.DAYS.items():
            if key in value:
                return day
        return None

    def identify_time(self, text):
        value = text.lower().replace(".", "")
        for time, (_, aliases) in self.TIMES.items():
            if any(alias.replace(".", "") in value for alias in aliases):
                return time
        if re.search(r"\b10\b", value):
            return "10:00 AM"
        if re.search(r"\b2\b", value):
            return "2:00 PM"
        if re.search(r"\b4\b", value):
            return "4:00 PM"
        return None

    def course_confirmation(self, course):
        return f"{course} course duration {course and {'Python Full Stack': '8 weeks', 'Java Full Stack': '10 weeks'}.get(course, 'the scheduled duration')}, fee is {'12,000 INR' if course == 'Python Full Stack' else '14,000 INR'}"

    def demo_booking_message(self, day, time):
        return f"Free demo class {day} at {time}"

    def booking_confirmation(self, name, course, day, time, phone):
        return f"{name}, your {course} free demo is confirmed for {day} at {time}. We will use {phone}."

    def closing_message(self):
        return "Thank you for your time. We look forward to seeing you in the demo class. Have a great day!"

    def booking_date(self):
        return datetime.now().strftime("%Y-%m-%d")
