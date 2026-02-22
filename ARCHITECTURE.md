# System Architecture

This project's architecture is designed as a modular, event-driven QA automation system for a voice AI. It is orchestrated by a central web server that responds to real-time events from a telephony provider (Twilio). The core logic is split between a conversational AI "patient bot" powered by LangChain and GPT-4o-mini, and a speech processing module that handles voice generation (ElevenLabs) and transcription (OpenAI Whisper).

The testing workflow is fully automated: the system initiates a phone call and then enters a webhook-driven loop. In each turn, it plays the patient bot's audio, records the AI assistant's response, transcribes it, and generates a new reply. Upon call completion, a separate AI agent analyzes the full transcript against predefined criteria to generate a quality report. The system then automatically triggers the next test in the sequence, creating a continuous, end-to-end evaluation process without manual intervention.
