from transformers import AutoTokenizer, AutoModelForCausalLM
from config import MODEL_CONFIG,PROPMPTS
from openai import OpenAI

# class LlamaModel:
#     def __init__(self):
#         self.model = None
#         self.tokenizer = None
#         self.load_model()

#     def load_model(self):
#         """加载Llama模型和分词器"""
#         model_path = MODEL_CONFIG['model_path']
#         tokenizer_path = MODEL_CONFIG['tokenizer_path']
#         self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
#         self.model = AutoModelForCausalLM.from_pretrained(model_path)
#         print(f"模型 {MODEL_CONFIG['model_name']} 加载成功！")

#     def generate_reply(self, prompt: str) -> str:
#         """根据提示生成自动回复文本"""
#         pre_prompt = ""
#         for propmt in PROPMPTS:
#             pre_prompt += propmt
#         # 将提示词与用户输入拼接
#         full_prompt = f"{pre_prompt} {prompt}"
#         inputs = self.tokenizer(prompt, return_tensors="pt", max_length=MODEL_CONFIG['max_length'], truncation=True)
#         outputs = self.model.generate(**inputs, max_length=MODEL_CONFIG['max_length'], temperature=MODEL_CONFIG['temperature'])
#         reply = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
#         return reply

class GPTModel:
    def __init__(self, model_name,pre_prompt):
        self.model_name = model_name
        self.client = OpenAI()
        self.pre_prompt = pre_prompt

    def generate_reply(self, prompt):
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.pre_prompt},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return completion.choices[0].message.content

reader_model = GPTModel(model_name="gpt-3.5-turbo",pre_prompt=PROPMPTS["reader"])
writer_model = GPTModel(model_name="gpt-4o",pre_prompt=PROPMPTS["writer"])
checker_mddel= GPTModel(model_name="gpt-3.5-turbo",pre_prompt=PROPMPTS['checker'])