import os
import re
from knowledge_base import COURSE_INFO, FAQS

try:
    from google import genai
except ImportError:
    genai = None


class QuestionAnswerer:
    def __init__(self):
        self.client = None
        api_key = os.getenv("GEMINI_API_KEY")
        if genai and api_key and not api_key.startswith("YOUR_"):
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception:
                self.client = None

    def answer(self, question, selected_course=None):
        normalized = re.sub(r"[^a-z0-9 ]", "", question.lower()).strip()
        direct_answers = {
            "who are you": "I am Ajay, an AI sales assistant for the Full Stack courses.",
            "what can you do": "I can explain the available courses, answer common questions, and help schedule a free demo class.",
            "what is ai": "AI is software that performs tasks which usually need human intelligence, such as understanding language.",
            "what is gemini": "Gemini is Google's generative AI model family, used here to help answer questions naturally.",
            "what is an llm": "An LLM is a large language model trained to understand and generate language.",
            "how does ai work": "AI learns patterns from data and uses those patterns to produce a useful response to an input.",
        }
        for question_key, answer in direct_answers.items():
            if question_key in normalized:
                return answer
        for faq_question, answer in FAQS.items():
            if faq_question in normalized or normalized in faq_question:
                return answer
        if any(word in normalized for word in ("fee", "fees", "cost", "price")):
            return FAQS["how much does the course cost"]
        if "course detail" in normalized or "course details" in normalized:
            return self._course_details(selected_course)
        if self.client:
            try:
                context = f"Course information: {COURSE_INFO}\nFAQ information: {FAQS}"
                prompt = ("You are a concise AI sales assistant for these courses. Answer only from the supplied "
                          "information. Never invent fees, dates, guarantees, or business claims. Use a natural "
                          "Telugu-English mix where appropriate. Keep the response under 45 words for a phone call.\n"
                          f"{context}\nQuestion: {question}")
                response = self.client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                if response.text:
                    return response.text.strip()
            except Exception:
                pass
        return "I don't have that specific information right now. I can connect you with a human representative for clarification."

    def _course_details(self, course):
        if course not in ("Python Full Stack", "Java Full Stack"):
            return FAQS["how much does the course cost"]
        info = COURSE_INFO[course]
        topics = ", ".join(info["topics"][:4])
        return f"{course} runs for {info['duration']} and costs {info['fee']}. Topics include {topics}, and practical projects are included."
