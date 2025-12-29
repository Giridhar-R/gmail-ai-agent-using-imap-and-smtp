"""IMAP and SMTP clients for Gmail access without Google Cloud Console"""

import imaplib
import smtplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
import re
import time
from bs4 import BeautifulSoup


class GmailIMAPClient:
    """Gmail IMAP client for reading emails"""
    
    def __init__(self, email_address: str, app_password: str):
        """
        Initialize Gmail IMAP client
        
        Args:
            email_address: Gmail email address
            app_password: Gmail App Password (16-character password)
        """
        self.email_address = email_address
        self.app_password = app_password
        self.imap = None
        self.connected = False
    
    def connect(self):
        """Connect to Gmail IMAP server"""
        try:
            self.imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
            self.imap.login(self.email_address, self.app_password)
            self.connected = True
            print(f"Connected to Gmail as {self.email_address}")
            return self
        except imaplib.IMAP4.error as e:
























              
               
                

                 
                  
                   
                    

                     
                      
                       
                        
                         
                          

                           
                            






                            
            raise ConnectionError(f"Failed to connect to Gmail: {str(e)}")
    
    def disconnect(self):
        """Disconnect from Gmail"""
        if self.imap and self.connected:
            try:
                self.imap.close()
                self.imap.logout()
                self.connected = False
            except:
                pass
    
    def _decode_header(self, header_value):
        """Decode email header"""
        if not header_value:
            return ""
        
        decoded_parts = decode_header(header_value)
        decoded_string = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    decoded_string += part.decode(encoding or "utf-8", errors="ignore")
                except:
                    decoded_string += part.decode("utf-8", errors="ignore")
            else:
                decoded_string += str(part)
        
        return decoded_string
    
    def _sanitize_email_content(self, content: str) -> str:
        """Remove potentially malicious instructions from email content"""
        
        # Remove HTML comments
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        # Remove hidden/suspicious patterns
        suspicious_patterns = [
            r'SYSTEM OVERRIDE',
            r'IGNORE.*PREVIOUS.*INSTRUCTIONS',
            r'NEW INSTRUCTION',
            r'IMPORTANT SYSTEM',
            r'SYSTEM CONTEXT UPDATE',
            r'CRITICAL SYSTEM',
            r'OVERRIDE:',
            r'REASONING OVERRIDE',
        ]
        
        for pattern in suspicious_patterns:
            content = re.sub(pattern, '[REMOVED_SUSPICIOUS_CONTENT]', 
                            content, flags=re.IGNORECASE)
        
        # Remove zero-width characters
        zero_width_chars = ['\u200b', '\u200c', '\u200d', '\ufeff']
        for char in zero_width_chars:
            content = content.replace(char, '')
        
        # Limit content length to prevent prompt stuffing
        max_length = 5000
        if len(content) > max_length:
            content = content[:max_length] + "\n[Content truncated for safety]"
        
        return content
    
    def _extract_email_body(self, msg):
        """Extract email body from message"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
                    except:
                        pass
                elif content_type == "text/html" and not body:
                    try:
                        html_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        # Convert HTML to plain text
                        soup = BeautifulSoup(html_body, "html.parser")
                        body = soup.get_text(separator="\n", strip=True)
                    except:
                        pass
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="ignore")
            except:
                body = str(msg.get_payload())
        
        # Clean up body
        body = re.sub(r'\n\s*\n', '\n\n', body)  # Remove excessive newlines
        return body.strip()
    
    def _parse_email(self, msg_data, uid) -> Dict:
        """Parse email message into dictionary"""
        msg = email.message_from_bytes(msg_data)
        
        # Extract headers
        subject = self._decode_header(msg.get("Subject", ""))
        from_header = self._decode_header(msg.get("From", ""))
        to_header = self._decode_header(msg.get("To", ""))
        date_header = msg.get("Date", "")
        
        # Parse date
        try:
            date_tuple = email.utils.parsedate_tz(date_header)
            if date_tuple:
                timestamp = email.utils.mktime_tz(date_tuple)
                date_obj = datetime.fromtimestamp(timestamp)
            else:
                date_obj = datetime.now()
        except:
            date_obj = datetime.now()
        
        # Extract body
        body = self._extract_email_body(msg)
        
        # Sanitize body content
        body = self._sanitize_email_content(body)
        
        return {
            "uid": uid,
            "from": from_header,
            "to": to_header,
            "subject": subject,
            "date": date_obj.strftime("%Y-%m-%d %H:%M:%S"),
            "body": body[:5000],  # Limit body size
        }
    
    def fetch_emails(self, folder: str = "INBOX", max_count: int = 10, 
                     search_criteria: str = "ALL") -> List[Dict]:
        """
        Fetch emails from specified folder
        
        Args:
            folder: Email folder (default: INBOX)
            max_count: Maximum number of emails to fetch
            search_criteria: IMAP search criteria (default: ALL)
        
        Returns:
            List of email dictionaries
        """
        if not self.connected:
            raise ConnectionError("Not connected to Gmail. Call connect() first.")
        
        try:
            # Select folder
            self.imap.select(folder, readonly=True)
            
            # Search for emails
            _, message_numbers = self.imap.search(None, search_criteria)
            
            if not message_numbers[0]:
                return []
            
            # Get message IDs (most recent first)
            msg_ids = message_numbers[0].split()
            msg_ids = msg_ids[-max_count:] if len(msg_ids) > max_count else msg_ids
            msg_ids = list(reversed(msg_ids))  # Most recent first
            
            emails = []
            for msg_id in msg_ids:
                try:
                    _, msg_data = self.imap.fetch(msg_id, "(RFC822)")
                    
                    if msg_data and msg_data[0]:
                        email_dict = self._parse_email(msg_data[0][1], msg_id.decode())
                        emails.append(email_dict)
                except Exception as e:
                    print(f"Warning: Failed to parse email {msg_id}: {e}")
                    continue
            
            return emails
        
        except Exception as e:
            raise Exception(f"Failed to fetch emails: {str(e)}")
    
    def fetch_unread_emails(self, max_count: int = 50) -> List[Dict]:
        """Fetch unread emails"""
        return self.fetch_emails(
            folder="INBOX",
            max_count=max_count,
            search_criteria="UNSEEN"
        )
    
    def search_emails(self, query: str, max_count: int = 20) -> List[Dict]:
        """
        Search emails by subject or body
        
        Args:
            query: Search query
            max_count: Maximum results
        
        Returns:
            List of matching emails
        """
        # IMAP search for subject or text
        search_criteria = f'OR SUBJECT "{query}" BODY "{query}"'
        return self.fetch_emails(
            folder="INBOX",
            max_count=max_count,
            search_criteria=search_criteria
        )
    
    def fetch_emails_from_sender(self, sender: str, max_count: int = 20) -> List[Dict]:
        """Fetch emails from specific sender"""
        search_criteria = f'FROM "{sender}"'
        return self.fetch_emails(
            folder="INBOX",
            max_count=max_count,
            search_criteria=search_criteria
        )
    
    def __enter__(self):
        """Context manager entry"""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


class GmailSMTPClient:
    """Gmail SMTP client for sending emails"""
    
    def __init__(self, email_address: str, app_password: str, imap_client=None):
        """
        Initialize Gmail SMTP client
        
        Args:
            email_address: Gmail email address
            app_password: Gmail App Password
            imap_client: Optional GmailIMAPClient for draft creation
        """
        self.email_address = email_address
        self.app_password = app_password
        self.imap_client = imap_client
        self.smtp = None
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        html: bool = False
    ) -> bool:
        """
        Send an email
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            cc: Optional list of CC recipients
            html: Whether body is HTML (default: plain text)
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            if html:
                msg = MIMEMultipart('alternative')
                msg.attach(MIMEText(body, 'html'))
            else:
                msg = MIMEText(body)
            
            msg['From'] = self.email_address
            msg['To'] = to
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
                recipients = [to] + cc
            else:
                recipients = [to]
            
            # Connect to SMTP server
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                smtp_server.login(self.email_address, self.app_password)
                smtp_server.sendmail(self.email_address, recipients, msg.as_string())
            
            print(f" Email sent to {to}")
            return True
            
        except Exception as e:
            print(f" Failed to send email: {e}")
            return False
    
    def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None
    ) -> bool:
        """
        Create a draft email (saves to Drafts folder via IMAP)
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            cc: Optional list of CC recipients
        
        Returns:
            True if draft created successfully
        """
        if not self.imap_client:
            print(" IMAP client not available for draft creation")
            return False
        
        try:
            # Create message
            from email.message import Message
            
            msg = Message()
            msg['From'] = self.email_address
            msg['To'] = to
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            msg.set_payload(body)
            utf8_message = str(msg).encode('utf-8')
            
            # Append to Drafts folder
            self.imap_client.imap.append(
                '[Gmail]/Drafts',
                '',
                imaplib.Time2Internaldate(time.time()),
                utf8_message
            )
            
            print(f" Draft created for {to}")
            return True
            
        except Exception as e:
            print(f" Failed to create draft: {e}")
            return False
