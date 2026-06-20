from gtts import gTTS
import io

def text_to_speech(text):
  tts = gTTS(text=text, lang='en', slow=False)
  audio_bytes = io.BytesIO()
  tts.write_to_fp(audio_bytes)
  return audio_bytes