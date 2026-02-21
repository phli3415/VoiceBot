import os
import json
import uvicorn
import requests
from fastapi import FastAPI, Form, Request, Response
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from twilio.twiml.voice_response import VoiceResponse
from threading import Timer

import agent
import twilio_handler
import speech_processing

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

global_state = {
    "current_scenario": None,
    "conversation_agent": None,
    "conversation_history": ""
}

def download_file_from_url(url: str, local_filename: str):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

@app.post("/twilio_webhook")
async def handle_twilio_webhook(request: Request, scenario_id: str = None, RecordingUrl: str = Form(None)):

    if scenario_id and not RecordingUrl:
        print(f"Starting conversation for scenario: {scenario_id}")
        scenarios = json.load(open('scenarios.json'))
        global_state["current_scenario"] = next((s for s in scenarios if s['scenario_id'] == scenario_id), None)
        
        global_state["conversation_agent"] = agent.create_patient_agent(global_state["current_scenario"])
        
        initial_response = global_state["current_scenario"]['initial_prompt']
        global_state["conversation_history"] += f"Patient: {initial_response}\n"
        
        audio_path = speech_processing.text_to_speech(initial_response, "static/initial.mp3")
        base_url = str(request.base_url)
        audio_url = f"{base_url}{audio_path}"
        twiml = twilio_handler.create_twiml_response(audio_url=audio_url)
        return Response(content=twiml, media_type="application/xml")

    elif RecordingUrl:
        print(f"Received a recording: {RecordingUrl}")
        
        audio_path = "static/agent_response.wav"
        download_file_from_url(RecordingUrl, audio_path)
        
        transcribed_text = speech_processing.transcribe_audio(audio_path)
        global_state["conversation_history"] += f"AI Assistant: {transcribed_text}\n"
        print(f"AI Assistant said: {transcribed_text}")

        patient_response = global_state["conversation_agent"].predict(input=transcribed_text)
        global_state["conversation_history"] += f"Patient: {patient_response}\n"
        print(f"Patient bot will say: {patient_response}")
        
        response_audio_path = speech_processing.text_to_speech(patient_response, "static/response.mp3")
        base_url = str(request.base_url)
        audio_url = f"{base_url}{response_audio_path}"
        twiml = twilio_handler.create_twiml_response(audio_url=audio_url)
        return Response(content=twiml, media_type="application/xml")

    response = VoiceResponse()
    response.hangup()
    return Response(content=str(response), media_type="application/xml")


@app.post("/status_callback")
async def handle_status_callback(CallSid: str = Form(...), CallStatus: str = Form(...)):

    if CallStatus == 'completed':
        print(f"Call {CallSid} completed. Analyzing conversation.")
        scenario = global_state["current_scenario"]
        history = global_state["conversation_history"]
        
        if not history:
            print("No conversation was recorded. Skipping analysis.")
            return Response(status_code=200)

        transcript_path = f"reports/call_transcripts/call_{scenario['scenario_id']}.txt"
        os.makedirs(os.path.dirname(transcript_path), exist_ok=True)
        with open(transcript_path, "w") as f:
            f.write(history)
            
        analysis = agent.analyze_conversation(history, scenario)
        bug_report_path = "reports/bug_report.md"
        with open(bug_report_path, "a") as f:
            f.write(f"\n---\n### Analysis for Scenario: {scenario['scenario_id']}\n\n")
            f.write(analysis)
            f.write("\n")
        print("Analysis complete and report updated.")
    return Response(status_code=200)


def main():

    os.makedirs("reports/call_transcripts", exist_ok=True)
    os.makedirs("static", exist_ok=True) # Ensure static dir exists
    
    with open("reports/bug_report.md", "w") as f:
        f.write("# AI Agent Bug and Quality Report\n")

    print("Starting FastAPI server. Use ngrok to expose this port to the internet.")
    print("Example ngrok command: ngrok http 8000")
    
    def run_call():
        print("Getting ready to make the first call...")
        ngrok_url = "https://<your-ngrok-subdomain>.ngrok.io"  # <--- IMPORTANT: Update this
        scenarios = json.load(open('scenarios.json'))
        first_scenario = scenarios[0]
        twilio_handler.make_call(
            to_number="805-439-8008", # The number to test
            ngrok_base_url=ngrok_url, 
            scenario_id=first_scenario['scenario_id']
        )
    Timer(2, run_call).start()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
