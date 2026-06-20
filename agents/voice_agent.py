from gtts import gTTS
import io
import re

def clean_text_for_speech(text):
    # Remove code blocks entirely (anything between triple backticks)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove any leftover single backticks
    text = text.replace('`', '')
    # Remove markdown bold/italic symbols
    text = text.replace('*', '').replace('_', '')
    # Clean up extra blank lines left behind
    text = re.sub(r'\n\s*\n', '\n', text).strip()
    return text

def text_to_speech(text):
    clean_text = clean_text_for_speech(text)
    
    if not clean_text.strip():
        clean_text = "Please check the code snippet shown on screen."
    
    tts = gTTS(text=clean_text, lang='en', slow=False)
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes