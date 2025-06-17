import streamlit as st
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
import requests
from streamlit_lottie import st_lottie

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

PRIMARY_MODEL = "models/gemini-1.5-pro-latest"
FALLBACK_MODEL = "models/gemini-1.5-flash-latest"

# Function to load Lottie animation safely
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to load animation: {e}")
        return None

# Load animations
ai_animation = load_lottie_url("https://assets6.lottiefiles.com/packages/lf20_jcikwtux.json")
analysis_animation = load_lottie_url("https://assets2.lottiefiles.com/private_files/lf30_editor_jpxkgzsk.json")

# Set page config
st.set_page_config(page_title="AI Hiring Assistant", page_icon="🤖", layout="wide")

# Custom CSS styling (Bootstrap-inspired)
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Title Section with Centered Logo
st.markdown("""
    <div style='text-align: center;'>
        <img src='https://cdn-icons-png.flaticon.com/512/4712/4712105.png' width='100'>
        <h1>🤖 AI Hiring Assistant</h1>
        <p>This app helps streamline your hiring process using AI.</p>
    </div>
""", unsafe_allow_html=True)

# Centered Lottie Animation
if ai_animation:
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    st_lottie(ai_animation, height=250, key="centered-ai-animation")
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.warning("⚠️ AI animation failed to load.")

# File Upload Section
st.markdown('<div class="section-header">📥 Upload Documents</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
with col2:
    job_file = st.file_uploader("📝 Upload Job Description (TXT)", type=["txt"])

jd_text_input = st.text_area("✍️ Or Paste Job Description Below", height=150)

# Extract Resume Text
resume_text = ""
if resume_file:
    reader = PyPDF2.PdfReader(resume_file)
    resume_text = "".join([page.extract_text() or "" for page in reader.pages])

# Get Job Description
job_description = ""
if job_file:
    job_description = job_file.read().decode("utf-8")
elif jd_text_input:
    job_description = jd_text_input

# Show Extracted Resume
if resume_text:
    st.markdown('<div class="section-header">📄 Extracted Resume</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.text_area("Resume Content", resume_text, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

# Show Job Description
if job_description:
    st.markdown('<div class="section-header">📝 Job Description</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.text_area("Job Description", job_description, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

# Analyze Button
if resume_text and job_description and st.button("🔍 Analyze Resume Against JD"):
    with st.spinner("Analyzing with Gemini..."):
        if analysis_animation:
            st_lottie(analysis_animation, height=200)
        else:
            st.info("Analyzing...")

        prompt = f"""
        You are an AI hiring assistant. Compare the candidate's resume with the job description below.

        1. Give a match percentage (0–100%) based on how well the resume fits the job.
        2. List the candidate's strengths for the role.
        3. Point out any missing or weak areas.
        4. Generate 3 technical and 2 behavioral interview questions based on the job and resume.

        --- Job Description ---
        {job_description}

        --- Resume ---
        {resume_text}
        """

        def analyze_with_model(model_id):
            model = genai.GenerativeModel(model_id)
            return model.generate_content(prompt)

        try:
            response = analyze_with_model(PRIMARY_MODEL)
            st.success("✅ Analysis Complete (Gemini Pro)")
            st.markdown('<div class="section-header">🧠 AI Feedback</div>', unsafe_allow_html=True)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(response.text)
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            if "429" in str(e):
                st.warning("⚠️ Pro model quota exceeded. Trying with Flash model...")
                time.sleep(2)
                try:
                    response = analyze_with_model(FALLBACK_MODEL)
                    st.success("✅ Analysis Complete (Gemini Flash)")
                    st.markdown('<div class="section-header">🧠 AI Feedback</div>', unsafe_allow_html=True)
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.write(response.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as fallback_error:
                    st.error(f"❌ Fallback model failed: {fallback_error}")
            else:
                st.error(f"❌ Unexpected error: {e}")

# Footer
st.markdown("""
<hr style="margin-top: 40px;">
<p style='text-align: center; color: grey;'>
    Made with ❤️ by Vandana Cherukuri | Powered by Google Gemini & Streamlit
</p>
""", unsafe_allow_html=True)
