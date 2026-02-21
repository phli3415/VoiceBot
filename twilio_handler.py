import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Play, Record

account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_phone_number = os.environ.get("TWILIO_PHONE_NUMBER")

client = Client(account_sid, auth_token)

def make_call(to_number: str, ngrok_base_url: str, scenario_id: str) -> str:

    try:
        call = client.calls.create(
            to=to_number,
            from_=twilio_phone_number,
            url=f"{ngrok_base_url}/twilio_webhook?scenario_id={scenario_id}",
            record=True, # Record the entire call
            status_callback=f"{ngrok_base_url}/status_callback",
            status_callback_event=['completed']
        )
        print(f"Call initiated with SID: {call.sid}")
        return call.sid
    except Exception as e:
        print(f"Error making call: {e}")
        return None
