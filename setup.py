from setuptools import setup, find_packages

setup(
    name="gmail-ai-agent-imap",
    version="0.2.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "langchain>=0.1.0",
        "langchain-openai>=0.0.5",
        "langchain-google-community>=0.0.1",
        "python-dotenv>=1.0.0",
        "beautifulsoup4>=4.12.0",
    ],
    python_requires=">=3.8",
    author="Your Name",
    description="AI agent for Gmail management with send/draft capabilities (no Google Cloud Console)",
    entry_points={
        "console_scripts": [
            "gmail-agent=gmail_agent.cli:main",
        ],
    },
)
