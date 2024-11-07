# Load model directly
from config.settings import BASE_DIR,DATA_DIR
from database.database import MongoDBClient
from core.model import LlamaModel


if __name__ == "__main__":
    model=LlamaModel()
    res=model.generate_reply("你好")
    print(res)
    with MongoDBClient('email-agent', 'student') as mongo_client:
        
        # 查询学生信息
        student_query = {"name": "李四"}
        student = mongo_client.find_student(student_query)
        print(f"查询到的学生信息: {student}")
