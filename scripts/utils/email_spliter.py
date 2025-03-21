from __future__ import annotations
import re
import base64
import quopri
from bs4 import BeautifulSoup
from email.header import decode_header
from typing import List, Dict, Union, Optional, Any

# 定义邮件对话轮次类
class EmailTurn:
    def __init__(
        self,
        role: str,
        name: str,
        content: str,
        attachments: Optional[List[str]] = None
    ) -> None:
        self.role: str = role  # 发件人邮箱作为标识
        self.name: str = name  # 显示名称（目前与邮箱相同）
        self.content: str = content.strip() if content else ""
        self.attachments: List[str] = attachments if attachments is not None else []

    def to_dict(self) -> Dict[str, Union[str, List[str]]]:
        """将对象转换为字典，便于序列化保存"""
        return {
            "role": self.role,
            "name": self.name,
            "content": self.content,
            "attachments": self.attachments
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EmailTurn:
        """从字典创建 EmailTurn 实例（反序列化）"""
        return cls(
            role=data.get("role", ""),
            name=data.get("name", ""),
            content=data.get("content", ""),
            attachments=data.get("attachments", [])
        )

    def __repr__(self) -> str:
        return f"EmailTurn(role={self.role}, content_len={len(self.content)}, attachments={len(self.attachments)})"

# 编码处理函数
def decode_base64(content: str, charset: str = 'utf-8') -> str:
    """解码 base64 编码的内容"""
    try:
        return base64.b64decode(content).decode(charset, errors='ignore')
    except Exception:
        return content

def decode_quoted_printable(content: str, charset: str = 'utf-8') -> str:
    """解码 quoted-printable 编码的内容"""
    try:
        return quopri.decodestring(content).decode(charset, errors='ignore')
    except Exception:
        return content

def decode_mime_words(s: str) -> str:
    """解码 MIME 编码的字符串（例如 =?UTF-8?B?...?=）"""
    if not s:
        return ""
    decoded_fragments = decode_header(s)
    return ''.join([
        part.decode(charset or 'utf-8', errors='ignore') if isinstance(part, bytes) else part
        for part, charset in decoded_fragments
    ])

def get_decoded_payload(part: Any) -> str:
    """
    尝试使用 get_payload(decode=True) 获取已解码的字节内容，
    再根据 charset 解码为字符串，若失败则尝试 gbk，最后回退到 utf-8。
    """
    charset: str = part.get_content_charset() or 'utf-8'
    payload: Optional[bytes] = part.get_payload(decode=True)
    if payload is None:
        return ""
    try:
        return payload.decode(charset, errors='ignore')
    except Exception:
        try:
            return payload.decode('gbk', errors='ignore')
        except Exception:
            return payload.decode('utf-8', errors='ignore')

# 分割嵌套回复部分
def split_by_reply_markers(text: str) -> List[str]:
    """
    按嵌套的‘原始邮件’分隔符划分对话轮次，
    分隔符格式支持两边任意数量的 '-'，不区分大小写。
    """
    parts = re.split(r"-+\s*原始邮件\s*-+", text, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]

def extract_sender_from_block(block: str) -> Optional[str]:
    """
    尝试从块内查找“发件人:”或“From:”字段，提取邮箱地址
    示例匹配：发件人: 张三 <zhangsan@qq.com>
    """
    match = re.search(r"(?:发件人|From)\s*[:：]\s*(?:.*?<?([\w\.-]+@[\w\.-]+)>?)", block, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def extract_email_dialog(email_data: Dict[str, Any]) -> List[Dict[str, Union[str, List[str]]]]:
    """
    构造对话序列：
      - 每封邮件视为一次对话轮次，包含：role, name, content, attachments；
      - 如果正文中没有嵌套回复（即无“原始邮件”分隔符），直接返回一段内容；
      - 无论正文是否为空，只要有附件，都将附件名称作为属性保留在该轮对话中。
    """
    from_email: str = email_data.get("from", "未知发送人")
    to_email: str = email_data.get("to", "未知收件人")
    raw_text: str = email_data.get("text_body", "").strip()
    all_attachments: List[Union[Dict[str, str], str]] = email_data.get("attachments", [])

    def normalize_attachments(attachments: List[Union[Dict[str, str], str]]) -> List[str]:
        return [
            att["filename"] if isinstance(att, dict) and att.get("filename") else str(att)
            for att in attachments if att
        ]

    chunks: List[str] = split_by_reply_markers(raw_text)
    dialog: List[EmailTurn] = []

    if len(chunks) <= 1:
        content_text: str = raw_text
        if not content_text and all_attachments:
            attachment_names = normalize_attachments(all_attachments)
            content_text = "(附件: " + ", ".join(attachment_names) + ")"
        dialog.append(EmailTurn(from_email, from_email, content_text, normalize_attachments(all_attachments)))
    else:
        for i, chunk in enumerate(chunks):
            sender: Optional[str] = extract_sender_from_block(chunk)
            if not sender:
                sender = from_email if i == 0 else to_email
            dialog.append(EmailTurn(sender, sender, chunk, []))
        if dialog:
            dialog[0].attachments = normalize_attachments(all_attachments)

    return [turn.to_dict() for turn in dialog]
