# ⚡ V.A.N.G.U.A.R.D. Hardware AI
**Virtual Assistant for Next-Gen Upgrades And Rig Diagnostics**

## Project Overview
V.A.N.G.U.A.R.D. is an autonomous, multi-agent AI system designed to automate PC hardware compatibility analysis, power constraint calculation, and bottleneck detection. Built as a final project for ANLYTC4.

## System Architecture & Libraries
This project utilizes a sequential agent architecture to process user requests, scour the live web, and render diagnostic telemetry.
* **Streamlit:** Powers the frontend dashboard and interactive UI.
* **CrewAI:** Orchestrates the multi-agent logic, assigning specific roles and sequential tasks to the AI agents.
* **Google Gemini 2.5 Flash (`crewai[google-genai]`):** Acts as the core reasoning LLM, chosen for its high-speed processing and advanced logic routing.
* **Serper API (`crewai-tools`):** Equips the Scout Agent with live Google Search capabilities to pull real-time benchmarks.
* **Plotly:** Renders the interactive "Bottleneck Severity" gauge chart based on metrics extracted via Python Regular Expressions (Regex).

## Setup Instructions

**1. Clone the repository**
Download the code to your local machine.

**2. Install Dependencies**
Ensure you have Python installed, then install the required libraries:
`pip install -r requirements.txt`

**3. Configure Environment Variables**
Create a `.streamlit` folder in the root directory of the project. Inside that folder, create a file named `secrets.toml` and add your API keys:
```toml
GEMINI_API_KEY = "your_google_api_key"
SERPER_API_KEY = "your_serper_api_key"