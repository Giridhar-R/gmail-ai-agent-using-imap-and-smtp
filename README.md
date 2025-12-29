# Gmail AI Agent 

An AI-powered CLI agent that manages your Gmail inbox using LangChain, OpenAI, and IMAP/SMTP.

## Features
-  **Read & Summarize:** Fetch recent emails and get AI summaries.
-  **Search:** Semantic search for specific emails.
-  **Send & Draft:** Compose and send emails using natural language.
-  **Secure:** Runs locally, uses App Passwords, and includes prompt injection defenses.

## Setup

1. **Clone the repo**
git clone https://github.com/your-username/gmail-ai-agent-imap.git

  cd gmail-ai-agent-imap



2. **Install Dependencies**
python -m venv venv

Windows :
venv\Scripts\activate

Mac/Linux :
source venv/bin/activate

pip install -r requirements.txt



3. **Configure Secrets**
Create a `.env` file in the root directory:

   GMAIL_EMAIL=your_email@gmail.com
   
   GMAIL_APP_PASSWORD=your_app_password
   
   OPENAI_API_KEY=sk-your_openai_key



5. **Run**
   
  python -m src.gmail_agent.cli

