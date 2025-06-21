# voice_input.py

import speech_recognition as sr

def recognize_voice(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "❌ Could not understand the audio."
    except sr.RequestError:
        return "⚠️ Error connecting to the speech recognition service."
