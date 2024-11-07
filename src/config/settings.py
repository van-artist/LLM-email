import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, '../data/mails')

# MODEL_NAME = "meta-llama/Llama-3.2-1B"
LENGTH_MAX_GENERATION = 50
NUM_RETURN_SEQUENCES = 1
OPENAIMODEL = "gpt-3.5-turbo"
MONGGODB_URL="mongodb://localhost:27017/"


# 模型相关配置
MODEL_CONFIG = {
    'model_name': 'meta-llama/Llama-3.2-3B',
    'model_path': 'meta-llama/Llama-3.2-3B',  
    'tokenizer_path': 'meta-llama/Llama-3.2-3B',  
    'max_length': 50,
    'temperature': 0.7,
    'repetition_penalty':1.2
}

PROPMPTS = [
    "使用一句话回答以下问题："
]