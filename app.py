import streamlit as st
import google.generativeai as genai
import pypdf
import pandas as pd

# 1. Setup & Configuration
st.set_page_config(page_title="AI Study Companion Hub", layout="wide")
st.title("📚 AI Study Companion Hub")
st.write("Upload a chapter PDF to generate study materials, or plan your day below!")

# Configure your Gemini API Key
# In production, use st.secrets for safety
API_KEY = st.sidebar.text_input("Enter your Gemini API Key:", type="password")
if API_KEY:
    genai.configure(api_key=API_KEY)

# 2. Sidebar Navigation
app_mode = st.sidebar.selectbox("Choose a Feature", ["Dashboard & AI Study Tools", "Timetable Planner"])

# --- FEATURE 1: AI STUDY TOOLS ---
if app_mode == "Dashboard & AI Study Tools":
    st.header("📖 Chapter AI Analyzer")
    uploaded_file = st.file_uploader("Upload your chapter PDF", type=["pdf"])

    if uploaded_file and not API_KEY:
        st.warning("Please enter your Gemini API key in the sidebar to process the PDF.")

    if uploaded_file and API_KEY:
        with st.spinner("Reading PDF and extracting text..."):
            # Extract text from PDF
            reader = pypdf.PdfReader(uploaded_file)
            extracted_text = ""
            for page in reader.pages[:10]: # Limiting to first 10 pages for demo/speed
                extracted_text += page.extract_text() + "\n"
        
        st.success("PDF uploaded successfully! What would you like to generate?")
        
        # Tabs for different AI outputs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Short Notes", "Summary & 1-Page Key Points", "Important Questions", "Flowchart Blueprint", "Visual Diagrams Guide"
        ])

        model = genai.GenerativeModel('gemini-pro')

        with tab1:
            st.subheader("📝 Concise Short Notes")
            if st.button("Generate Short Notes"):
                with st.spinner("Analyzing chapter..."):
                    response = model.generate_content(f"Create highly organized, clear short notes with bullet points for this text:\n\n{extracted_text[:4000]}")
                    st.markdown(response.text)

        with tab2:
            st.subheader("📄 Summary & 1-Page Key Points")
            if st.button("Generate Summary & Key Points"):
                with st.spinner("Condensing chapter..."):
                    prompt = f"Provide a brief overall summary followed by a strictly structured '1-Page Key Points' list for the following text:\n\n{extracted_text[:4000]}"
                    response = model.generate_content(prompt)
                    st.markdown(response.text)

        with tab3:
            st.subheader("❓ Easy & Important Questions")
            if st.button("Generate Questions"):
                with st.spinner("Formulating questions..."):
                    prompt = f"Based on this text, generate 5 Easy conceptual questions and 5 Highly Important exam questions. Provide answers separately below each section:\n\n{extracted_text[:4000]}"
                    response = model.generate_content(prompt)
                    st.markdown(response.text)

        with tab4:
            st.subheader("🌿 Chapter Flowchart")
            st.write("This generates a structured visual hierarchy of the chapter concepts.")
            if st.button("Render Flowchart"):
                with st.spinner("Mapping concepts..."):
                    # We prompt Gemini to output standard Graphviz DOT language
                    prompt = (
                        f"Analyze this text and create a concept flowchart map using Graphviz DOT language. "
                        f"Return ONLY the valid DOT code inside a standard code block, starting with 'digraph G {{' and ending with '}}'. "
                        f"Keep it clean, simple, and relevant to the text content:\n\n{extracted_text[:2000]}"
                    )
                    response = model.generate_content(prompt)
                    
                    # Extract the DOT code safely
                    raw_text = response.text
                    if "digraph" in raw_text:
                        dot_code = raw_text.split("```")
                        clean_dot = [c for c in dot_code if "digraph" in c][0].replace("dot", "").strip()
                        st.graphviz_chart(clean_dot)
                    else:
                        st.error("Could not render flowchart dynamically. Try clicking again.")

        with tab5:
            st.subheader("🎨 Diagram & Visual Guide")
            if st.button("Get Diagram Explanations"):
                with st.spinner("Identifying key processes..."):
                    prompt = (
                        f"Identify the main biological/scientific processes or structures in this text that require diagrams. "
                        f"Describe clearly how a student should draw them, what to label, and why they are important:\n\n{extracted_text[:4000]}"
                    )
                    response = model.generate_content(prompt)
                    st.markdown(response.text)

# --- FEATURE 2: TIMETABLE PLANNER ---
elif app_mode == "Timetable Planner":
    st.header("📅 Your Daily & Study Timetable")
    st.write("Plan your day and track your study slots perfectly.")

    # Initialize a simple session state timetable if it doesn't exist
    if "timetable" not in st.session_state:
        st.session_state.timetable = [
            {"Time Slot": "06:00 AM - 07:00 AM", "Activity/Subject": "Morning Routine / Exercise", "Type": "General Routine"},
            {"Time Slot": "09:00 AM - 11:00 AM", "Activity/Subject": "Study Session 1: Hardest Topic", "Type": "Study Block"},
            {"Time Slot": "02:00 PM - 04:00 PM", "Activity/Subject": "Study Session 2: Revision", "Type": "Study Block"},
        ]

    # Display Timetable
    df = pd.DataFrame(st.session_state.timetable)
    
    st.subheader("Current Schedule")
    # Allows user to edit the table directly on screen!
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    st.session_state.timetable = edited_df.to_dict('records')

    # Quick Add Form
    st.subheader("➕ Add New Time Slot")
    with st.form("add_slot_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            time_input = st.text_input("Time (e.g., 05:00 PM - 06:30 PM)")
        with col2:
            task_input = st.text_input("Subject or Activity")
        with col3:
            type_input = st.selectbox("Category", ["Study Block", "Break", "General Routine", "Sleep/Rest"])
        
        submit_btn = st.form_submit_with_button("Add to Timetable")
        
        if submit_btn and time_input and task_input:
            st.session_state.timetable.append({"Time Slot": time_input, "Activity/Subject": task_input, "Type": type_input})
            st.rerun()

    # AI Timetable Optimizer Helper
    if API_KEY and st.button("🤖 Let AI Review & Optimize My Timetable"):
        with st.spinner("Analyzing routine..."):
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"Review this daily student timetable schedule and suggest 3 quick, practical tips to maximize study focus and prevent burnout:\n{str(st.session_state.timetable)}"
            response = model.generate_content(prompt)
            st.info(response.text)
