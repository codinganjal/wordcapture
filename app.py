import streamlit as st
import easyocr
from PIL import Image
import numpy as np
from deep_translator import GoogleTranslator
from gtts import gTTS
import base64
import os

# Custom CSS for improved styling
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #eef2f3, #dfe9f3);
        }
        .main-container {
            background-color: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.1);
            max-width: 700px;
            margin: auto;
        }
        .stButton>button {
            background-color: #0056b3;
            color: white;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
            transition: background-color 0.3s, transform 0.1s;
            display: block;
            margin: 10px auto;
            width: auto;
        }
        .stButton>button:hover {
            background-color: #003f7f;
            transform: scale(1.05);
        }
        h1, h2, h3 {
            color: #2c3e50;
            text-align: center;
        }
        .text-box {
            background-color: #f8f9fa;
            border: 2px solid #0056b3;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
            font-size: 16px;
            font-weight: 500;
            color: #333;
            white-space: pre-wrap;
            word-wrap: break-word;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            max-width: 90%;
            margin-left: auto;
            margin-right: auto;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-container'>", unsafe_allow_html=True)

# Title
st.title("📷 Text Extraction & Translation App")

# Language selection for OCR (Input Languages)
lang_options = {
    "English": "en", "Marathi": "mr", "Kannada": "kn", "Hindi": "hi",
    "Korean": "ko", "Japanese": "ja", "Chinese": "ch_sim"
}
selected_langs = st.sidebar.multiselect("Select Input Languages:", list(lang_options.keys()), default=["English"])
lang_list = [lang_options[lang] for lang in selected_langs]

# Target language for translation
target_lang = st.sidebar.selectbox("Choose Translation Language:", list(lang_options.keys()), index=0)
target_lang_code = lang_options[target_lang]

# Load EasyOCR Reader
reader = easyocr.Reader(lang_list,gpu=True)

# Upload image
uploaded_files = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Capture from Camera
show_camera = st.button("📷 Open Camera")
camera_image = None
if show_camera:
    camera_image = st.camera_input("Take a picture")

def text_to_speech(text, lang="en"):
    """Convert text to speech and return audio bytes."""
    tts = gTTS(text=text, lang=lang)
    audio_file = f"translation_audio_{lang}.mp3"
    tts.save(audio_file)
    
    with open(audio_file, "rb") as f:
        audio_bytes = f.read()
    os.remove(audio_file)  # Remove after reading
    return audio_bytes

def resize_image(image, max_size=800):
    """Resize image to a reasonable size to speed up OCR."""
    w, h = image.size
    scale = max_size / max(w, h)
    new_size = (int(w * scale), int(h * scale)) if scale < 1 else (w, h)
    return image.resize(new_size, Image.LANCZOS)  # Use LANCZOS instead of ANTIALIAS




def process_image(image, image_index):
    """Extract text, translate, and generate speech."""
    if image:
        image = Image.open(image)
        image = resize_image(image, max_size=800)
        st.image(image, caption=f"Processed Image {image_index + 1}", use_column_width=True)
        
        image_array = np.array(image)
        st.write("🔍 Extracting text...")
        
        # OCR Extraction
        result = reader.readtext(image_array)
        detected_texts = [detection[1] for detection in result]
        
        if detected_texts:
            st.subheader("📝 Detected Text:")
            detected_text_display = "\n".join(detected_texts)
            st.markdown(f"<div class='text-box'>{detected_text_display}</div>", unsafe_allow_html=True)
            
            if st.button(f"🌍 Translate Image {image_index + 1}", key=f"translate_{image_index}"):
                st.subheader("📖 Translated Text:")
                translated_texts = [GoogleTranslator(source='auto', target=target_lang_code).translate(text) for text in detected_texts]
                translated_text_display = "\n".join(translated_texts)
                st.markdown(f"<div class='text-box'>{translated_text_display}</div>", unsafe_allow_html=True)
                
                # Play audio
                audio_bytes = text_to_speech(translated_text_display, target_lang_code)
                st.audio(audio_bytes, format="audio/mp3")
        else:
            st.warning("⚠ No text detected in the image.")

# Process uploaded image or camera image
if uploaded_files:
    for idx, uploaded_file in enumerate(uploaded_files):
        process_image(uploaded_file, idx)
elif camera_image:
    process_image(camera_image, "camera")

st.markdown("</div>", unsafe_allow_html=True)

