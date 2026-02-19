# POET: Multilingual Poem Agents (LangGraph-style)

This small Python project demonstrates three agents collaborating to create a poem:
- `agent_marathi` writes lines in Marathi
- `agent_kannada` writes lines in Kannada
- `agent_translator` translates the entire poem to Hindi

The script uses a simple chat-completion HTTP client and targets the `sarvam-m` model for completion.

Prereqs
- Python 3.8+
- A Servam chat api key, (Register yourself and get it from https://www.sarvam.ai/)

Environment variables
- `SARVAM_API_URL` — URL for the chat completions endpoint (required)
- `SARVAM_API_KEY` — API key for authorization (required)

Using a .env file
 - Copy `.env.example` to `.env` and fill in your values.
 - The script will load `.env` located next to `agents.py` automatically.

Example `.env` (see `.env.example`):

```
SARVAM_API_BASE_URL=https://api.sarvam.ai/v1
SARVAM_API_KEY=sk-xxx
```

Install

```bash
pip install -r requirements.txt
```

Run

```bash
set SARVAM_API_BASE_URL=https://api.sarvam.ai/v1
set SARVAM_API_KEY=sk-xxx
python agents.py --topic "monsoon memories" --turns 6
```

You can also pass the topic using the Windows launchers:

PowerShell:

```powershell
.\launch_windows.ps1 --topic "monsoon memories"
```

Batch:

```cmd
run_agents.bat --topic "monsoon memories"
```

Outputs
- `outputs/poem_multilingual.txt` — the poem with language tags and the Hindi translation.

Demo
<video controls src="Demo.mp4" title="Demo"> Video Not found </video>


Notes
- The script expects the endpoint to follow an OpenAI-style chat completion schema (POST JSON with `model` and `messages`, returning `choices[0].message.content`). If your provider differs, update `agents.ChatClient.chat_completion` accordingly.

Windows launcher scripts
- Use `launch_windows.ps1` (PowerShell) or `run_agents.bat` (CMD) to create a local `.venv`, install dependencies from `requirements.txt`, and run the script.

PowerShell example:

```powershell
.\launch_windows.ps1
```

Batch example:

```cmd
run_agents.bat
```
