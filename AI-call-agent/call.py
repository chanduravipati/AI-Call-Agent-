import os
import re
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()


def main():
    phone = input("Enter phone number to call: ").strip()
    if not re.fullmatch(r"\+[1-9]\d{7,14}", phone):
        print("Invalid phone number. Use international format, for example +91XXXXXXXXXX.")
        return
    required = ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM_NUMBER", "VOICE_WEBHOOK_URL")
    missing = [key for key in required if not os.getenv(key) or os.getenv(key).startswith("YOUR_")]
    if missing:
        print("Missing configuration: " + ", ".join(missing))
        return
    try:
        client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
        call = client.calls.create(
            to=phone,
            from_=os.environ["TWILIO_FROM_NUMBER"],
            url=os.environ["VOICE_WEBHOOK_URL"],
            method="POST",
        )
        print(f"Entered phone number: {phone}")
        print(f"Call status: {call.status}")
        print(f"Call SID: {call.sid}")
    except Exception as error:
        print(f"Twilio call failed: {error}")


if __name__ == "__main__":
    main()
