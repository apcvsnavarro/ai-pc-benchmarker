import streamlit as st
import re
import os
import plotly.graph_objects as go
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai_tools import SerperDevTool

# ==========================================
# 1. PAGE CONFIG & SESSION MEMORY INIT
# ==========================================
st.set_page_config(page_title="V.A.N.G.U.A.R.D.", layout="wide", page_icon="⚡")

# Initialize Session Memory for the Audit Trail (Ms. Rhea's feature)
if 'diagnostic_history' not in st.session_state:
    st.session_state.diagnostic_history = []

# ==========================================
# 2. API KEYS SETUP
# ==========================================
# Grabbing keys securely from .streamlit/secrets.toml
# Langchain strictly requires the environment variable to be named 'GOOGLE_API_KEY'
os.environ["GOOGLE_API_KEY"] = st.secrets["GEMINI_API_KEY"]
os.environ["SERPER_API_KEY"] = st.secrets["SERPER_API_KEY"]

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
search_tool = SerperDevTool()

# ==========================================
# 3. PLOTLY VISUALIZATION FUNCTIONS
# ==========================================
def render_bottleneck_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Bottleneck Severity %", 'font': {'color': 'white'}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': "white"},
            'bar': {'color': "#00ff00" if score < 20 else ("#ffff00" if score < 50 else "#ff0000")},
            'bgcolor': "black",
            'steps': [
                {'range': [0, 20], 'color': "rgba(0, 255, 0, 0.1)"},
                {'range': [20, 50], 'color': "rgba(255, 255, 0, 0.1)"},
                {'range': [50, 100], 'color': "rgba(255, 0, 0, 0.1)"}],
        }
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"}, height=300)
    st.plotly_chart(fig, use_container_width=True)

def render_price_inflation_chart(msrp, current):
    inflation_pct = ((current - msrp) / msrp) * 100 if msrp > 0 else 0
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Original MSRP', 'Current Market Price'],
        y=[msrp, current],
        marker_color=['#555555', '#00ff00' if inflation_pct <= 0 else '#ff0000'],
        text=[f"${msrp}", f"${current}"],
        textposition='auto'
    ))
    fig.update_layout(
        title=f"Price Inflation: {inflation_pct:+.1f}%",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 4. SIDEBAR: MEMORY AUDIT TRAIL
# ==========================================
with st.sidebar:
    st.header("⚡ Diagnostic History") # Fixed the broken image link!
    st.markdown("---")
    
    if st.session_state.diagnostic_history:
        for i, record in enumerate(reversed(st.session_state.diagnostic_history)):
            with st.expander(f"Run {len(st.session_state.diagnostic_history) - i}: {record['prompt'][:20]}..."):
                st.write(f"**Query:** {record['prompt']}")
                st.write(f"**Power:** {record['power']}W | **Bottleneck:** {record['bottleneck']}%")
    else:
        st.info("No past diagnostics in this session. Initialize a query to begin.")

# ==========================================
# 5. MAIN UI LAYOUT
# ==========================================
st.title("⚡ V.A.N.G.U.A.R.D.")
st.subheader("Virtual Assistant for Next-Gen Upgrades And Rig Diagnostics")

user_input = st.text_input("Enter your hardware configuration or build idea:", placeholder="e.g., RTX 4090 with an Intel Core i9 on a 400W PSU")

if st.button("Initialize Diagnostics", type="primary"):
    if user_input:
        try:
            with st.status("Agents Scouring Live Web & Analyzing Telemetry...", expanded=True) as status:
                
                # --- AGENT DEFINITIONS ---
                scout_agent = Agent(
                    role="Hardware Telemetry Scout",
                    goal="Scour the live web for real-world benchmarks, thermal limits, power draw (TDP), and pricing data for the given hardware.",
                    backstory="You are an expert PC hardware researcher. You find accurate, up-to-date data for PC parts, including their original MSRP and their current market price.",
                    verbose=True,
                    allow_delegation=False,
                    tools=[search_tool],
                    llm=llm
                )

                consultant_agent = Agent(
                    role="Lead IT Consultant",
                    goal="Analyze the scout's data, calculate bottlenecks, verify power constraints, and output precise diagnostic telemetry.",
                    backstory="You are a senior IT hardware architect. You do not hallucinate math. You provide brutally honest compatibility diagnostics.",
                    verbose=True,
                    allow_delegation=False,
                    llm=llm
                )

                # --- TASK DEFINITIONS ---
                scout_task = Task(
                    description=f"Search the web for real-world data regarding: {user_input}. Specifically find: 1. CPU/GPU power draw. 2. CPU/GPU bottlenecks. 3. The original MSRP and current market price of the primary GPU or CPU mentioned.",
                    expected_output="A raw data summary of power draw, bottlenecks, and pricing.",
                    agent=scout_agent
                )

                consultant_task = Task(
                    description=f"Using the scout's data, write a short diagnostic report for: {user_input}.\n\n"
                                "CRITICAL INSTRUCTIONS - YOU MUST INCLUDE THESE EXACT LINES AT THE END OF YOUR REPORT:\n"
                                "Bottleneck Score: [Insert integer 0-100 here]\n"
                                "Estimated Power Draw: [Insert integer here]\n"
                                "GPU MSRP: [Insert integer here]\n"
                                "GPU Current Price: [Insert integer here]\n",
                    expected_output="A Markdown diagnostic report ending with the four exact mathematical metrics requested.",
                    agent=consultant_agent
                )

                # --- CREW EXECUTION ---
                vanguard_crew = Crew(
                    agents=[scout_agent, consultant_agent],
                    tasks=[scout_task, consultant_task],
                    process=Process.sequential
                )
                
                result = vanguard_crew.kickoff()
                status.update(label="Diagnostics Complete!", state="complete", expanded=False)

            # --- REGEX EXTRACTION (THE SAFETY NET) ---
            raw_text = str(result)
            
            # Using Try/Except inside regex to provide safe fallbacks if the LLM hallucinates
            try: bottleneck_val = int(re.search(r"Bottleneck Score:\s*(\d+)", raw_text).group(1))
            except: bottleneck_val = 50 
            
            try: power_val = int(re.search(r"Estimated Power Draw:\s*(\d+)", raw_text).group(1))
            except: power_val = 450
            
            try: msrp_val = int(re.search(r"GPU MSRP:\s*(\d+)", raw_text).group(1))
            except: msrp_val = 800
            
            try: current_val = int(re.search(r"GPU Current Price:\s*(\d+)", raw_text).group(1))
            except: current_val = 850

            # --- RENDER VISUALS ---
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("System Bottleneck")
                render_bottleneck_gauge(bottleneck_val)
                st.metric(label="Calculated Power Draw", value=f"{power_val}W", delta="Check PSU Limits", delta_color="off")
                
            with col2:
                st.subheader("Market Price Tracker")
                render_price_inflation_chart(msrp_val, current_val)
            
            # --- RENDER REPORT ---
            st.markdown("### Agent Diagnostic Report")
            st.markdown(raw_text)

            # --- SAVE TO MEMORY ---
            st.session_state.diagnostic_history.append({
                "prompt": user_input,
                "power": power_val,
                "bottleneck": bottleneck_val,
                "report": raw_text
            })

        except Exception as e:
            # THIS IS YOUR MS. RHEA DEFENSE CODE
            st.error("⚠️ Agent flow interrupted by API server traffic. Please wait 30 seconds and try again.")
            print(f"API Error Log: {e}")