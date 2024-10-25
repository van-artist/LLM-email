from transformers import AutoTokenizer, AutoModelForCausalLM
from config import MODEL_CONFIG

class LlamaModel:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.load_model()

    def load_model(self):
        """加载Llama模型和分词器"""
        model_path = MODEL_CONFIG['model_path']
        tokenizer_path = MODEL_CONFIG['tokenizer_path']
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
        print(f"模型 {MODEL_CONFIG['model_name']} 加载成功！")

    def generate_reply(self, prompt: str) -> str:
        """根据提示生成自动回复文本"""
        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=MODEL_CONFIG['max_length'], truncation=True)
        outputs = self.model.generate(**inputs, max_length=MODEL_CONFIG['max_length'], temperature=MODEL_CONFIG['temperature'])
        reply = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return reply
