import streamlit as st
import time
import json
import os
import uuid
from agents.resume_parser import parse_resume
from agents.technical_agent import technical_agent
from agents.behavioral_agent import behavioral_agent
from agents.evaluator_agent import evaluator_agent
from agents.feedback_agent import feedback_agent
from agents.interview_manager import interview_manager
from agents.filler_detector import detect_fillers
from agents.voice_agent import text_to_speech

SESSIONS_DIR = "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

def save_session():
    if "session_id" in st.session_state:
        data = {
            "stage": st.session_state.stage,
            "state": st.session_state.state,
            "question": st.session_state.question,
            "history": st.session_state.history,
            "q_count": st.session_state.q_count,
            "report": st.session_state.report,
            "shown_questions": list(st.session_state.get("shown_questions", set())),
            "last_filler": st.session_state.last_filler,
        }
        path = os.path.join(SESSIONS_DIR, f"{st.session_state.session_id}.json")
        with open(path, "w") as f:
            json.dump(data, f)

def load_session(session_id):
    path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def stream_question(text):
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.markdown(f"""
        <div class="question-box">
            <div class="interviewer-label">🎙️ Interviewer</div>
            {displayed}
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.015)
    placeholder.markdown(f"""
    <div class="question-box">
        <div class="interviewer-label">🎙️ Interviewer</div>
        {displayed}
    </div>
    """, unsafe_allow_html=True)

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#  Session ID setup (survives refresh via URL)
query_params = st.query_params
if "sid" in query_params:
    st.session_state.session_id = query_params["sid"]
elif "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
    st.query_params["sid"] = st.session_state.session_id

# ── Session State Init ──
if "stage" not in st.session_state:
    st.session_state.stage = "setup"
if "state" not in st.session_state:
    st.session_state.state = {}
if "question" not in st.session_state:
    st.session_state.question = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "q_count" not in st.session_state:
    st.session_state.q_count = 0
if "report" not in st.session_state:
    st.session_state.report = ""
if "last_filler" not in st.session_state:
    st.session_state.last_filler = None
if "shown_questions" not in st.session_state:
    st.session_state.shown_questions = set()

# ── Load saved session on refresh (runs once) ──
if "loaded" not in st.session_state:
    saved = load_session(st.session_state.session_id)
    if saved:
        st.session_state.stage = saved["stage"]
        st.session_state.state = saved["state"]
        st.session_state.question = saved["question"]
        st.session_state.history = saved["history"]
        st.session_state.q_count = saved["q_count"]
        st.session_state.report = saved["report"]
        st.session_state.shown_questions = set(saved.get("shown_questions", []))
        st.session_state.last_filler = saved.get("last_filler")
    st.session_state.loaded = True

TOTAL_QUESTIONS = 5

# STAGE 1 — SETUP
if st.session_state.stage == "setup":

    st.markdown("""
    <div class="logo-wrap">
        <div class="logo-title">🎯 AI Interview Coach</div>
        <div class="logo-sub">Your personal AI-powered mock interviewer</div>
        <div class="stats-row">
            <div class="stat-item">
                <span class="stat-value">6</span>
                <span class="stat-label">AI Agents</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
                <span class="stat-value">5</span>
                <span class="stat-label">Questions</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
                <span class="stat-value">100%</span>
                <span class="stat-label">Free</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📄 Upload Your Resume (PDF)", type="pdf")
    job_role = st.text_input("💼 Job Role", placeholder="e.g. AI Engineer, Frontend Developer")
    company = st.text_input("🏢 Target Company (optional)", placeholder="e.g. Google, Meta, local startup name")
    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

    if st.button("🚀 Start My Interview"):
        if uploaded_file and job_role:
            with st.spinner("Reading your resume..."):
                resume_data = parse_resume(uploaded_file)
                state = {
                    "job_role": job_role,
                    "company": company if company.strip() else "a general tech company",
                    "resume_data": resume_data,
                    "interview_history": "",
                    "round": "",
                    "question": "",
                    "evaluation": ""
                }
                round_decision = interview_manager(state)
                state["round"] = round_decision
                st.session_state.state = state

            with st.spinner("Preparing your interview..."):
                if "Technical" in round_decision:
                    q = technical_agent(st.session_state.state, include_code=True)
                else:
                    q = behavioral_agent(st.session_state.state)
                st.session_state.question = q
                st.session_state.stage = "interview"
                save_session()
                st.rerun()
        else:
            st.warning("Please upload your resume and enter a job role first.")

    st.markdown('</div>', unsafe_allow_html=True)

# STAGE 2 - INTERVIEW
elif st.session_state.stage == "interview":

    st.markdown("""
    <div class="page-title">
        <h1>🎯 AI Interview Coach</h1>
    </div>
    """, unsafe_allow_html=True)

    main_col, score_col = st.columns([2.2, 1])

    with main_col:
        round_name = st.session_state.state.get('round', 'Technical').strip().rstrip('.')
        progress_pct = int((st.session_state.q_count / TOTAL_QUESTIONS) * 100)

        company_name = st.session_state.state.get('company', 'a general tech company')
        st.markdown(f"""
        <div class="badge-row">
            <div class="round-badge">🔵 {round_name} Round</div>
            <div class="company-badge">🏢 {company_name}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f'<div class="progress-label">Question {st.session_state.q_count + 1} of {TOTAL_QUESTIONS}</div>', unsafe_allow_html=True)
        st.progress(progress_pct / 100)

        if st.session_state.q_count not in st.session_state.shown_questions:
            if "```" in st.session_state.question:
                st.markdown('<div class="interviewer-label">🎙️ Interviewer</div>', unsafe_allow_html=True)
                st.markdown(st.session_state.question)
            else:
                stream_question(st.session_state.question)
            st.session_state.shown_questions.add(st.session_state.q_count)
            save_session()
        else:
            if "```" in st.session_state.question:
                st.markdown('<div class="interviewer-label">🎙️ Interviewer</div>', unsafe_allow_html=True)
                st.markdown(st.session_state.question)
            else:
                st.markdown(f"""
                <div class="question-box">
                    <div class="interviewer-label">🎙️ Interviewer</div>
                    {st.session_state.question}
                </div>
                """, unsafe_allow_html=True)

        with st.spinner("🔊 Interviewer speaking..."):
            audio = text_to_speech(st.session_state.question)
            st.audio(audio, format="audio/mp3", autoplay=True)

        answer = st.text_area(
            "Your Answer",
            placeholder="Take a breath and type your answer here...",
            height=140,
            key=f"answer_{st.session_state.q_count}"
        )

        submit = st.button("Submit Answer ➜")

    with score_col:
        st.markdown('<div class="scoreboard-title">📊 Scoreboard</div>', unsafe_allow_html=True)

        if st.session_state.history:
            avg_tech = sum(h['evaluation']['technical_accuracy'] for h in st.session_state.history) / len(st.session_state.history)
            avg_comm = sum(h['evaluation']['communication'] for h in st.session_state.history) / len(st.session_state.history)
            avg_conf = sum(h['evaluation']['confidence'] for h in st.session_state.history) / len(st.session_state.history)
        else:
            avg_tech = avg_comm = avg_conf = 0

        st.markdown(f"""
        <div class="score-box">
            <span class="score-value">{avg_tech:.1f}</span>
            <span class="score-label">Technical</span>
        </div>
        <div class="score-box">
            <span class="score-value">{avg_comm:.1f}</span>
            <span class="score-label">Communication</span>
        </div>
        <div class="score-box">
            <span class="score-value">{avg_conf:.1f}</span>
            <span class="score-label">Confidence</span>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.last_filler and st.session_state.last_filler['total_fillers'] > 0:
            filler_list = ", ".join([f"{w} ×{c}" for w, c in st.session_state.last_filler['breakdown'].items()])
            st.markdown(f"""
            <div class="score-box filler-box">
                <span class="score-value">{st.session_state.last_filler['total_fillers']}</span>
                <span class="score-label">Filler Words</span>
                <span class="filler-detail">{filler_list}</span>
            </div>
            """, unsafe_allow_html=True)

    if submit:
        if answer.strip():
            filler_result = detect_fillers(answer)
            st.session_state.last_filler = filler_result

            with st.spinner("Evaluating your answer..."):
                evaluation = evaluator_agent(st.session_state.question, answer)
                st.session_state.history.append({
                    "question": st.session_state.question,
                    "answer": answer,
                    "evaluation": evaluation
                })
                st.session_state.state["interview_history"] += f"\nQ: {st.session_state.question}\nA: {answer}\nScore: Technical {evaluation['technical_accuracy']}/10, Communication {evaluation['communication']}/10, Confidence {evaluation['confidence']}/10. Feedback: {evaluation['feedback']}\n"
                st.session_state.q_count += 1

            if st.session_state.q_count >= TOTAL_QUESTIONS:
                st.session_state.stage = "results"
                save_session()
                st.rerun()
            else:
                with st.spinner("Preparing next question..."):
                    if "Technical" in st.session_state.state['round']:
                        want_code = st.session_state.q_count % 2 == 0
                        next_q = technical_agent(st.session_state.state, user_answer=answer, include_code=want_code)
                    else:
                        next_q = behavioral_agent(st.session_state.state, user_answer=answer)
                    st.session_state.question = next_q
                    save_session()
                    st.rerun()
        else:
            st.warning("Please type your answer before submitting.")


# STAGE 3 — REPORT Card
elif st.session_state.stage == "results":

    st.markdown("""
    <div class="page-title">
        <h1>🎯 AI Interview Coach</h1>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.report:
        with st.spinner("Generating your personalized report..."):
            st.session_state.report = feedback_agent(st.session_state.state)
            save_session()

    st.markdown(f"""
    <div class="report-card">
    {st.session_state.report}
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "📥 Download Report",
            data=st.session_state.report,
            file_name="interview_report.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col2:
        if st.button("🔄 New Interview", use_container_width=True):
            session_path = os.path.join(SESSIONS_DIR, f"{st.session_state.session_id}.json")
            if os.path.exists(session_path):
                os.remove(session_path)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.query_params.clear()
            st.rerun()