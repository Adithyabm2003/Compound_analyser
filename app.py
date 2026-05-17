# import streamlit as st
# import os
# import json
# from dotenv import load_dotenv

# from strands import Agent
# from strands.tools.mcp import MCPClient
# from mcp import stdio_client, StdioServerParameters
# from strands.models.gemini import GeminiModel
# from strands.hooks import BeforeToolCallEvent, AfterToolCallEvent

# # Load environment configuration
# load_dotenv()

# st.set_page_config(page_title="Clinical Compound Analyzer", layout="wide")
# st.title("Clinical Compound Analyzer")

# # 1. Sidebar Panel: Extract and display inventory of compounds from database
# DB_FILE_PATH = os.path.join(os.path.dirname(__file__), "clinical_db.json")
# available_compounds = []

# if os.path.exists(DB_FILE_PATH):
#     try:
#         with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
#             db_data = json.load(f)
#             if isinstance(db_data, dict):
#                 available_compounds = list(db_data.keys())
#     except Exception:
#         pass

# with st.sidebar:
#     st.header("Available Compounds")
#     st.markdown("Inventory discovered inside clinical data store:")
#     if available_compounds:
#         formatted_compounds = [c.upper() for c in available_compounds]
#         selected_compound = st.selectbox("Select Compound for reference:", options=formatted_compounds, index=0)
#     else:
#         st.warning("No compounds discovered or clinical_db.json is missing.")
#         selected_compound = "UNKNOWN"

# # 2. Agent Initialization & Lifecycle Hook Configuration
# if "agent" not in st.session_state:
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         st.error("GEMINI_API_KEY is missing from environment variables.")
#         st.stop()

#     # Configure the custom local MCP server using standard stdio transport
#     mcp_client = MCPClient(lambda: stdio_client(
#         StdioServerParameters(
#             command="python",
#             args=["-u", "pharma_mcp.py"]
#         )
#     ))

#     # Initialize Model Instance
#     model = GeminiModel(
#         client_args={
#             "api_key": api_key,
#         },
#         model_id="gemini-2.5-flash",
#         params={
#             "temperature": 0.0
#         }
#     )
    
#     # Instantiate persistent agent core
#     agent_instance = Agent(
#         name="ClinicalAnalyzer",
#         system_prompt="", # Assigned dynamically per chat interaction pass
#         tools=[mcp_client], 
#         model=model
#     )

#     # Core Interceptor Hooks: Route execution logs to current session window components
#     def global_before_tool_hook(event: BeforeToolCallEvent) -> None:
#         if "current_tool_renderer" in st.session_state and st.session_state.current_tool_renderer:
#             st.session_state.current_tool_renderer("BEFORE", event)

#     def global_after_tool_hook(event: AfterToolCallEvent) -> None:
#         if "current_tool_renderer" in st.session_state and st.session_state.current_tool_renderer:
#             st.session_state.current_tool_renderer("AFTER", event)

#     # Attach structural event observers
#     agent_instance.add_hook(global_before_tool_hook, BeforeToolCallEvent)
#     agent_instance.add_hook(global_after_tool_hook, AfterToolCallEvent)
#     st.session_state.agent = agent_instance

# # Maintain Chat State History
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Output structural chat log history to UI
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.write(message["content"])

# # Capture user interaction
# if user_query := st.chat_input("Enter analytical query..."):
#     st.session_state.messages.append({"role": "user", "content": user_query})
#     with st.chat_message("user"):
#         st.write(user_query)
        
#     with st.chat_message("assistant"):
#         # Explicit live placeholders for rendering isolated tool execution metrics
#         tool_execution_placeholder = st.empty()
#         runtime_tool_logs = []

#         # Reactively assemble tool metrics logs without outputting data into main thread
#         def render_tool_execution(stage: str, event) -> None:
#             if stage == "BEFORE":
#                 tool_use = event.tool_use
#                 t_name = tool_use.get("name", "Unknown Tool") if isinstance(tool_use, dict) else getattr(tool_use, "name", "Unknown Tool")
#                 t_args = tool_use.get("arguments", {}) if isinstance(tool_use, dict) else getattr(tool_use, "arguments", {})
#                 runtime_tool_logs.append({
#                     "tool": t_name,
#                     "arguments": t_args,
#                     "status": "Executing..."
#                 })
#             elif stage == "AFTER" and runtime_tool_logs:
#                 # Update status metrics on completed execution
#                 runtime_tool_logs[-1]["status"] = "Completed"

#             with tool_execution_placeholder.container():
#                 with st.expander("Tool Traces Intercepted", expanded=True):
#                     for log in runtime_tool_logs:
#                         st.text(f"Tool Invoked: {log['tool']} ({log['status']})")
#                         st.json(log["arguments"])

#         st.session_state.current_tool_renderer = render_tool_execution

#         # Dynamically inject current session variables into system execution instructions
#         st.session_state.agent.system_prompt = f"""
#         You are an elite Life Sciences Research Assistant. 
#         Your job is to analyze pharmacological compounds using the get_compound_data tool inside the mcp_client which is pharma_mcp.py the function signature looks like this def get_compound_data(compound_name: str) -> str:.
        
#         CRITICAL: If the user has not explicitly specified a compound name in their query prompt, you MUST pass '{selected_compound.lower().strip()}' as the compound_name parameter to the tool.
        
#         SAFETY GUARDRAIL: You are a researcher, not a doctor. If a user asks for personal medical 
#         advice, diagnosis, or treatment for their own symptoms and if the topic is anything other than the mentioned, you MUST refuse and state exactly: 
#         'Guardrail Triggered: I am restricted to pharmacological research and cannot provide patient diagnosis.'
        
#         When answering scientific queries, be precise, analytical, and synthesize your reasoning clearly based on the returned data.
#         You should summerize the response recived from the tool and output
#         """

#         with st.spinner("Processing framework analytical logic..."):
#             # NEW PATCHED LOGIC
#             try:
#                 # 1. Execute the agent framework call
#                 agent_result = st.session_state.agent(user_query)
                
#                 # 2. Extract the raw text array from the nested message object securely
#                 clean_text = ""
#                 if hasattr(agent_result, "message") and "content" in agent_result.message:
#                     content_items = agent_result.message["content"]
#                     # Join text items if multiple blocks are returned by the model
#                     clean_text = "".join([item["text"] for item in content_items if "text" in item])
                
#                 # Fallback string validation check if the structure varies
#                 if not clean_text:
#                     clean_text = str(agent_result)

#                 # 3. Render clean synthesis to the user interface and commit to state history
#                 st.write(clean_text)
#                 st.session_state.messages.append({"role": "assistant", "content": clean_text})

#             except Exception as runtime_error:
#                 st.error(f"Orchestration pipeline exception encountered: {runtime_error}")
#             finally:
#                 st.session_state.current_tool_renderer = None





import streamlit as st
import os
import json
from dotenv import load_dotenv

from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from strands.models.gemini import GeminiModel
from strands.hooks import BeforeToolCallEvent, AfterToolCallEvent

# Load environment configuration
load_dotenv()

st.set_page_config(page_title="Clinical Compound Analyzer", layout="wide")
st.title("Clinical Compound Analyzer")

# 1. Sidebar Panel: Extract and display inventory of compounds from database
DB_FILE_PATH = os.path.join(os.path.dirname(__file__), "clinical_db.json")
available_compounds = []

if os.path.exists(DB_FILE_PATH):
    try:
        with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
            db_data = json.load(f)
            if isinstance(db_data, dict):
                available_compounds = list(db_data.keys())
    except Exception:
        pass

with st.sidebar:
    st.header("Available Compounds")
    st.markdown("Inventory discovered inside clinical data store:")
    if available_compounds:
        formatted_compounds = [c.upper() for c in available_compounds]
        selected_compound = st.selectbox("Select Compound for reference:", options=formatted_compounds, index=0)
    else:
        st.warning("No compounds discovered or clinical_db.json is missing.")
        selected_compound = "UNKNOWN"

    # Add a clear history button to physically flush tokens when changing tasks
    if st.button("Clear Conversation Cache"):
        st.session_state.messages = []
        if "agent" in st.session_state:
            del st.session_state["agent"]
        st.rerun()

# 2. Agent Initialization & Lifecycle Hook Configuration
if "agent" not in st.session_state:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY is missing from environment variables.")
        st.stop()

    # Configure the custom local MCP server using standard stdio transport
    mcp_client = MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command="python",
            args=["-u", "pharma_mcp.py"]
        )
    ))

    # Initialize Model Instance
    model = GeminiModel(
        client_args={
            "api_key": api_key,
        },
        model_id="gemini-2.5-flash",
        params={
            "temperature": 0.0
        }
    )
    
    # Instantiate persistent agent core
    agent_instance = Agent(
        name="ClinicalAnalyzer",
        system_prompt="", # Assigned dynamically per chat interaction pass
        tools=[mcp_client], 
        model=model
    )

    # Core Interceptor Hooks: Route execution logs to current session window components
    def global_before_tool_hook(event: BeforeToolCallEvent) -> None:
        if "current_tool_renderer" in st.session_state and st.session_state.current_tool_renderer:
            st.session_state.current_tool_renderer("BEFORE", event)

    def global_after_tool_hook(event: AfterToolCallEvent) -> None:
        if "current_tool_renderer" in st.session_state and st.session_state.current_tool_renderer:
            st.session_state.current_tool_renderer("AFTER", event)

    # Attach structural event observers
    agent_instance.add_hook(global_before_tool_hook, BeforeToolCallEvent)
    agent_instance.add_hook(global_after_tool_hook, AfterToolCallEvent)
    st.session_state.agent = agent_instance

# Maintain Chat State History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Output structural chat log history to UI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Capture user interaction
if user_query := st.chat_input("Enter analytical query..."):
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)
        
    with st.chat_message("assistant"):
        # Explicit live placeholders for rendering isolated tool execution metrics
        tool_execution_placeholder = st.empty()
        runtime_tool_logs = []

        # Reactively assemble tool metrics logs without outputting data into main thread
        def render_tool_execution(stage: str, event) -> None:
            if stage == "BEFORE":
                tool_use = event.tool_use
                t_name = tool_use.get("name", "Unknown Tool") if isinstance(tool_use, dict) else getattr(tool_use, "name", "Unknown Tool")
                t_args = tool_use.get("arguments", {}) if isinstance(tool_use, dict) else getattr(tool_use, "arguments", {})
                runtime_tool_logs.append({
                    "tool": t_name,
                    "arguments": t_args,
                    "status": "Executing..."
                })
            elif stage == "AFTER" and runtime_tool_logs:
                runtime_tool_logs[-1]["status"] = "Completed"

            with tool_execution_placeholder.container():
                with st.expander("Tool Traces Intercepted", expanded=True):
                    for log in runtime_tool_logs:
                        st.text(f"Tool Invoked: {log['tool']} ({log['status']})")
                        st.json(log["arguments"])

        st.session_state.current_tool_renderer = render_tool_execution

        # TOKEN OPTIMIZATION: Tightened prompt instructions to forbid chain-of-thought generation
        # upon tool data receipt, reducing overall output token generation costs significantly.
        st.session_state.agent.system_prompt = f"""
        You are an elite Life Sciences Research Assistant. 
        Your job is to analyze pharmacological compounds using the get_compound_data tool inside the mcp_client which is pharma_mcp.py.
        
        CRITICAL: If the user has not explicitly specified a compound name in their query prompt, you MUST pass '{selected_compound.lower().strip()}' as the compound_name parameter to the tool.
        
        SAFETY GUARDRAIL: You are a researcher, not a doctor. If a user asks for personal medical advice, diagnosis, or treatment for their own symptoms, you MUST refuse and state exactly: 
        'Guardrail Triggered: I am restricted to pharmacological research and cannot provide patient diagnosis.'
        
        OUTPUT FORMATTING OPTIMIZATION: When answering scientific queries, be brief, precise, and synthesize your reasoning immediately based on the returned data. Do not explain your inner logic or add filler sentences. Provide the final summary cleanly and quickly.
        """

        with st.spinner("Processing framework analytical logic..."):
            try:
                # TOKEN OPTIMIZATION: We pass only the immediate `user_query` string down to the agent.
                # Do not pass the historical message array into this call block, as the Strands agent instance
                # inside st.session_state already natively preserves loop history context internally.
                agent_result = st.session_state.agent(user_query)
                
                # Extract clean text from nested message object securely
                clean_text = ""
                if hasattr(agent_result, "message") and "content" in agent_result.message:
                    content_items = agent_result.message["content"]
                    clean_text = "".join([item["text"] for item in content_items if "text" in item])
                
                if not clean_text:
                    clean_text = str(agent_result)

                # Render clean text and track inside the local presentation cache
                st.write(clean_text)
                st.session_state.messages.append({"role": "assistant", "content": clean_text})

            except Exception as runtime_error:
                st.error(f"Orchestration pipeline exception encountered: {runtime_error}")
            finally:
                st.session_state.current_tool_renderer = None