import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

email = os.getenv('GMAIL_EMAIL')
password = os.getenv('GMAIL_APP_PASSWORD')

print(f'Testing connection for: {email}')
print('Connecting to Gmail IMAP...')

try:
    imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    print('✓ Connected to server')
    
    imap.login(email, password)
    print('✓ Authentication successful!')
    
    status, folders = imap.list()
    print(f'✓ Found {len(folders)} folders')
    
    imap.select('INBOX')
    status, messages = imap.search(None, 'ALL')
    email_count = len(messages[0].split())
    print(f'✓ Inbox has {email_count} emails')
    
    imap.logout()
    print('\n All tests passed! IMAP is working correctly.')
    
except imaplib.IMAP4.error as e:
    print(f'\n Authentication failed: {e}')
    print('\nPossible issues:')
    print('1. Wrong email or app password in .env')
    print('2. App password has spaces (remove them)')
    print('3. Need to generate a new app password')
    
except Exception as e:
    print(f'\n Error: {e}')
