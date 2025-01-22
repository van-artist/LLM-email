import re
from email.parser import Parser
from email.header import decode_header
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup


def parse_email(file_path: str) -> dict:
    """
    从一个 .txt 文件中解析邮件，返回结构化内容，包括修复多行头部和多余的空行。
    """
    # 1) 读取原始文件并修复多行头部
    fixed_text = fix_multiline_headers(file_path)
    # print("Fixed text:", fixed_text)
    # 2) 用 Parser 解析修复后的邮件文本
    msg = Parser().parsestr(fixed_text)

    # 3) 解析各常见头部并解码
    subject = decode_mime_str(msg.get('Subject', ''))
    from_ = decode_mime_str(msg.get('From', ''))
    to_ = decode_mime_str(msg.get('To', ''))
    date_str = msg.get('Date', '')
    date_parsed = None
    print("subject:", subject)
    try:
        date_parsed = parsedate_to_datetime(date_str)
    except:
        pass

    # 4) 提取正文（若有）
    body_text = extract_body_text(msg)

    # 5) 返回结果
    return {
        "subject": subject,
        "from": from_,
        "to": to_,
        "date": date_parsed.isoformat() if date_parsed else date_str,
        "body": body_text.strip()
    }


def fix_multiline_headers(file_path: str) -> str:
    """
    读取原始邮件文件，对头部区域(遇到空行前)做修复。
    - 尽量跳过/合并头部区域内的“意外空行”，防止 Subject 等多行中断。
    - 如果判定空行确实是头部结束，则进入正文。
    - 合并多行头部（缺少前置空格的 continuation）。
    """

    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    fixed_lines: list[str] = []
    in_header = True

    # 用下标遍历，以便在检测到空行时可以查看“下一行”是否可能是头部延续。
    i = 0
    while i < len(lines):
        line = lines[i]

        if in_header:
            # 如果这行是空行或只含空白
            if not line.strip():
                # 可能是头部结束，也可能是意外的空行
                # 查看下一行，若下一行仍然看似头部行或 continuation，则跳过该空行
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if is_header_line(next_line) or is_continuation_line(next_line, fixed_lines):
                        # “意外空行”，跳过，不结束头部
                        i += 1
                        continue
                    else:
                        # 下一行也不是头部 => 这是真正的分隔行
                        fixed_lines.append(line)  # 保留这个空行，标记头部结束
                        in_header = False
                        i += 1
                        continue
                else:
                    # 已无下一行，算头部结束
                    fixed_lines.append(line)
                    in_header = False
                    i += 1
                    continue

            else:
                # 当前行非空，判断是新的头部行还是 continuation
                if is_header_line(line):
                    # 有效的新头部行 (例如 "Subject: ...", "From: ...")
                    fixed_lines.append(line)
                else:
                    # continuation (上一行是头部，则拼接)
                    if fixed_lines and ":" in fixed_lines[-1]:
                        # 拼接到上一行
                        fixed_lines[-1] = fixed_lines[-1].rstrip("\r\n") + " " + line.strip("\r\n")
                    else:
                        # 理论上极少出现，但万一上一行也不是头部，就只能新加一行
                        fixed_lines.append(line)
            i += 1
        else:
            # 已经进入正文区域，原样保留
            fixed_lines.append(line)
            i += 1

    return "".join(fixed_lines)


def is_header_line(line: str) -> bool:
    """
    判断当前行是否看起来是一个新的头部字段，比如:
      Subject: ...
      From: ...
      X-Custom-Header: ...
    满足条件: line 含冒号, 并且冒号前是 [A-Za-z0-9-]+
    """
    line_stripped = line.strip()
    if ":" not in line_stripped:
        return False
    # 用正则匹配是否类似 "Key: Value"
    return bool(re.match(r'^[A-Za-z0-9-]+:\s?.*', line_stripped))

def is_continuation_line(line: str, fixed_lines: list[str]) -> bool:
    """
    判断该行是否可视作上一头部的 continuation。
    即: 上一行已是头部字段，并且这行并没有新的冒号.
    """
    line_stripped = line.strip()
    if not fixed_lines:
        return False
    if ":" not in line_stripped:
        # 没有冒号 => 可能是 continuation
        # 但要确保上一行确实是头部
        last_line = fixed_lines[-1]
        return (":" in last_line)  # 上一行包含冒号 => 可被视作 continuation
    else:
        # 这行含有冒号 => 很可能是新的头部行，而不是 continuation
        return False

def decode_mime_str(raw_header: str) -> str:
    """
    使用 decode_header 对 MIME 编码字符串做解码，并且对错误的 Base64/QP 编码进行宽容处理。
    """
    if not raw_header:
        return ""
    try:
        parts = decode_header(raw_header)
    except Exception:
        return raw_header

    decoded_string = ""
    for part, enc in parts:
        if isinstance(part, bytes):
            if not enc:
                enc = 'ascii'
            try:
                decoded_string += part.decode(enc, errors='replace')
            except:
                decoded_string += part.decode('utf-8', errors='replace')
        else:
            decoded_string += part
    return decoded_string


def extract_body_text(msg) -> str:
    """
    提取邮件正文，支持多分段 MIME。
    """
    if msg.is_multipart():
        parts_text = []
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get('Content-Disposition', ''))

            if ctype in ['text/plain', 'text/html'] and 'attachment' not in disp.lower():
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or 'utf-8'
                    try:
                        text = payload.decode(charset, errors='replace')
                    except:
                        text = payload.decode('utf-8', errors='replace')

                    if ctype == 'text/html':
                        soup = BeautifulSoup(text, 'html.parser')
                        text = soup.get_text(separator='\n')
                    parts_text.append(text)
        return "\n".join(parts_text)
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            ctype = msg.get_content_type()
            charset = msg.get_content_charset() or 'utf-8'
            try:
                text = payload.decode(charset, errors='replace')
            except:
                text = payload.decode('utf-8', errors='replace')

            if ctype == 'text/html':
                soup = BeautifulSoup(text, 'html.parser')
                text = soup.get_text(separator='\n')
            return text
        else:
            return ""

