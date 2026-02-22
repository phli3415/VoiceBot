# Pretty Good AI - Engineering Challenge: Voice Bot

This project is a Python-based automated voice bot designed to test an AI agent over a phone line. The bot acts as a "patient," simulating realistic scenarios to evaluate the AI's performance, identify bugs, and stress-test its capabilities.

## Core Technologies

- **AI Agent Framework**: LangChain (v0.3.25)
- **Language Model**: ChatGPT (via OpenAI API)
- **Telephony**: Twilio API
- **Speech-to-Text (STT)**: OpenAI Whisper
- **Text-to-Speech (TTS)**: gTTS or ElevenLabs

## How to Set Up

### 1. Prerequisites

- Python 3.8+
- A paid Twilio account with a provisioned phone number.
- An OpenAI API key.
- An ElevenLabs API key.
- [Conda](https://docs.conda.io/en/latest/miniconda.html) installed on your system.
- [ngrok](https://ngrok.com/download) for exposing the local server to the internet.

### Installation

1.  **Clone the repository:**
    Run following command in an IDE terminal:
    ```bash
    git clone https://github.com/phli3415/VoiceBot.git
    cd VoiceBot
    ```

2.  **Create and Activate the Conda Environment:**
    The `environment.yml` file (located in this `app` directory) contains all the necessary Python dependencies. 

    **Note:** For Windows users, it is recommended to run the following commands in the **"Anaconda Prompt"** or **"Miniconda Prompt"**. For macOS/Linux users, a standard terminal is sufficient.

    First, create the environment from the file:
    ```bash
    conda env create -f environment.yml
    ```
    
    This will create a new environment named `voicebot-challenge`. Activate it using:
    ```bash
    conda activate voicebot-challenge
    ```

3.  **Configure Environment Variables:**
    Create a file named `.env` in the current `VoiceBot` directory. This file will store your secret keys and configuration details. Fill in the following information.

    ```
    # app/.env

    OPENAI_API_KEY="sk-..."

    ELEVEN_API_KEY="..."

    TWILIO_ACCOUNT_SID="AC..."
    TWILIO_AUTH_TOKEN="..."
    TWILIO_PHONE_NUMBER="+1..."



## 3. Running the Test Sequence

### 1. Start Ngrok

The application runs a local web server on port 8000 to receive instructions (webhooks) from Twilio. You need to use `ngrok` to create a secure, public URL that points to this local server.

Open a new IDE terminal  and run:
```bash
ngrok http 8000
```
Ngrok will display a public "Forwarding" URL (e.g., `https://<unique-id>.ngrok-free.dev`). **Copy this HTTPS URL.**

### 2. Update the Ngrok URL in the Code

Open the `app/main.py` file and paste your ngrok HTTPS URL into the `ngrok_url` variable (around line 30):

```python
# main.py
...
scenarios = json.load(open('scenarios.json'))
ngrok_url = "https://<your-unique-id>.ngrok-free.dev" # <--- PASTE YOUR NGROK URL HERE
...
```
**Note:** The application logic requires this URL to be hardcoded for now. Remember to update it every time you restart ngrok.

### 3. Run the Application

Make sure your `voicebot-challenge` Conda environment is still active and you are in the `app` directory. Then, run the main script:

```bash
python main.py
```

The server will start, and after a few seconds, the automated call sequence will begin. Your verified phone number will receive the first of 10 consecutive calls.

## 4. How It Works

1.  **Initiation**: The `main.py` script starts a FastAPI server and kicks off the test sequence by calling `initiate_next_call_in_sequence()`.
2.  **Making the Call**: The script uses the Twilio API to call your phone number. It tells Twilio to fetch instructions from the public ngrok URL.
3.  **First Turn**: When you answer, Twilio fetches TwiML instructions. The server generates the patient bot's first line, converts it to speech using ElevenLabs, and serves the audio file for Twilio to play.
4.  **Conversation Loop**:
    - The server instructs Twilio to record your response.
    - The recording is sent back to the `/twilio_webhook`.
    - The audio is transcribed using OpenAI Whisper.
    - The transcribed text is fed to the LangChain "patient bot".
    - The bot generates a reply, which is converted to speech and played back.
5.  **Call Completion & Analysis**: When a call ends, Twilio sends a final notification to the `/status_callback` endpoint.
    - The full conversation transcript is saved.
    - A separate "analyzer" AI agent reads the transcript and the original test scenario.
    - It generates a detailed QA report, which is appended to `reports/bug_report.md`.
6.  **Chain Reaction**: After the analysis is complete, `initiate_next_call_in_sequence()` is called again, automatically starting the test for the next scenario. This continues until all 10 scenarios are completed.

## 5. Output

All test results are saved in the `reports` directory:

-   `reports/bug_report.md`: The final, comprehensive report containing the analysis for all 10 test scenarios.
-   `reports/call_transcripts/`: This folder contains the raw text transcript for each individual call, saved as a `.txt` file.
