import os
import json
import time
import uvicorn
import requests

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Form, Request, Response
from fastapi.staticfiles import StaticFiles
from twilio.twiml.voice_response import VoiceResponse

import agent
import twilio_handler
import speech_processing

os.makedirs("reports/call_transcripts", exist_ok=True)
os.makedirs("static", exist_ok=True)

with open("reports/bug_report.md", "w") as f:
    f.write("# AI Agent Bug and Quality Report\n")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

scenarios = json.load(open('scenarios.json'))
ngrok_url = "https://nonextended-emogene-diaphragmatically.ngrok-free.dev"

global_state = {
    "current_scenario_index": -1, 
    "current_scenario": None,
    "conversation_agent": None,
    "conversation_history": ""
}


def download_file_from_url(url: str, local_filename: str):
    """Downloads a file from a URL, saving it locally with authentication."""
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

    with requests.get(url, stream=True, auth=(account_sid, auth_token)) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


@app.post("/twilio_webhook")
async def handle_twilio_webhook(request: Request, scenario_id: str = None, RecordingUrl: str = Form(None)):
    response = VoiceResponse()

    if scenario_id and not RecordingUrl:
        print(
            f"\n---\n[SCENARIO {global_state['current_scenario_index'] + 1}/{len(scenarios)}] Starting conversation for scenario: {scenario_id}\n---")
        global_state["current_scenario"] = next((s for s in scenarios if s['scenario_id'] == scenario_id), None)

        global_state["conversation_history"] = ""
        global_state["conversation_agent"] = agent.create_patient_agent(global_state["current_scenario"])

        initial_prompt = global_state["conversation_agent"].memory.chat_memory.messages[0].content
        global_state["conversation_history"] += f"Patient: {initial_prompt}\n"

        audio_path = speech_processing.text_to_speech(initial_prompt, "static/initial.mp3")
        base_url = str(request.base_url)
        audio_url = f"{base_url}{audio_path}"

        response.play(audio_url)
        response.record(action="/twilio_webhook", method="POST", finish_on_key="*")
        response.hangup()

        return Response(content=str(response), media_type="application/xml")

    elif RecordingUrl:
        audio_path = "static/agent_response.wav"
        download_file_from_url(RecordingUrl, audio_path)

        transcribed_text = speech_processing.transcribe_audio(audio_path)
        if transcribed_text:
            global_state["conversation_history"] += f"AI Assistant: {transcribed_text}\n"
            print(f"AI Assistant said: {transcribed_text}")

            patient_response = global_state["conversation_agent"].predict(input=transcribed_text)
            global_state["conversation_history"] += f"Patient: {patient_response}\n"
            print(f"Patient bot will say: {patient_response}")

            response_audio_path = speech_processing.text_to_speech(patient_response, "static/response.mp3")
            base_url = str(request.base_url)
            audio_url = f"{base_url}{response_audio_path}"

            response.play(audio_url)
            response.record(action="/twilio_webhook", method="POST", finish_on_key="*")

    response.hangup()
    return Response(content=str(response), media_type="application/xml")


@app.post("/status_callback")
async def handle_status_callback(CallSid: str = Form(...), CallStatus: str = Form(...)):
    if CallStatus == 'completed':
        print(f"Call {CallSid} completed. Analyzing conversation.")

        scenario = global_state["current_scenario"]
        history = global_state["conversation_history"]

        if history and scenario:
            transcript_path = f"reports/call_transcripts/call_{scenario['scenario_id']}.txt"
            with open(transcript_path, "w") as f:
                f.write(history)

            analysis = agent.analyze_conversation(history, scenario)
            bug_report_path = "reports/bug_report.md"
            with open(bug_report_path, "a") as f:
                f.write(f"\n---\n### Analysis for Scenario: {scenario['scenario_id']}\n\n")
                f.write(analysis)
                f.write("\n")
            print(f"Analysis complete for scenario '{scenario['scenario_id']}'. Report updated.")

        time.sleep(2)  
        initiate_next_call_in_sequence()

    return Response(status_code=200)


def initiate_next_call_in_sequence():
    global_state["current_scenario_index"] += 1
    index = global_state["current_scenario_index"]

    if index < len(scenarios):
        next_scenario = scenarios[index]
        print(
            f"\n>>> Preparing to initiate call for scenario {index + 1}/{len(scenarios)}: '{next_scenario['scenario_id']}'...")

        twilio_handler.make_call(
            to_number="805-439-8008", 
            ngrok_base_url=ngrok_url,
            scenario_id=next_scenario['scenario_id']
        )
    else:
        print("\n=========================================")
        print("All test scenarios have been completed!")
        print("=========================================")


def main():
    print("Starting FastAPI server...")
    print(f"Loaded {len(scenarios)} scenarios to test.")
    print("The test sequence will begin shortly.")

    # Kick off the first call after the server starts
    from threading import Timer
    Timer(3, initiate_next_call_in_sequence).start()

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
