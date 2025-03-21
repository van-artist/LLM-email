import imaplib
import os
from email.parser import BytesParser
from email.header import decode_header
from email.policy import default

class EmailReceiver:
    def __init__(self, server, port, username, password, mailbox="INBOX"):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.mailbox = mailbox
        self.connection = None

    def connect(self):
        """连接到IMAP服务器，并选择指定邮箱"""
        try:
            self.connection = imaplib.IMAP4_SSL(self.server, self.port)
            print(f"Connected to IMAP server {self.server}")
            self.connection.login(self.username, self.password)
            self.connection.select(self.mailbox, readonly=True)
        except Exception as e:
            raise Exception(f"Error connecting to IMAP server: {e}")

    def fetch_email_raw(self, email_id):
        """
        通过邮件ID获取原始邮件内容（完整RFC822格式的二进制数据）
        """
        try:
            if self.connection is None:
                raise Exception("Not connected to the server.")
            status, data = self.connection.fetch(email_id, "(RFC822)")
            if status != "OK" or not data or not data[0]:
                raise Exception(f"Failed to fetch email ID {email_id}")
            raw_email = data[0][1]
            if not isinstance(raw_email, (bytes, bytearray)):
                raise Exception(f"Invalid email data type: {type(raw_email)}")
            return raw_email
        except Exception as e:
            print(f"Error fetching email ID {email_id}: {e}")
            return None

    def parse_email(self, raw_email):
        """将原始邮件数据解析为email.message.Message对象"""
        try:
            email_message = BytesParser(policy=default).parsebytes(raw_email)
            return email_message
        except Exception as e:
            print(f"Error parsing email: {e}")
            return None

    def decode_filename(self, filename):
        """解码附件文件名（支持RFC2047编码）"""
        try:
            decoded_parts = decode_header(filename)
            return "".join(
                part[0].decode(part[1] if part[1] else 'utf-8') if isinstance(part[0], bytes) else part[0]
                for part in decoded_parts
            )
        except Exception as e:
            print(f"Error decoding filename {filename}: {e}")
            return filename

    def save_email(self, email_id, save_dir, extract_attachments=True):
        """
        保存邮件到本地：
          - 以二进制形式保存原始.eml文件（保留完整邮件内容）
          - 如果extract_attachments为True，则解析邮件并提取附件到同一文件夹中
        :param email_id: 邮件ID
        :param save_dir: 保存目录
        :param extract_attachments: 是否提取附件
        """
        raw_email = self.fetch_email_raw(email_id)
        if raw_email is None:
            print(f"Skipping email ID {email_id} due to fetch error.")
            return

        email_message = self.parse_email(raw_email)

        # 构造保存目录（基于递增数字命名）
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        folder_number = len(os.listdir(save_dir)) + 1
        email_folder = os.path.join(save_dir, str(folder_number))
        os.makedirs(email_folder, exist_ok=True)

        # 保存原始完整.eml文件（二进制保存）
        email_file_path = os.path.join(email_folder, f"{folder_number}.eml")
        with open(email_file_path, "wb") as f:
            f.write(raw_email)
        print(f"Saved raw email to {email_file_path}")

        # 可选提取附件
        if extract_attachments and email_message is not None:
            for part in email_message.walk():
                content_disposition = part.get("Content-Disposition", "")
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        filename = self.decode_filename(filename)
                        attachment_data = part.get_payload(decode=True)
                        if attachment_data:
                            attachment_path = os.path.join(email_folder, filename)
                            with open(attachment_path, "wb") as af:
                                af.write(attachment_data)
                            print(f"Attachment '{filename}' saved to {attachment_path}")

    def fetch_all_email_ids(self):
        """获取所有邮件ID（返回ID列表）"""
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

    def disconnect(self):
        """断开IMAP服务器连接"""
        if self.connection is not None:
            self.connection.logout()
            self.connection = None

