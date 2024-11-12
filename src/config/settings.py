import os
from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, '../data')

# MODEL_NAME = "meta-llama/Llama-3.2-1B"
LENGTH_MAX_GENERATION = 50
NUM_RETURN_SEQUENCES = 1
MONGGODB_URL="mongodb://localhost:27017/"


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print(OPENAI_API_KEY)

# 模型相关配置
MODEL_CONFIG = {
    'model_name': 'meta-llama/Llama-3.2-3B',
    'model_path': 'meta-llama/Llama-3.2-3B',  
    'tokenizer_path': 'meta-llama/Llama-3.2-3B',  
    'max_length': 50,
    'temperature': 0.7,
    'repetition_penalty':1.2
}

PROPMPTS = {
    "reader":"""
            请提取求学邮件中的有用信息，并以如下的 JSON 格式输出，确保字段和结构保持一致：
            {
            "subject": "邮件主题",
            "sender": {
                "name": "发件人姓名",
                "university": "发件人学校",
                "degree": "发件人学历/年级",
                "email": "发件人邮箱"
            },
            "application_intent": {
                "program": "申请的专业或项目",
                "interests": ["兴趣领域1", "兴趣领域2", ...]
            },
            "background": {
                "projects": [
                {
                    "title": "项目名称",
                    "results": "项目成果"
                }
                ],
                "courses": ["课程1", "课程2", ...]
            },
            "reason_for_applying": "申请理由",
            "request": {
                "type": "请求类型（如建议或问题）",
                "appreciation": "感谢表达"
            },
            "closing": "结束语"
            }
            请按照上述结构生成 JSON 输出，不要包含额外的文本。
            """,

    "writer":"""
            基于以下提取的申请人信息[关键信息]，撰写一封正式的回复邮件。邮件内容应包括：
            - 对申请人提出的问题的回答，特别是关于申请流程或研究方向的建议。
            - 对申请人背景的认可，表达学校对其兴趣的欢迎。
            - 提供后续联系的途径，或邀请申请人参加相关活动。

            邮件应以招生办的口吻，语气礼貌、正式。
        """
}
