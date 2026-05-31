# ⚡ V.A.N.G.U.A.R.D. Hardware AI
**Virtual Assistant for Next-Gen Upgrades And Rig Diagnostics**

## Project Overview
V.A.N.G.U.A.R.D. is an autonomous, multi-agent AI system designed to automate PC hardware compatibility analysis, power constraint calculation, and bottleneck detection. Built as a final project for ANLYTC4.

## System Architecture & Libraries
This project utilizes a sequential agent architecture to process user requests, scour the live web, and render diagnostic telemetry.

```mermaid
graph TD
    %% Flowchart Nodes
    Start([🚀 Start Diagnostic])
    
    A[🧑‍💻 User Input - Streamlit UI]
    
    subgraph Multi-Agent System
        B(🤖 CrewAI Orchestrator)
        C{🕵️ Agent 1: Scout}
        E{👨‍💼 Agent 2: Consultant}
    end
    
    D[🌐 Serper Dev API - Live Web Scraping]
    F[🧠 LLM Engine - Gemini 2.5 & Groq Llama 3]
    
    G[⚙️ Regex Extractor - Math Parsing]
    
    subgraph Dashboard Output
        H[📊 Plotly Gauges & Charts]
        I[🗂️ Session Memory Recents]
        J[📥 Downloadable TXT Report]
    end
    
    Finish([✅ End Process])

    %% Routing / Connections
    Start --> A
    A -->|Target Workload, Budget, Hardware| B
    B -->|Assigns Data Gathering| C
    C <-->|Searches real-time benchmarks| D
    C -->|Passes raw web data| E
    E <-->|Performs math & logic| F
    E -->|Generates 4-Part Report| G
    G -->|Routes specific integers| H
    G -->|Saves state| I
    G -->|Formats Markdown| J
    
    H --> Finish
    I --> Finish
    J --> Finish

    %% Define Styles (Safe Method)
    classDef userNode fill:#2b3035,stroke:#4caf50,stroke-width:2px,color:#fff
    classDef agentNode fill:#1e1e1e,stroke:#2196f3,stroke-width:2px,color:#fff
    classDef apiNode fill:#333333,stroke:#ff9800,stroke-width:2px,color:#fff
    classDef uiNode fill:#2b3035,stroke:#9c27b0,stroke-width:2px,color:#fff
    classDef terminalNode fill:#d32f2f,stroke:#ff5252,stroke-width:2px,color:#fff

    %% Apply Styles (Safe Method)
    class A userNode
    class B,C,E agentNode
    class D,F apiNode
    class G,H,I,J uiNode
    class Start,Finish terminalNode