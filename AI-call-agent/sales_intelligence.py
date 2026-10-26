import re
from course_booking import CourseBookingManager
from question_answerer import QuestionAnswerer


class SalesIntelligence:
    STOP_PHRASES = ("stop calling", "don't call me", "do not call me", "remove my number")
    NO_PHRASES = ("not interested", "no thanks", "not now", "don't want")

    def __init__(self):
        self.booking = CourseBookingManager()
        self.answerer = QuestionAnswerer()

    def initial_greeting(self):
        return "Hello బ్రో! Nenu Ajay. Full Stack programming courses gurinchi calling chestunnanu. Interested unnara?"

    def respond(self, state, speech):
        text = speech.strip()
        lower = text.lower()
        if not text:
            return "Sorry, mee voice clear ga vinapadaledu. Please repeat cheyyandi.", False
        if any(phrase in lower for phrase in self.STOP_PHRASES):
            return "Sure, mee request respect chestunnanu. We will not continue this call. Thank you.", True
        if any(phrase in lower for phrase in self.NO_PHRASES) or re.search(r"\b(no|nope)\b", lower):
            return "Okay, mee decision respect chestunnanu. Thank you for your time. Have a good day!", True

        course = self.booking.identify_course(text)
        if course:
            state["selected_course"] = course
            state["stage"] = "day"
            info = self.answerer._course_details(course)
            return f"Nice బ్రో! {info} Free demo class ki preferred day cheppandi, Monday to Friday lo.", False

        if state["stage"] == "day":
            day = self.booking.identify_day(text)
            if day:
                state["selected_demo_day"] = day
                state["stage"] = "time"
                return "Great, preferred time 10 AM, 2 PM, or 4 PM lo cheppandi.", False
            return "Monday to Friday lo meeku convenient day cheppandi.", False

        if state["stage"] == "time":
            time = self.booking.identify_time(text)
            if time:
                state["selected_demo_time"] = time
                state["stage"] = "name"
                return "Perfect. Student name cheppandi please.", False
            return "Available times 10 AM, 2 PM, and 4 PM. Which one works for you?", False

        if state["stage"] == "name":
            state["student_name"] = text[:80]
            state["stage"] = "confirm"
            state["demo_offered"] = True
            return self._confirm_prompt(state), False

        if state["stage"] == "confirm":
            if re.search(r"\b(yes|confirm|correct|okay|ok)\b", lower):
                state["stage"] = "booked"
                return "Your details are confirmed. Saving your demo booking now.", False
            if "no" in lower or "change" in lower:
                state["stage"] = "day"
                return "No problem. Please tell me your preferred day again.", False
            return self._confirm_prompt(state), False

        if any(word in lower for word in ("interested", "yes", "sure", "tell me", "details")):
            state["stage"] = "course"
            return "Bagundi! Python Full Stack or Java Full Stack, which course are you interested in?", False

        state["turn_count"] += 1
        return self.answerer.answer(text, state.get("selected_course")), False

    def _confirm_prompt(self, state):
        return (f"Please confirm: {state['student_name']}, {state['selected_course']} demo on "
                f"{state['selected_demo_day']} at {state['selected_demo_time']}. Is that correct?")
