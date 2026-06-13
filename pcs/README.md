# Spear Phishing Awareness Simulator

Educational Flask app showing how synthetic public-profile exposure can make social-engineering messages more convincing.

The app uses only built-in demo profiles and simulated placeholder links. It does not scrape real accounts, send email, or perform attacks.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Optional Gemini LLM Mode

Template generation works without any API key. To enable Gemini generation, set an environment variable before starting Flask.

PowerShell:

```powershell
$env:GEMINI_API_KEY="your-api-key"
python app.py
```

Or create `pcs/.env`:

```text
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemini-2.5-flash
```

Then restart Flask:

```powershell
python app.py
```

Command Prompt:

```cmd
set GEMINI_API_KEY=your-api-key
python app.py
```

Linux/macOS:

```bash
export GEMINI_API_KEY="your-api-key"
python app.py
```

Optional model override:

```powershell
$env:GEMINI_MODEL="gemini-2.5-flash"
```

## Project Structure

```text
pcs/
  app.py
  simulator.py
  requirements.txt
  data/
    profiles.json
  static/
    script.js
    style.css
  templates/
    index.html
```
