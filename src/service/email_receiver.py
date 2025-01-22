import imaplib
from email.parser import BytesParser
from email import policy
import os

class EmailReceiver:
    def __init__(self, server, port, username, password):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.saved_emails = []

    def connect(self):
        """连接到IMAP服务器"""
        try:
            self.connection = imaplib.IMAP4_SSL(self.server, self.port)
            print(f"Connected to IMAP server {self.server}")
            print(f"Logging in as {self.username}...")
            print(f"Logging in with password: {self.password}...")
            self.connection.login(self.username, self.password)
            self.connection.select("inbox", readonly=True)
        except Exception as e:
            raise Exception(f"Error connecting to IMAP server: {e}")

    def fetch_email_by_id(self, email_id):
        """通过邮件ID获取邮件内容"""
        try:
            if self.connection is None:
                raise Exception("Not connected to the server.")
            status, data = self.connection.fetch(email_id, "(RFC822)")
            if status != "OK":
                raise Exception(f"Failed to fetch email ID {email_id}")
            if data is None or data[0] is None:
                raise Exception(f"Failed to fetch email ID {email_id}, no data returned.")
            raw_email = data[0][1]
            email_message = BytesParser().parsebytes(raw_email if isinstance(raw_email, (bytes, bytearray)) else bytes())
            return email_message
        except Exception as e:
            print(f"Error fetching email ID {email_id}: {e}")
            return None

    def save_email(self, email_message, directory):
        """保存邮件到指定目录"""
        try:
            email_id = email_message["Message-ID"]
            if not os.path.exists(directory):
                os.makedirs(directory)
            email_path = os.path.join(directory, f"{email_id}.eml")
            with open(email_path, "wb") as f:
                f.write(email_message.as_bytes())
            self.saved_emails.append(email_id)
            print(f"Email {email_id} saved to {email_path}")
        except Exception as e:
            print(f"Error saving email: {e}")

    def fetch_all_emails(self):
        """获取所有邮件ID"""
        try:
            if self.connection is None:
                raise Exception("Not connected to the server.")
            status, email_ids = self.connection.search(None, "ALL")
            if status != "OK":
                raise Exception("Failed to fetch emails.")
            return email_ids[0].split()
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []

    def handle_email(self, email_message, directory):
        """处理邮件，只保存原始邮件"""
        # 检查邮件是否是回复邮件
        if "In-Reply-To" in email_message or "References" in email_message:
            print(f"Skipping reply email: {email_message['Message-ID']}")
            return  # 是回复邮件，跳过

        # 检查邮件是否是自己发送的
        if email_message["From"] == self.username:
            print(f"Skipping sent email: {email_message['Message-ID']}")
            return  # 是自己发的邮件，跳过

        # 保存邮件
        self.save_email(email_message, directory)

    def disconnect(self):
        """断开连接"""
        if self.connection is not None:
            self.connection.logout()
            self.connection = None