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
    ```bash
    git clone https://github.com/phli3415/VoiceBot.git
    cd <your-repository-name>
    ```

2.  **Create the Conda Environment:**
    This project uses a specific set of Python libraries. Use the provided `environment.yml` file to create a dedicated Conda environment with all the necessary dependencies.

    ```bash
    conda env create -f doc/Environment/environment.yml
    ```
    This will create a new environment named `prettygoodai`.

3.  **Activate the Conda Environment:**
    Before running the application, you must activate the newly created environment.
    ```bash
    conda activate prettygoodai
    ```

4.  **Configure Environment Variables:**
    Create a file named `.env` in the `app` directory. This file will store your secret keys and configuration details. You can copy `.env.example` to get started.

    ```
    # app/.env

    # OpenAI API Key
    OPENAI_API_KEY="sk-..."

    # ElevenLabs API Key
    ELEVEN_API_KEY="..."

    # Twilio Credentials
    TWILIO_ACCOUNT_SID="AC..."
    TWILIO_AUTH_TOKEN="..."
    TWILIO_PHONE_NUMBER="+1..." # Your Twilio phone number

    # Your personal phone number, verified with Twilio
    YOUR_VERIFIED_PHONE_NUMBER="+1..."
    ```
