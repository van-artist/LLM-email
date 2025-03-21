import mailparser
import base64
import quopri
from bs4 import BeautifulSoup
import json
from email.header import decode_header

def decode_base64(content, charset='utf-8'):
    """解码 base64 编码的内容"""
    try:
        return base64.b64decode(content).decode(charset, errors='ignore')
    except Exception:
        return content

def decode_quoted_printable(content, charset='utf-8'):
    """解码 quoted-printable 编码的内容"""
    try:
        return quopri.decodestring(content).decode(charset, errors='ignore')
    except Exception:
        return content

def decode_mime_words(s):
    """解码 MIME 编码的字符串（例如 =?UTF-8?B?...?=）"""
    if not s:
        return ""
    decoded_fragments = decode_header(s)
    return ''.join([
        (part.decode(charset or 'utf-8', errors='ignore') if isinstance(part, bytes) else part)
        for part, charset in decoded_fragments
    ])

def get_decoded_payload(part):
    """
    尝试使用 get_payload(decode=True) 获取已解码的字节内容，
    再根据 charset 解码为字符串，若失败则尝试 gbk，最后回退到 utf-8。
    """
    charset = part.get_content_charset() or 'utf-8'
    payload = part.get_payload(decode=True)
    if payload is None:
        return ""
    try:
        return payload.decode(charset, errors='ignore')
    except Exception:
        try:
            return payload.decode('gbk', errors='ignore')
        except Exception:
            return payload.decode('utf-8', errors='ignore')

def parse_eml_file(file_path):
    """完整解析 .eml 文件，确保提取正文、附件、并妥善处理内联资源"""
    try:
        mail = mailparser.parse_from_file(file_path)

        subject = decode_mime_words(mail.subject) if mail.subject else "No Subject"
        from_email = decode_mime_words(mail.from_[0][1]) if mail.from_ else "Unknown"
        to_email = decode_mime_words(mail.to[0][1]) if mail.to else "Unknown"
        date = str(mail.date) if mail.date else "Unknown Date"
        headers = mail.headers

        text_body = ""
        html_body = ""
        attachments = []

        if mail.message:
            for part in mail.message.walk():
                content_type = part.get_content_type()
                content_disposition = part.get("Content-Disposition", "") or ""
                content_id = part.get("Content-ID", "")
                filename = part.get_filename()

                # 内联图像或内嵌资源（例如：cid:xxx 引用），处理为附件，不放正文
                is_inline_attachment = (
                    "inline" in content_disposition.lower()
                    or content_id
                ) and filename and content_type.startswith("image/")

                # 真正的正文
                if content_type in ["text/plain", "text/html"] and not is_inline_attachment:
                    decoded_content = get_decoded_payload(part)
                    if content_type == "text/plain":
                        text_body += decoded_content.strip() + "\n"
                    elif content_type == "text/html":
                        html_body += decoded_content.strip() + "\n"
                    continue

                # 附件或内联资源（都保存到 attachments）
                if "attachment" in content_disposition.lower() or is_inline_attachment:
                    decoded_filename = decode_mime_words(filename) if filename else "unnamed"
                    payload = part.get_payload(decode=True)
                    mime_type = part.get_content_type()
                    attachments.append({
                        "filename": decoded_filename,
                        "size": len(payload) if payload else 0,
                        "mime_type": mime_type,
                        "disposition": content_disposition.strip() or "inline",
                        "is_inline": is_inline_attachment
                    })

        if not text_body and html_body:
            soup = BeautifulSoup(html_body, "html.parser")
            text_body = soup.get_text(separator="\n").strip()

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
    """存储解析后的邮件内容（包括完整邮件头部和详细附件信息）"""
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

            if email_data["attachments"]:
                f.write("Attachments:\n")
                for att in email_data["attachments"]:
                    f.write(
                        f"- {att['filename']} ({att['size']} bytes, {att['mime_type']}, disposition: {att['disposition']})\n"
                    )

        print(f"Parsed email saved to {output_path}")

    except Exception as e:
        print(f"Error saving email to {output_path}: {e}")



def extract_main_content(file_path, output_json_path):
    """
    提取邮件的主要内容：
      - subject: 邮件主题
      - from: 发送方
      - to: 接收方
      - text_body: 正文内容（优先 text/plain，fallback 到从 HTML 中提取纯文本）
      - attachments: 附件文件名列表
    然后以 JSON 格式保存到 output_json_path 中
    """
    email_data = parse_eml_file(file_path)
    if not email_data:
        print(f"解析 {file_path} 失败！")
        return

    main_content = {
        "subject": email_data.get("subject", ""),
        "from": email_data.get("from", ""),
        "to": email_data.get("to", ""),
        "text_body": email_data.get("text_body", ""),
        "attachments": [att["filename"] for att in email_data.get("attachments", [])]
    }
    
    try:
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(main_content, f, ensure_ascii=False, indent=2)
        print(f"提取结果已保存到 {output_json_path}")
    except Exception as e:
        print(f"保存 JSON 文件失败：{e}")