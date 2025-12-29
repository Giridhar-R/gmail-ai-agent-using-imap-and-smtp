"""Interactive Natural Language CLI for Gmail AI Agent"""

import sys
from .agent import GmailAIAgent


def print_header():
    """Print welcome header"""
    print("=" * 70)
    print("Gmail AI Agent - Conversational Mode".center(70))
    print("Talk to me in natural language!".center(70))
    print("=" * 70)


def print_welcome():
    """Print welcome message and examples"""
    print("\n Natural Language Mode - Just talk to me naturally!")
    print("\n Example queries you can ask:")
    print("  • Can you summarize my emails?")
    print("  • Show me unread messages")
    print("  • Find emails about the project")
    print("  • Get emails from john@example.com")
    print("  • How many emails did I receive today?")
    print("  • Send an email to friend@example.com about meeting")
    print("  • Create a draft to boss@company.com")
    print("\n Special commands:")
    print("  • 'help' - Show examples")
    print("  • 'quit' or 'exit' - Leave the chat")
    print()


def is_exit_command(text):
    """Check if user wants to exit"""
    exit_words = ['quit', 'exit', 'bye', 'goodbye', 'q']
    return text.lower().strip() in exit_words


def main():
    """Main CLI function with natural language support"""
    print_header()
    
    print("\n Initializing agent...")
    print("(First-time users: Make sure you've set up Gmail App Password)")
    
    try:
        agent = GmailAIAgent()
        print(" Agent initialized successfully!\n")
    except ValueError as e:
        print(f"\n Configuration Error: {e}")
        print("\n Please set up your .env file with:")
        print("  - GMAIL_EMAIL=your-email@gmail.com")
        print("  - GMAIL_APP_PASSWORD=your-16-char-password")
        print("  - OPENAI_API_KEY=your-openai-key")
        sys.exit(1)
    except Exception as e:
        print(f"\n Failed to initialize: {e}")
        sys.exit(1)
    
    print_welcome()
    
    # Conversation loop
    while True:
        try:
            # Get user input
            user_input = input("\n You: ").strip()
            
            if not user_input:
                continue
            
            # Check for exit
            if is_exit_command(user_input):
                print("\n Thanks for using Gmail AI Agent. Goodbye!")
                agent.close()
                break
            
            # Check for help
            if user_input.lower() == 'help':
                print_welcome()
                continue
            
            # Process with the agent (natural language)
            print("\n Agent: ", end="", flush=True)
            
            try:
                # The agent handles natural language directly
                response = agent.run(user_input)
                print(response)
            except Exception as e:
                print(f"\n Error processing your request: {e}")
                print("Please try rephrasing your question or type 'help' for examples.")
            
            print("\n" + "-" * 70)
        
        except KeyboardInterrupt:
            print("\n\n Goodbye!")
            agent.close()
            break
        except Exception as e:
            print(f"\n Unexpected error: {e}\n")


if __name__ == "__main__":
    main()
