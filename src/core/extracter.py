import re
from .model import LlamaModel

def extract_info_from_email(email_content: str) -> dict:
    """
    使用 LlamaModel 从邮件中提取求学者的基本信息和问题。
    """
    # 初始化 Llama 模型
    model = LlamaModel()

    # 改进提示词，提供一个更明确的结构和格式
    prompt = f"""
    请从下面的邮件内容中提取出以下信息，并提供具体的值：
    1. 求学者的姓名，例如："张三"
    2. 求学者的邮箱地址，例如："zhangsan@example.com"
    3. 求学者的电话号码，例如："13912345678"
    4. 求学者要询问的问题，例如："想了解关于申请流程的信息"

    邮件内容: {email_content}
    
    请严格按照以下格式返回:
    姓名: [求学者的姓名]
    邮箱: [求学者的邮箱地址]
    电话: [求学者的电话号码]
    问题: [求学者的具体问题]
    """
    
    # 调用模型生成结果
    model_output = model.generate_reply(prompt)
    print("model_output", model_output)

    # 使用正则表达式提取模型生成的结果中的信息
    user_info = {
        "姓名": extract_field(model_output, "姓名"),
        "邮箱": extract_field(model_output, "邮箱"),
        "电话": extract_field(model_output, "电话"),
        "问题": extract_field(model_output, "问题")
    }
    
    return user_info

def extract_field(output: str, field: str) -> str:
    """
    从模型生成的文本中提取指定字段的值
    """
    pattern = rf"{field}: ([^\n]+)"  # 改进正则表达式以确保只提取指定字段后面的值
    match = re.search(pattern, output)
    return match.group(1).strip() if match else "未知"



