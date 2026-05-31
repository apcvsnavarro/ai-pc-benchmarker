# ⚡ V.A.N.G.U.A.R.D. Hardware AI
**Virtual Assistant for Next-Gen Upgrades And Rig Diagnostics**

## Project Overview
V.A.N.G.U.A.R.D. is an autonomous, multi-agent AI system designed to automate PC hardware compatibility analysis, power constraint calculation, and bottleneck detection. Built as a final project for ANLYTC4.

## System Architecture & Libraries
This project utilizes a sequential agent architecture to process user requests, scour the live web, and render diagnostic telemetry.

```mermaid
graph TD
    %% Define Styles
    classDef user fill:#2b3035,stroke:#4caf50,stroke-width:2px,color:#fff
    classDef agent fill:#1e1e1e,stroke:#2196f3,stroke-width:2px,color:#fff
    classDef api fill:#333333,stroke:#ff9800,stroke-width:2px,color:#fff
    classDef ui fill:#2b3035,stroke:#9c27b0,stroke-width:2px,color:#fff

    %% Flowchart Nodes
    A[🧑‍💻 User Input<br/>Streamlit UI] ::: user
    
    subgraph Multi-Agent System
    B(🤖 CrewAI Orchestrator) ::: agent
    C{🕵️ Agent 1: Scout} ::: agent
    E{👨‍💼 Agent 2: Consultant} ::: agent
    end
    
    D[🌐 Serper Dev API<br/>Live Web Scraping] ::: api
    F[🧠 LLM Engine<br/>Gemini 2.5 / Groq Llama 3] ::: api
    
    G[⚙️ Regex Extractor<br/>Math Parsing] ::: ui
    
    subgraph Dashboard Output
    H[📊 Plotly Gauges & Charts] ::: ui
    I[🗂️ Session Memory Recents] ::: ui
    J[📥 Downloadable TXT Report] ::: ui
    end

    %% Routing / Connections
    A -->|Target Workload, Budget, Hardware| B
    B -->|Assigns Data Gathering| C
    C <-->|Searches real-time benchmarks| D
    C -->|Passes raw web data| E
    E <-->|Performs math & logic| F
    E -->|Generates 4-Part Report| G
    G -->|Routes specific integers| H
    G -->|Saves state| I
    G -->|Formats Markdown| J