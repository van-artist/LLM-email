import os
import mailparser
import base64
import quopri
from bs4 import BeautifulSoup

def decode_text(content, encoding):
    """根据编码方式（Base64, Quoted-Printable, 8bit等）解码正文"""
    try:
        if encoding == "base64":
            return base64.b64decode(content).decode("utf-8", errors="ignore")
        elif encoding == "quoted-printable":
            return quopri.decodestring(content).decode("utf-8", errors="ignore")
        else:
            return content.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
    except:
        return content  # 解码失败，返回原始内容

def parse_eml_file(file_path):
    """完整解析 .eml 文件，确保提取所有正文和附件信息"""
    try:
        mail = mailparser.parse_from_file(file_path)

        # 获取邮件基本信息
        subject = mail.subject if mail.subject else "No Subject"
        from_email = mail.from_[0][1] if mail.from_ else "Unknown"
        to_email = mail.to[0][1] if mail.to else "Unknown"
        date = str(mail.date) if mail.date else "Unknown Date"

        # 获取邮件头部信息
        headers = mail.headers

        # 解析邮件正文
        text_body = ""
        html_body = ""

        for part in mail.message.walk():
            content_type = part.get_content_type()
            content_transfer_encoding = part.get("Content-Transfer-Encoding", "").lower()
            charset = part.get_content_charset() or "utf-8"  # 默认 utf-8
            content = part.get_payload()

            # 解码正文
            decoded_content = decode_text(content, content_transfer_encoding)

            if content_type == "text/plain":
                text_body += decoded_content.strip() + "\n"
            elif content_type == "text/html":
                html_body += decoded_content.strip() + "\n"

        # 如果 text_body 为空，则从 HTML 提取纯文本
        if not text_body and html_body:
            soup = BeautifulSoup(html_body, "html.parser")
            text_body = soup.get_text(separator="\n").strip()

        # 解析附件信息
        attachments = []
        for attachment in mail.attachments:
            if attachment["filename"]:
                attachments.append({
                    "filename": attachment["filename"],
                    "size": len(attachment["payload"]),  # 字节数
                    "mime_type": attachment["mail_content_type"]
                })

        return {
            "subject": subject,
            "from": from_email,
            "to": to_email,
            "date": date,
            "headers": headers,
            "text_body": text_body,
            "attachments": attachments
        }

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None


def save_parsed_email(email_data, output_path):
    """存储解析后的邮件内容（包括完整邮件头部和附件信息）"""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Subject: {email_data['subject']}\n")
            f.write(f"From: {email_data['from']}\n")
            f.write(f"To: {email_data['to']}\n")
            f.write(f"Date: {email_data['date']}\n\n")

            f.write("Headers:\n")
            for key, value in email_data["headers"].items():
                f.write(f"{key}: {value}\n")
            f.write("\n")

            f.write("Text Body:\n")
            f.write(email_data["text_body"] + "\n\n")

            # 记录附件信息（文件名、大小、MIME 类型）
            if email_data["attachments"]:
                f.write("Attachments:\n")
                for attachment in email_data["attachments"]:
                    f.write(f"- {attachment['filename']} ({attachment['size']} bytes, {attachment['mime_type']})\n")

        print(f"Parsed email saved to {output_path}")

    except Exception as e:
        print(f"Error saving email to {output_path}: {e}")