import os
import re
from threading import Lock

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from twilio.twiml.voice_response import Gather, VoiceResponse
from twilio.rest import Client

from booking_system import create_booking
from sales_intelligence import SalesIntelligence

load_dotenv()
app = Flask(__name__)
agent = SalesIntelligence()
conversation_states = {}
states_lock = Lock()


def new_state(phone=""):
    return {
        "stage": "interest",
        "turn_count": 0,
        "selected_course": None,
        "selected_demo_day": None,
        "selected_demo_time": None,
        "student_name": None,
        "student_phone": phone,
        "conversation_history": [],
        "demo_offered": False,
    }


def gather_response(message, call_sid):
    response = VoiceResponse()
    gather = Gather(input="speech", action="/process", method="POST", language="en-IN", speech_timeout="auto", timeout=5)
    gather.say(message, language="en-IN", voice="Polly.Aditi")
    response.append(gather)
    response.say("I did not hear a response. Thank you for your time.", language="en-IN", voice="Polly.Aditi")
    return response


def valid_phone(phone):
    return bool(re.fullmatch(r"\+[1-9]\d{7,14}", phone or ""))


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "AI Call Sales Agent"})


@app.get("/")
def dashboard():
    return render_template("index.html")


@app.post("/trigger_call")
def trigger_call():
    payload = request.get_json(silent=True) if request.is_json else request.form
    phone = (payload.get("phone", "") if payload else "").strip()
    if not valid_phone(phone):
        return jsonify({"error": "Enter a valid international phone number, such as +91XXXXXXXXXX."}), 400
    required = ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM_NUMBER", "VOICE_WEBHOOK_URL")
    missing = [key for key in required if not os.getenv(key) or os.getenv(key).startswith("YOUR_")]
    if missing:
        return jsonify({"error": "Missing Twilio configuration: " + ", ".join(missing)}), 503
    try:
        client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
        call = client.calls.create(to=phone, from_=os.environ["TWILIO_FROM_NUMBER"], url=os.environ["VOICE_WEBHOOK_URL"], method="POST")
        return jsonify({"message": "Call initiated.", "call_sid": call.sid, "status": call.status})
    except Exception as error:
        return jsonify({"error": f"Twilio could not place the call: {error}"}), 502


@app.post("/voice")
def voice():
    call_sid = request.form.get("CallSid", "unknown")
    phone = request.form.get("To", "")
    with states_lock:
        conversation_states[call_sid] = new_state(phone)
    return str(gather_response(agent.initial_greeting(), call_sid))


@app.post("/process")
def process():
    call_sid = request.form.get("CallSid", "unknown")
    speech = request.form.get("SpeechResult", "")
    phone = request.form.get("To", "")
    with states_lock:
        state = conversation_states.setdefault(call_sid, new_state(phone))
        if phone:
            state["student_phone"] = phone
        state["conversation_history"].append({"role": "caller", "text": speech})
        message, end_call = agent.respond(state, speech)
        if state.get("stage") == "booked":
            create_booking(state["student_name"], state["student_phone"], state["selected_course"], state["selected_demo_day"], state["selected_demo_time"])
            state["stage"] = "closed"
            message += " " + agent.booking.closing_message()
            end_call = True
        state["conversation_history"].append({"role": "agent", "text": message})
    response = VoiceResponse()
    if end_call:
        response.say(message, language="en-IN", voice="Polly.Aditi")
        response.hangup()
    else:
        gather = Gather(input="speech", action="/process", method="POST", language="en-IN", speech_timeout="auto", timeout=5)
        gather.say(message, language="en-IN", voice="Polly.Aditi")
        response.append(gather)
        response.say("I did not hear you. We can continue another time. Thank you.", language="en-IN", voice="Polly.Aditi")
    return str(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
