# LangChain Job Application Tracker

A conversational AI agent for tracking job applications, built with LangChain and Gemini.

## What it does
- Save job applications manually or by pasting a job description
- View, update, and delete applications
- Requires approval before deleting anything
- Blocks off-topic requests
- Streams responses in real time

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/willapat/langchain-job-tracker.git
cd langchain-job-tracker
```

**2. Make sure you have Python 3.11+**
```bash
python3 --version
```

**3. Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**4. Install dependencies**
```bash
pip install -r requirements.txt
```

**5. Set up your API keys**

Copy the example env file and fill in your keys:
```bash
cp .env.example .env
```

- **GOOGLE_API_KEY** — get it at [aistudio.google.com](https://aistudio.google.com/app/apikey)
- **LANGSMITH_API_KEY** — get it at [smith.langchain.com](https://smith.langchain.com)

## Run it

**Terminal chat:**
```bash
python3 main.py
```

**LangSmith Studio (visual interface):**
```bash
langgraph dev
```
Then open the URL it prints.
