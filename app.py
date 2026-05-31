import streamlit as st
import re
import os
import plotly.graph_objects as go
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# ==========================================
# 1. PAGE CONFIG & SESSION MEMORY INIT
# ==========================================
st.set_page_config(page_title="V.A.N.G.U.A.R.D.", layout="wide", page_icon="⚡")

if 'diagnostic_history' not in st.session_state:
    st.session_state.diagnostic_history = []

if 'current_run' not in st.session_state:
    st.session_state.current_run = None

if 'api_key_index' not in st.session_state:
    st.session_state.api_key_index = 0

# ==========================================
# 2. API KEYS SETUP
# ==========================================
os.environ["SERPER_API_KEY"] = st.secrets["SERPER_API_KEY"]
gemini_keys = st.secrets["GEMINI_API_KEYS"]

# Safely load Groq if it exists in secrets
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

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

def render_price_fluctuation_chart(msrp, current):
    fluctuation_pct = ((current - msrp) / msrp) * 100 if msrp > 0 else 0
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Original MSRP', 'Current Market Price'],
        y=[msrp, current],
        marker_color=['#555555', '#00ff00' if fluctuation_pct <= 0 else '#ff0000'],
        text=[f"{msrp} USD", f"{current} USD"], 
        textposition='auto'
    ))
    fig.update_layout(
        title=f"Market Price Fluctuation: {fluctuation_pct:+.1f}%",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 4. SIDEBAR: THE NEW CONTROL PANEL
# ==========================================
with st.sidebar:
    st.markdown("## ⚡ V.A.N.G.U.A.R.D.")
    
    if st.button("🏠 Home Dashboard", use_container_width=True, type="secondary"):
        st.session_state.current_run = None
        st.rerun()

    st.markdown("---")
    
    st.markdown("### ⚙️ Diagnostic Tuning")
    
    # NEW: The AI Engine Selector!
    ai_engine = st.selectbox("AI Engine", ["Gemini 2.5 Flash", "Llama 3 (Groq)"])
    
    target_workload = st.selectbox(
        "Target Workload", 
        ["General Productivity", "Heavy 3D Rendering", "Heavy AAA Gaming (Ultra Settings)", "Local AI/LLM Training", "1080p eSports Gaming"]
    )
    max_budget = st.slider("Max Budget (USD)", min_value=500, max_value=8000, value=2500, step=100)
    
    st.markdown("---")
    
    st.markdown("### 🗂️ Recents")
    if st.session_state.diagnostic_history:
        for i, record in enumerate(reversed(st.session_state.diagnostic_history)):
            if st.button(f"📌 {record['title']}", key=f"hist_{i}", use_container_width=True):
                st.session_state.current_run = record
                st.rerun()
    else:
        st.caption("No recent diagnostics in this session.")

    st.markdown("---")
    
    st.markdown("### 📡 System Status")
    
    # Dynamically updates the status based on your engine choice
    if ai_engine == "Gemini 2.5 Flash":
        st.caption(f"🟢 **Active Engine:** Gemini Slot [{st.session_state.api_key_index + 1}/{len(gemini_keys)}]")
    else:
        st.caption("🟢 **Active Engine:** Llama 3 (Groq)")
        
    st.caption("🟢 **Serper Uplink:** Connected")

# ==========================================
# 5. MAIN UI LAYOUT
# ==========================================
st.title("⚡ V.A.N.G.U.A.R.D.")
st.subheader("Virtual Assistant for Next-Gen Upgrades And Rig Diagnostics")

user_input = st.text_input("Enter your hardware configuration or build idea:", placeholder="e.g., RTX 4090 with an Intel Core i9 on a 400W PSU")

if st.button("Initialize Diagnostics", type="primary"):
    if user_input:
        
        success = False
        attempts = 0
        
        # If Gemini, use all 5 slots. If Groq, just 1 attempt is needed.
        max_attempts = len(gemini_keys) if ai_engine == "Gemini 2.5 Flash" else 1
        
        with st.status(f"Agents Scouring Live Web via {ai_engine}...", expanded=True) as status:
            
            while attempts < max_attempts and not success:
                
                # --- DYNAMIC ENGINE ROUTING ---
                if ai_engine == "Gemini 2.5 Flash":
                    current_api_key = gemini_keys[st.session_state.api_key_index]
                    os.environ["GEMINI_API_KEY"] = current_api_key
                    llm_model = "gemini/gemini-2.5-flash"
                else:
                    llm_model = "groq/llama3-8b-8192"
                
                try:
                    scout_agent = Agent(
                        role="Hardware Telemetry Scout",
                        goal="Scour the live web for real-world benchmarks, thermal limits, power draw (TDP), and pricing data for the given hardware.",
                        backstory="You are an expert PC hardware researcher. You find accurate, up-to-date data for PC parts, including their original MSRP and their current market price.",
                        verbose=True,
                        allow_delegation=False,
                        tools=[search_tool],
                        llm=llm_model, # <--- INJECTS YOUR CHOSEN AI ENGINE HERE
                        max_iter=3
                    )

                    consultant_agent = Agent(
                        role="Lead IT Consultant",
                        goal="Analyze the scout's data, calculate bottlenecks, verify power constraints, and output precise diagnostic telemetry.",
                        backstory="You are a senior IT hardware architect. You do not hallucinate math. You provide brutally honest compatibility diagnostics.",
                        verbose=True,
                        allow_delegation=False,
                        llm=llm_model, # <--- INJECTS YOUR CHOSEN AI ENGINE HERE
                        max_iter=3
                    )

                    scout_task = Task(
                        description=f"Analyze the user's request: '{user_input}'. "
                                    f"Their budget is {max_budget} USD, and target workload is {target_workload}. "
                                    "CRITICAL INSTRUCTION: If the user's request is vague or does not specify exact CPU/GPU models, YOU MUST immediately decide on a specific, realistic CPU and GPU combination that fits their budget. "
                                    "Once the exact hardware is decided, search the web to find: 1. CPU/GPU power draw. 2. CPU/GPU bottlenecks. 3. Original MSRP and current market price for that specific hardware.",
                        expected_output="A raw data summary of the specific CPU/GPU chosen, their power draw, bottlenecks, and pricing.",
                        agent=scout_agent
                    )

                    consultant_task = Task(
                        description=f"Using the scout's data, write a detailed 4-part diagnostic report for: '{user_input}'.\n\n"
                                    f"Evaluate if this build can handle '{target_workload}' and if it makes sense for a budget of {max_budget} USD.\n\n"
                                    "Format your response with these exact four sections:\n"
                                    "### 1. Compatibility & Bottlenecks\n"
                                    "### 2. Power Constraints\n"
                                    "### 3. Pricing Context\n"
                                    "### 4. Final Verdict\n\n"
                                    "CRITICAL FORMATTING RULE: DO NOT use the '$' symbol anywhere in your text. Use the word 'USD' instead.\n\n"
                                    "CRITICAL INSTRUCTIONS - YOU MUST INCLUDE THESE EXACT LINES AT THE VERY END OF YOUR REPORT:\n"
                                    "Report Title: [Insert a short, catchy 3-to-5 word title for this build here]\n"
                                    "Bottleneck Score: [Insert integer 0-100 here]\n"
                                    "Estimated Power Draw: [Insert integer here]\n"
                                    "GPU MSRP: [Insert integer here]\n"
                                    "GPU Current Price: [Insert integer here]\n",
                        expected_output="A 4-part Markdown diagnostic report ending with the specific requested metrics.",
                        agent=consultant_agent
                    )

                    vanguard_crew = Crew(
                        agents=[scout_agent, consultant_agent],
                        tasks=[scout_task, consultant_task],
                        process=Process.sequential,
                        max_rpm=10 
                    )
                    
                    result = vanguard_crew.kickoff()
                    success = True 
                    status.update(label="Diagnostics Complete!", state="complete", expanded=False)

                except Exception as e:
                    error_msg = str(e)
                    # ONLY rotate if Gemini hit a rate limit
                    if ai_engine == "Gemini 2.5 Flash" and ("429" in error_msg or "quota" in error_msg.lower() or "exhausted" in error_msg.lower()):
                        st.session_state.api_key_index = (st.session_state.api_key_index + 1) % len(gemini_keys)
                        attempts += 1
                        st.write(f"⚠️ Speed limit hit. Auto-rotating to Gemini Slot [{st.session_state.api_key_index + 1}/{len(gemini_keys)}]...")
                    else:
                        st.error(f"⚠️ ACTUAL ERROR LOG: {e}")
                        break

        if success:
            raw_text = str(result)
            
            try: report_title = re.search(r"Report Title:\s*(.*)", raw_text).group(1).strip()
            except: report_title = f"{user_input[:15]}... Build"

            try: bottleneck_val = int(re.search(r"Bottleneck Score:\s*(\d+)", raw_text).group(1))
            except: bottleneck_val = 50 
            
            try: power_val = int(re.search(r"Estimated Power Draw:\s*(\d+)", raw_text).group(1))
            except: power_val = 450
            
            try: msrp_val = int(re.search(r"GPU MSRP:\s*(\d+)", raw_text).group(1))
            except: msrp_val = 800
            
            try: current_val = int(re.search(r"GPU Current Price:\s*(\d+)", raw_text).group(1))
            except: current_val = 850

            new_record = {
                "prompt": user_input,
                "title": report_title,
                "power": power_val,
                "bottleneck": bottleneck_val,
                "msrp": msrp_val,
                "current": current_val,
                "report": raw_text
            }
            st.session_state.diagnostic_history.append(new_record)
            st.session_state.current_run = new_record
            
            st.rerun()

# ==========================================
# 6. RENDER THE ACTIVE DASHBOARD
# ==========================================
if st.session_state.current_run:
    run = st.session_state.current_run
    
    st.markdown("---")
    
    st.header(f"🖥️ {run['title']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("System Bottleneck")
        render_bottleneck_gauge(run['bottleneck'])
        st.metric(label="Calculated Power Draw", value=f"{run['power']}W", delta="Check PSU Limits", delta_color="off")
        
    with col2:
        st.subheader("Market Price Fluctuation")
        render_price_fluctuation_chart(run['msrp'], run['current'])
    
    st.markdown("### Agent Diagnostic Report")
    st.markdown(run['report'])

    st.download_button(
        label="📥 Download Diagnostic Report",
        data=run['report'],
        file_name=f"VANGUARD_Diagnostic_{run['prompt'][:10]}.txt",
        mime="text/plain",
        type="primary"
    )