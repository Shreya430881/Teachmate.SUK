import gradio as gr
import speech_recognition as sr
import openai
import os
from PIL import Image
import requests
from io import BytesIO


openai.api_key = "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"

# Transcription using Google Speech API
def transcribe_with_google(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f"[Speech API error: {e}]"


def ask_chatgpt(prompt, temperature=0.7):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response['choices'][0]['message']['content'].strip()

# Image generation using DALL·E
def generate_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    img_data = requests.get(image_url).content
    return Image.open(BytesIO(img_data))

# TeachMate main function
def teachmate_pipeline(audio_path):
    try:
        if not os.path.exists(audio_path):
            return "⚠ Error", "Audio file not found", None

        print("🔊 Transcribing...")
        input_text = transcribe_with_google(audio_path)
        print("Transcribed Text:", input_text)

        if not input_text or input_text.startswith("[Speech API error"):
            return "⚠ Transcription Error", input_text or "No text detected.", None

        print("📝 Summarizing with ChatGPT...")
        summary_prompt = f"Summarize the following content in 3-5 sentences:\n\n{input_text}"
        summary = ask_chatgpt(summary_prompt)

        print("❓ Generating Quiz...")
        quiz_prompt = f"Create 3 multiple choice questions from this summary:\n\n{summary}"
        quiz = ask_chatgpt(quiz_prompt)

        print("🖼 Generating related image...")
        image = generate_image(summary)

        return summary, quiz, image

    except Exception as e:
        import traceback
        traceback.print_exc()
        return "⚠ Error occurred", str(e), None

# Gradio interface
interface = gr.Interface(
    fn=teachmate_pipeline,
    inputs=gr.Audio(type="filepath", label="🎤 Record or Upload Your Voice"),
    outputs=[
        gr.Textbox(label="📄 Summary"),
        gr.Textbox(label="❓ MCQ Quiz"),
        gr.Image(label="🖼 AI-generated Topic Image")
    ],
    title="TeachMate: AI-Powered Learning Assistant",
    description="🎓 Upload or record your voice on a topic. Get an instant summary, quiz, and image with ChatGPT + DALL·E.",
)

interface.launch()
