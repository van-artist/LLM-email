import re
from pymongo import MongoClient
from config import MONGGODB_URL
from datetime import datetime

class MongoDBClient:
    def __init__(self, db_name: str, collection_name: str):
        self.client = MongoClient(MONGGODB_URL)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def validate_student_data(self, student_data: dict):
        """
        验证学生数据的约束。
        """
        # 验证姓名
        if 'name' not in student_data or not isinstance(student_data['name'], str) or len(student_data['name']) == 0:
            raise ValueError("学生姓名必须是非空字符串")

        # 验证邮箱格式
        if 'email' not in student_data or not re.match(r"[^@]+@[^@]+\.[^@]+", student_data['email']):
            raise ValueError("无效的电子邮件地址")

        # 验证电话号码（可选）
        if 'phone' in student_data and not re.match(r"^\+?\d{7,15}$", student_data['phone']):
            raise ValueError("无效的电话号码")

        # 验证学校
        if 'school' not in student_data or not isinstance(student_data['school'], str) or len(student_data['school']) == 0:
            raise ValueError("学校名称必须是非空字符串")

        # 验证本科专业
        if 'major' not in student_data or not isinstance(student_data['major'], str) or len(student_data['major']) == 0:
            raise ValueError("专业名称必须是非空字符串")

        # 验证申请的硕士课程/项目
        if 'intended_program' not in student_data or not isinstance(student_data['intended_program'], str) or len(student_data['intended_program']) == 0:
            raise ValueError("申请的硕士课程必须是非空字符串")

        # 验证需求类型
        if 'query_type' not in student_data or not isinstance(student_data['query_type'], str) or len(student_data['query_type']) == 0:
            raise ValueError("需求类型必须是非空字符串")

        # 验证疑问详情
        if 'query_details' not in student_data or not isinstance(student_data['query_details'], str) or len(student_data['query_details']) == 0:
            raise ValueError("疑问详情必须是非空字符串")

    def insert_student(self, student_data: dict):
        """
        向 'student' 集合插入一条学生信息记录。
        :param student_data: 学生数据字典
        :return: 插入记录的ID
        """
        # 插入之前验证数据
        self.validate_student_data(student_data)
        
        # 插入当前日期
        student_data['created_at'] = datetime.now()
        
        # 插入数据到集合
        result = self.collection.insert_one(student_data)
        return result.inserted_id

    def find_student(self, query: dict):
        """
        根据查询条件查找 'student' 集合中的学生记录。
        :param query: 查询条件
        :return: 查找到的学生记录
        """
        return self.collection.find_one(query)


