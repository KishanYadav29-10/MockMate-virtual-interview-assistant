# app.py

import streamlit as st
from resume_parser import parse_resume, extract_links_from_pdf
from llm_question_generator import generate_llm_questions, evaluate_answer
from voice_input import recognize_voice
from audiorecorder import audiorecorder
import base64, tempfile, wave, json
from fpdf import FPDF
from io import BytesIO
from pydub import AudioSegment
import re

from nlp_extractor import (
    extract_email,
    extract_phone,
    extract_name,
    extract_skills,
    extract_sections,
    extract_projects
)

st.set_page_config(page_title="MockMate - Virtual Mock Interviewer", layout="centered")
st.title("🧠 MockMate - Virtual Mock Interviewer")
st.subheader("📄 Upload your resume to generate personalized interview questions")

if "llm_questions" not in st.session_state:
    st.session_state.llm_questions = []

if "transcripts" not in st.session_state:
    st.session_state.transcripts = []

if "answered_questions" not in st.session_state:
    st.session_state.answered_questions = {}

uploaded_file = st.file_uploader("📤 Choose your resume file (PDF or DOCX)", type=['pdf', 'docx'])

if uploaded_file is not None:
    st.success("✅ Resume uploaded successfully!")

    with st.spinner("🔍 Parsing your resume..."):
        resume_text = parse_resume(uploaded_file)
        pdf_links = extract_links_from_pdf(uploaded_file) if uploaded_file.name.endswith(".pdf") else []

    if "⚠️ No readable text" in resume_text:
        st.warning("⚠️ No readable text found in uploaded PDF.")
    else:
        emails = [link for link in pdf_links if "mailto:" in link]
        linkedin = [link for link in pdf_links if "linkedin.com" in link]
        github = [link for link in pdf_links if "github.com" in link]

        name = extract_name(resume_text)
        email = extract_email(resume_text) or (emails[0][7:] if emails else "Not found")
        phone = extract_phone(resume_text) or "Not found"
        skills = extract_skills(resume_text)
        sections = extract_sections(resume_text)
        project_blocks = extract_projects(resume_text)

        st.text_area("📝 Extracted Resume Text", resume_text, height=300)

        st.markdown("### 📊 Extracted Resume Info")
        st.markdown(f"👤 **Name:** `{name}`")
        st.markdown(f"📧 **Email:** `{email}`")
        st.markdown(f"📱 **Phone:** `{phone}`")
        st.markdown(f"🔗 **LinkedIn:** {linkedin[0] if linkedin else 'Not found'}")
        st.markdown(f"🐙 **GitHub:** {github[0] if github else 'Not found'}")
        st.markdown(f"🧠 **Skills:** `{', '.join(skills) if skills else 'No skills detected'}`")

        st.markdown("### 🛠️ Projects")
        if project_blocks:
            for i, proj in enumerate(project_blocks, 1):
                st.markdown(f"**Project {i}:**")
                st.code(proj, language='text')
        else:
            st.markdown("❌ No projects found.")

        st.markdown("### 💼 Experience")
        if "Experience" in sections and sections["Experience"]:
            st.code('\n'.join(sections["Experience"]), language='text')
        else:
            st.info("🎓 Fresher / No prior professional experience")

        st.markdown("### 🤖 LLM-Powered Mock Interview")

        if st.button("🎯 Generate AI Questions (Mistral via Ollama)"):
            with st.spinner("Generating questions using Mistral..."):
                st.session_state.llm_questions = generate_llm_questions(
                    name,
                    skills,
                    "\n".join(project_blocks),
                    "\n".join(sections.get("Experience", []))
                )
                st.session_state.transcripts = []
                st.session_state.answered_questions = {}

        if st.session_state.llm_questions:
            for idx, q in enumerate(st.session_state.llm_questions, 1):
                with st.expander(f"**Q{idx}:** {q.strip()}", expanded=(idx not in st.session_state.answered_questions)):
                    if idx not in st.session_state.answered_questions:
                        st.markdown("🎙️ Record your answer below:")
                        audio_segment = audiorecorder("Start Recording", "Stop Recording", key=f"rec_{idx}")

                        if audio_segment:
                            buffer = BytesIO()
                            audio_segment.export(buffer, format="wav")
                            buffer.seek(0)

                            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                                tmp.write(buffer.read())
                                tmp_path = tmp.name

                            with st.spinner("🧠 Transcribing..."):
                                transcription = recognize_voice(tmp_path)
                            st.markdown(f"📝 **Your Answer:** {transcription}")

                            with st.spinner("💬 Getting feedback..."):
                                feedback = evaluate_answer(q.strip(), transcription)
                            st.success(f"🧠 **Feedback:**\n{feedback}")

                            st.session_state.transcripts.append({
                                "question": q.strip(),
                                "answer": transcription,
                                "feedback": feedback
                            })

                            st.session_state.answered_questions[idx] = True

        if st.session_state.transcripts:
            st.markdown("### 🧾 Interview Summary")
            total = len(st.session_state.transcripts)
            scores = []
            for t in st.session_state.transcripts:
                match = re.search(r"Score:\s*(\d+)/10", t["feedback"])
                if match:
                    scores.append(int(match.group(1)))

            if scores:
                avg_score = sum(scores) / len(scores)
                st.markdown(f"✅ **Answered Questions:** {total}")
                st.markdown(f"📈 **Average Score:** {avg_score:.1f}/10")

                if avg_score >= 8:
                    st.success("🏅 Excellent performance! You're well-prepared.")
                elif avg_score >= 5:
                    st.info("📝 Decent job. A bit more practice will help.")
                else:
                    st.warning("🚧 Needs improvement. Try refining your answers.")

                st.bar_chart(scores)

            st.markdown("### 📤 Export Interview Report")

            if st.button("📄 Download as PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                for entry in st.session_state.transcripts:
                    pdf.multi_cell(0, 10, f"Q: {entry['question']}\nA: {entry['answer']}\nFeedback: {entry['feedback']}\n")

                pdf_path = "mock_interview_answers.pdf"
                pdf.output(pdf_path)
                with open(pdf_path, "rb") as f:
                    st.download_button("📥 Click to download PDF", data=f, file_name=pdf_path)

            if st.button("📄 Download as JSON"):
                st.download_button("📥 Click to download JSON", json.dumps(st.session_state.transcripts, indent=2), file_name="answers.json")