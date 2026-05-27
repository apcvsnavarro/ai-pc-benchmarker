import os
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerperDevTool

# --- UI Setup & Theme ---
# Sets the app to full-width dashboard mode
st.set_page_config(
    page_title="V.A.N.G.U.A.R.D. Hardware AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Header ---
st.title("⚡ V.A.N.G.U.A.R.D.")
st.markdown("**V**irtual **A**ssistant for **N**ext-Gen **U**pgrades **A**nd **R**ig **D**iagnostics")
st.markdown("Advanced multi-agent telemetry, web-scouring, and bottleneck analysis for high-performance systems.")

# --- System Architecture Overview ---
# This replaces the static baseline rig and proves to the panel this is a multi-agent system.
st.subheader("Active Agent Architecture")
col1, col2, col3 = st.columns(3)
with col1:
    st.info("**🕵️‍♂️ Hardware Scout Agent**\n\nExecutes live Serper API web-scrapes to gather real-world benchmarks and thermal data.")
with col2:
    st.success("**👨‍💻 Lead Consultant Agent**\n\nSynthesizes raw data, detects hardware bottlenecks, and writes the final diagnostic report.")
with col3:
    st.warning("**🧠 Logic Engine**\n\nPowered by Google Gemini 2.5 Flash for high-speed reasoning and step-by-step task delegation.")

st.markdown("---")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("⚙️ System Directives")
    st.info("Input a specific hardware configuration or a general use-case for the agents to analyze.")
    
    user_query = st.text_area(
        "Hardware Target or Use-Case",
        "I need a PC for heavy 4K video editing in Premiere Pro, but my budget is only $1,200. What is the best configuration, and what compromises will I have to make?",
        height=150
    )
    
    run_button = st.button("Initialize V.A.N.G.U.A.R.D. 🚀", use_container_width=True)
    
    st.markdown("---")
    st.caption("Agent Framework: CrewAI")

# --- The App Logic ---
if run_button:
    with st.spinner("Agents are scouring benchmarks, evaluating components, and calculating bottlenecks..."):
        try:
            # 1. Setup the Brain & Tools
            os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
            os.environ["SERPER_API_KEY"] = st.secrets["SERPER_API_KEY"]
            
            google_llm = LLM(
                model="gemini/gemini-2.5-flash",
                api_key=st.secrets["GEMINI_API_KEY"]
            )
            
            search_tool = SerperDevTool()

            # 2. Define the Agents
            hardware_scout = Agent(
                role='Hardware Performance Analyst',
                goal='Search the web for live benchmarks, thermal limits, and hardware recommendations for the user query.',
                backstory='You are a senior PC hardware reviewer specializing in high-refresh-rate optimization and professional workstation builds.',
                llm=google_llm,
                verbose=False,
                allow_delegation=False,
                tools=[search_tool]
            )

            consultant = Agent(
                role='Lead IT Hardware Consultant',
                goal='Synthesize raw benchmark data into a professional compatibility, recommendation, and bottleneck report.',
                backstory='Trusted by enthusiasts and professionals to give brutally honest advice on system bottlenecks, power supply constraints, and budget compromises.',
                llm=google_llm,
                verbose=False,
                allow_delegation=False
            )

            # 3. Define the Tasks
            research_task = Task(
                description=f'Search for current benchmarks, hardware combinations, and technical reviews testing this query: {user_query}.',
                expected_output='A raw data summary of recommended parts, framerates/render times, and noted bottlenecks.',
                agent=hardware_scout
            )

            report_task = Task(
                description='Using the scouted data, write a final Markdown report. Include: 1. Recommended Build/Target Performance, 2. Bottleneck Analysis, 3. Thermal/Power Warnings, 4. Final Verdict.',
                expected_output='A professional 4-section Markdown report.',
                agent=consultant
            )

            # 4. Fire up the Crew
            pc_crew = Crew(
                agents=[hardware_scout, consultant],
                tasks=[research_task, report_task],
                process=Process.sequential,
                max_rpm=3
            )

            result = pc_crew.kickoff()

            # 5. Display the Results on the Web App
            st.success("V.A.N.G.U.A.R.D. Analysis Complete!")
            
            # Transparent workflow proof
            with st.expander("🔍 View Diagnostics Pipeline Status"):
                st.write("✅ Web Scrape & Telemetry Gathered")
                st.write("✅ Bottleneck Synthesis Complete")
                st.write("✅ Final Render Complete")
            
            st.markdown("### 📊 System Diagnostic Report")
            st.markdown(str(result))

        # Failsafe for API congestion
        except Exception as e:
            st.error("Agent flow interrupted by API server traffic.")
            st.warning(f"Technical details: {e}")
            st.info("The external API is temporarily congested. Please wait 30 seconds and click Initialize again.")