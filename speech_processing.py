import os
from openai import OpenAI
from gtts import gTTS
from elevenlabs.client import ElevenLabs
from elevenlabs import save

openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

eleven_client = ElevenLabs()
has_elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY") is not None

def transcribe_audio(audio_file_path: str) -> str:

    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return ""


def text_to_speech(text: str, output_path: str = "response.mp3", use_elevenlabs: bool = True) -> str:

    try:
        if use_elevenlabs and has_elevenlabs_key:
            audio = eleven_client.generate(
                text=text,
                voice="Bella",
                model="eleven_monolingual_v1"
            )
            save(audio, output_path)
        else:
            tts = gTTS(text=text, lang='en')
            tts.save(output_path)
        return output_path
    except Exception as e:
        print(f"Error during text-to-speech conversion: {e}")
        return None
