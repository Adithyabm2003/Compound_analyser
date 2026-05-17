# Clinical Compound Analyzer

## What is this?
This is an AI-powered assistant designed to look up and analyze pharmacological clinical trials. 

Instead of putting all the code in one messy script, this project uses a strict **two-part architecture**. It separates the AI's "brain" (the reasoning engine) from the "vault" (the actual clinical data). We do this using the **AWS Strands Framework** and the **Model Context Protocol (MCP)**.

This setup prevents the AI from hallucinating, keeps the data secure, and drastically reduces API token costs.

---

## The Core Architecture

### 1. The Brain: AWS Strands
Strands is the orchestrator. It manages the conversation and decides *when* and *how* to look up data. 
* **Smart Memory:** Instead of sending the entire chat history to the AI every single time (which drains your API quota instantly), Strands handles memory internally. We only feed it exactly what it needs for the current step.
* **Live Interception:** We use Strands' built-in "Hooks" (`BeforeToolCallEvent`, `AfterToolCallEvent`). This allows us to watch exactly what tools the AI is trying to use in real-time and display those traces to the user, without confusing the AI.
* **Strict Guardrails:** Strands is explicitly instructed to refuse medical diagnosis requests and to stop generating long, expensive "thinking" text. It gets the data and gives the answer. Period.

### 2. The Vault: Model Context Protocol (MCP)
MCP is the secure bridge to our local data. The AI does not have direct access to our database.
* **Total Isolation:** The data layer (`pharma_mcp.py`) runs as its own separate background process. 
* **Specific Rules:** The MCP server only allows the AI to use one specific tool: `get_compound_data`. 
* **How it helps:** When Strands realizes it needs data, it sends a formal request to the MCP server. MCP grabs the data from `clinical_db.json` and hands it back. Because the AI never touches the raw file, we can easily swap our simple JSON file for a massive cloud database later without changing any of the AI's code.

---

## How it Works (The Flow)

1. **You ask a question** (e.g., "What is the data on Compound-X9?").
2. **Strands thinks:** The agent realizes it doesn't know the answer off the top of its head.
3. **Strands asks MCP:** The agent sends a request over the secure bridge asking for "Compound-X9".
4. **MCP fetches data:** The MCP server checks `clinical_db.json` and sends the hard facts back to Strands.
5. **Strands answers:** The AI reads the facts, summarizes them cleanly, and shows you the result.

---

## Project Structure

* `app.py` — The main file. It runs the Strands agent, manages the chat, and displays the UI.
* `pharma_mcp.py` — The MCP server. This runs silently in the background and guards the data.
* `clinical_db.json` — The local database containing the compound facts.
* `.env` — Your private file for the API key.

---

## Setup & Run

**1. Add your API Key**
Create a `.env` file in the same folder and add your Gemini API key:

* `GEMINI_API_KEY=your_key_here`
---

## 2. Install Requirements
Install the necessary python packages:

* `pip install -r requirements.txt`

---

## 3. Start the App
Run the main file. (Note: You do not need to run the pharma_mcp.py file yourself. Strands is smart enough to start the MCP server automatically in the background).

* `streamlit run app.py`

  ---

  ## Thank you
