import re
from email.parser import Parser
from email.header import decode_header
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
import base64
from urllib.parse import unquote


def parse_email(file_path: str) -> dict:
    """
    从一个 .txt 文件中解析邮件，返回结构化内容，包括修复多行头部和多余的空行。
    """
    # 1) 读取原始文件并修复多行头部
    # fixed_text = fix_multiline_headers(file_path)
    content=""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    # 2) 用 Parser 解析修复后的邮件文本
    msg = Parser().parsestr(content)
    # print("msg: ", msg)
    # 3) 解析各常见头部并解码
    tmp_subject_str=msg.get('Subject', '')
    tmp_subject_str=tmp_subject_str.replace("\n", "").replace("\t", "")
    print("tmp_subject_str: ", tmp_subject_str)
    print("tmp_str: ", tmp_subject_str.replace("\n","").strip())
    subject = decode_mime_str(tmp_subject_str)
    print("subject: ", subject)
    from_ = decode_mime_str(msg.get('From', ''))
    to_ = decode_mime_str(msg.get('To', ''))
    date_str = msg.get('Date', '')
    date_parsed = None
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
    修复邮件头部，确保多行字段正确拼接，空行和空格处理符合规范。
    """
    head_lines = []
    fixed_lines = []
    subject_line_str=""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    
    exit=False
    for line in lines:
        if exit:
            break
        if "Date:" in line:
            exit=True
        head_lines.append(line)
    
    print("head_lines: ", head_lines)

    subject_lines_count=0

    for line in head_lines:
        if "From:" in line:
            break
        else :
            tmp_line = line.strip()
            subject_line_str+=tmp_line
        subject_lines_count+=1
    print("subject_line_str: ", subject_line_str)
    print("subject_lines_count: ", subject_lines_count)



            

    # 修复多余的空行
    fixed_lines = [line for line in fixed_lines if line]

    return "\n".join(fixed_lines)

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

def decode_mime_str(header_str: str) -> str:
    """
    强行解码不规范的 MIME 字段。支持 B (Base64) 和 Q (Quoted-Printable)。
    1) 首先拼接所有多行，并去掉行首空白 (例如 \t)。
    2) 根据 =?xxx?B? 或 =?xxx?Q? 拆分各个段，分别解码。
    3) 如果仍然失败，就原样返回。
    """
    if not header_str:
        return ""

    # 1) 先把换行符和制表符去掉，拼成一行
    fixed_str = re.sub(r'\s+', ' ', header_str).strip()

    # 2) 用正则把所有 MIME 段分割出来
    #    形如 =?charset?B?xxx?= 或 =?charset?Q?xxx?=
    pattern = re.compile(r'(\=\?[^\?]+\?[BQbq]\?[^\?]+\?\=)')
    segments = pattern.split(fixed_str)

    decoded_segments = []
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue

        if pattern.match(seg):
            # MIME 段 (=?charset?B?xxxx?= 或 =?charset?Q?xxxx?=)
            decoded = _decode_one_mime_segment(seg)
            decoded_segments.append(decoded)
        else:
            # 普通字符串
            decoded_segments.append(seg)

    return "".join(decoded_segments).strip()

def _decode_one_mime_segment(segment: str) -> str:
    """
    解码单个 MIME 段，支持 B / Q 编码。
    格式: =?charset?B?xxxx?= 或 =?charset?Q?xxxx?=
    """
    match = re.match(r'=\?([^?]+)\?([BQbq])\?([^?]+)\?=', segment, flags=re.IGNORECASE)
    if not match:
        return segment  # 不符合预期的就原样返回

    charset = match.group(1)
    encoding_flag = match.group(2).upper()  # B or Q
    encoded_data = match.group(3).strip()

    if encoding_flag == 'B':
        return _bruteforce_decode_b64(charset, encoded_data, segment)
    else:
        # Q 编码
        return _decode_qp(charset, encoded_data)

def _bruteforce_decode_b64(charset: str, b64_data: str, original_segment: str) -> str:
    """
    处理 B (Base64) 编码的尝试修复解码。
    """
    tries = [
        (b64_data, "原样"),
        (b64_data.replace('_', '/'), "下划线 -> /"),
        (b64_data.replace('_', '+'), "下划线 -> +"),
    ]
    for data_fix, desc in tries:
        fixed_data = _fix_base64_padding(data_fix)
        try:
            raw = base64.b64decode(fixed_data, validate=False)
            try:
                return raw.decode(charset, errors='replace')
            except:
                return raw.decode('utf-8', errors='replace')
        except:
            # 下一个尝试
            pass
    # 所有都失败
    return original_segment

def _decode_qp(charset: str, qp_data: str) -> str:
    """
    解码 Q (Quoted-Printable) 编码的字符串。
    注意: 在 Q 编码中, '_' 代表空格, 而 =xx 为十六进制转义。
    """
    # 先把 '_' 替换成 ' ' (空格)
    qp_data = qp_data.replace('_', ' ')
    # 把 =XX 转成相应字节
    # 可以借助 Python 标准库 quopri, 但这里我们用 urllib.parse.unquote_to_bytes
    # 需要先把每个 =xx 转换成 %xx
    qp_data = re.sub(r'=([0-9A-Fa-f]{2})', r'%\1', qp_data)
    raw = unquote(qp_data)
    try:
        return raw.encode('latin-1', errors='replace').decode(charset, errors='replace')
    except:
        # 若 charset 不行, 再试 utf-8
        return raw.encode('latin-1', errors='replace').decode('utf-8', errors='replace')

def _fix_base64_padding(b64_str: str) -> str:
    """
    若长度不是4的倍数，则补 '='
    """
    missing = len(b64_str) % 4
    if missing:
        b64_str += "=" * (4 - missing)
    return b64_str


def fix_base64_padding(header: str) -> str:
    """
    修复 Base64 编码部分的填充问题。
    """
    def fix_segment(segment: str) -> str:
        # 判断是否是 Base64 编码的部分
        if "?B?" in segment:
            base64_part = segment.split("?B?")[-1].split("?=")[0]
            # 补齐 Base64 编码的填充
            missing_padding = len(base64_part) % 4
            if missing_padding:  # 计算需要补充的填充字符数量
                base64_part += "=" * (4 - missing_padding)
            return segment.replace(segment.split("?B?")[-1].split("?=")[0], base64_part)
        return segment

    # 使用正则分割出 MIME 编码段落
    segments = re.split(r'(\=\?[^\?]+\?[BQ]\?[^\?]+\?\=)', header)
    return "".join(fix_segment(segment) for segment in segments if segment)


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

