import os
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

# --- UI Setup ---
# This builds the visual front-end of your web app
st.set_page_config(page_title="AI PC Builder", page_icon="🖥️")
st.title("🖥️ AI Hardware Consultant")
st.write("Enter your desired PC components, and my AI agents will scour the internet for live benchmarks to generate a custom compatibility report.")

# Input fields for the user
api_key = st.text_input("Enter your Google Gemini API Key (starts with AIza...)", type="password")
user_query = st.text_area("What hardware do you want to test?", "RTX 4060 and Ryzen 5 5600 for 1080p 180Hz gaming")

# --- The App Logic ---
# This button triggers the AI when clicked
if st.button("Run Benchmarker"):
    if not api_key:
        st.error("Please enter your API key first!")
    else:
        # A loading spinner so the user knows the AI is thinking
        with st.spinner("Agents are scouring the web and reading reviews... This takes about 30-60 seconds."):
            
            # 1. Setup the Brain & Tools
            os.environ["GEMINI_API_KEY"] = api_key
            google_llm = LLM(model="gemini/gemini-2.5-flash")

            @tool("Web Search")
            def search_tool(query: str) -> str:
                """Search the internet for live PC benchmarks, Reddit threads, and hardware reviews."""
                return DuckDuckGoSearchRun().run(query)

            # 2. Define the Agents
            hardware_scout = Agent(
                role='Hardware Performance Analyst',
                goal='Search the web for live benchmarks, Reddit threads, and tech reviews to gather real-world performance data.',
                backstory='You are a senior PC hardware reviewer. You specialize in identifying thermal limits, GPU/CPU bottlenecks, and high-refresh-rate gaming metrics.',
                llm=google_llm,
                verbose=False, # Turned off verbose so it doesn't spam your terminal behind the scenes
                allow_delegation=False,
                tools=[search_tool]
            )

            consultant = Agent(
                role='Lead IT Hardware Consultant',
                goal='Analyze raw benchmark data and write professional, easy-to-read hardware compatibility reports.',
                backstory='You are trusted by gamers and professionals to give unbiased advice on whether a PC build will actually hit their target framerates without stuttering or bottlenecking.',
                llm=google_llm,
                verbose=False,
                allow_delegation=False
            )

            # 3. Define the Tasks (Using the user's custom input!)
            research_task = Task(
                description=f'Search for current benchmarks and user reviews testing the following hardware configuration: {user_query}.',
                expected_output='A detailed list of real-world framerates, potential bottleneck percentages, and noted performance issues.',
                agent=hardware_scout
            )

            report_task = Task(
                description='Using the gathered benchmarks, write a final compatibility report. Include sections for: 1. Target Performance, 2. Bottleneck Analysis, 3. Final Verdict (Is this a good buy?).',
                expected_output='A clean, professional 3-section Markdown report summarizing the viability of the build.',
                agent=consultant
            )

            # 4. Fire up the Crew
            pc_crew = Crew(
                agents=[hardware_scout, consultant],
                tasks=[research_task, report_task],
                process=Process.sequential
            )

            # Run the AI and store the final answer
            result = pc_crew.kickoff()

            # 5. Display the Results on the Web App!
            st.success("Report Generated Successfully!")
            st.markdown("---")
            st.markdown(str(result))