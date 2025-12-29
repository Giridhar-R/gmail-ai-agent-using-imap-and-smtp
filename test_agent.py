from src.gmail_agent import GmailAIAgent

print('=' * 70)
print('Gmail AI Agent Test')
print('=' * 70)

print('\n Initializing agent...')
try:
    agent = GmailAIAgent()
    print(' Agent initialized successfully!\n')
    
    print(' Test 1: Summarizing 3 most recent emails...')
    print('-' * 70)
    result = agent.summarize_inbox(max_count=3)
    print(result)
    print('\n' + '=' * 70)
    
    agent.close()
    print('\n Test completed successfully!')
    
except Exception as e:
    print(f'\n Error: {e}')
    import traceback
    traceback.print_exc()
