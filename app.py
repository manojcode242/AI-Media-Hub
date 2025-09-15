import streamlit as st
import google.genai as genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv


# Here we are generating imgs from the GEMINI model and 
# DOC : https://ai.google.dev/gemini-api/docs/image-generation (Which we are refering)

# ==============================
# Load API Key
# ==============================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# ==============================
# Page Setup
# ==============================
st.set_page_config(page_title="AI Media Hub", page_icon="🤖", layout="wide")

# ==============================
# Sidebar / Clear Button
# ==============================
with st.sidebar:
    st.title("⚙️ Controls")
    if st.button("🗑️ Clear Chat / Reset App"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()

# ==============================
# Custom CSS (center content + card style)
# ==============================
st.markdown(
    """
    <style>
    /* Center everything in the middle of the page */
    .block-container {
        max-width: 700px;  
        margin: auto;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Background */
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    /* Headings */
    h1, h2, h3 {
        color: white;
        font-weight: 700;
        text-align: center;
    }
    /* Card look */
    .stCard {
        background: #1C1F26;
        padding: 25px;
        border-radius: 12px;
        margin-top: 15px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.35);
    }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center; 
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1C1F26;
        border-radius: 8px;
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #4db8ff, #1a75ff);
        color: white !important;
        font-weight: 700;
    }
    /* Buttons */
    div.stButton > button {
        background-color: #262730;
        border-radius: 8px;
        padding: 0.6em 1.2em;
        color: white;
        border: 1px solid #4db8ff;
        font-weight: 600;
        display: block;
        margin: auto;  /* Center button */
    }
    div.stButton > button:hover {
        background: #4db8ff;
        color: black;
        border: none;
        transform: scale(1.02);
        transition: all 0.2s ease-in-out;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================
# Header
# ==============================
st.title("🤖 AI Media Hub")
st.markdown(
    " One stop AI tool for **Image Generation, Captioning & Video Summarization** 🚀"
)

# ==============================
# Tabs
# ==============================
tab1, tab2, tab3 = st.tabs(
    ["🎨 Image Generator", "✨ Image Captioning", "🎬 Video Summarizer"]
)

# ==============================
# TAB 1: Image Generator
# ==============================
with tab1:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.subheader("AI Image Generator")

    # Only Input + Button
    user_prompt = st.text_input("💡 Enter your prompt to generate an image:")

    if st.button("Generate IMG"):
        if not user_prompt:
            st.warning("⚠️ Please enter a prompt")
        else:
            try:
                with st.spinner("🎨 Generating image..."):
                    response = client.models.generate_content(
                        model="gemini-2.0-flash-exp-image-generation",
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            response_modalities=["Text", "Image"]
                        ),
                    )
                for part in response.candidates[0].content.parts:
                    if part.text is not None:
                        st.write(part.text)
                    elif part.inline_data is not None:
                        image = Image.open(BytesIO(part.inline_data.data))
                        st.image(image, use_container_width=True)
                        st.download_button(
                            "📥 Download Image",
                            data=part.inline_data.data,
                            file_name="generated.png",
                            mime="image/png",
                        )
            except Exception as e:
                st.error(f"❌ Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# TAB 2: Image Captioning
# ==============================
with tab2:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.subheader("AI Image Caption Generator")
    uploaded_img = st.file_uploader(
        "📤 Upload an image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"]
    )

    if uploaded_img:
        image = Image.open(uploaded_img)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        if st.button("Generate Caption"):
            try:
                with st.spinner("📝 Generating caption..."):
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=["What is in this image?", image],
                    )
                st.subheader("🖊️ Caption")
                st.success(response.text)
                st.download_button(
                    "📄 Download Caption",
                    data=response.text,
                    file_name="caption.txt",
                    mime="text/plain",
                )
            except Exception as e:
                st.error(f"❌ Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# TAB 3: YT Summarizer
# ==============================
with tab3:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.subheader("AI YouTube Video Summarizer")
    yt_url = st.text_input("🔗 Enter YouTube video URL")

    if st.button("Summarize Video"):
        if not yt_url:
            st.warning("⚠️ Please enter a valid YouTube URL")
        else:
            try:
                with st.spinner("📺 Summarizing video..."):
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=types.Content(
                            parts=[
                                types.Part(text="Summarize this video:"),
                                types.Part(file_data=types.FileData(file_uri=yt_url)),
                            ]
                        ),
                    )
                st.subheader("📌 Video Summary")
                st.info(response.text)
                st.download_button(
                    "📄 Download Summary",
                    data=response.text,
                    file_name="summary.txt",
                    mime="text/plain",
                )
            except Exception as e:
                st.error(f"❌ Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
