import os
import re
from dataclasses import asdict
from typing import Dict, Any
from typing_extensions import final
from config import DATA_DIR
from controller.schemas.student_email import StudentEmail
from controller.data_manager import student_email_data_client, student_data_client, reference_data_client , email_to_student
from controller.shared_pool import shared_message_pool
from models import writer_model, reader_model, checker_mddel

def read_email_from_file(file_path: str) -> str:
    """Reads the email content from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file: 
            print("Step 1: Email content successfully read from file.")
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        raise

def generate_reader_reply() -> str:
    """Generates a reader's reply based on the student's email."""
    print("Step 2: Generating reader's reply based on student email...")
    email = shared_message_pool.get('original_email')
    reply = reader_model.generate_reply(email)
    print("Step 2: Reader reply successfully generated.")
    return reply if reply is not None else ""

def process_student_email() -> Dict[str, Any]:
    """Processes the email into the student database and returns the student data."""
    print("Step 3: Processing student email and storing into database...")
    new_student = shared_message_pool.get('reader_reply')
    email_id = student_email_data_client.insert_from_json(new_student)
    email_dict = student_email_data_client.find(email_id)
    student_email = StudentEmail(**email_dict)
    student_dict = asdict(email_to_student(student_email))
    student_data_client.insert(student_dict)
    print("Step 3: Student email successfully processed and stored.")
    return student_dict


def generate_writer_reply(is_first_iteration: bool) -> str:
    """Generates a writer's reply based on the student's data and the checker's suggestions."""
    print("Step 4: Generating writer's reply based on student data and checker feedback...")
    
    student_data = shared_message_pool.get('student_data')
    checker_reply = shared_message_pool.get('checker_reply')
    reference = shared_message_pool.get('reference')

    # 处理第一次生成的回复
    if is_first_iteration:
        print("First iteration: Using student data and reference for reply generation.")
        # 如果是第一次生成，使用学生信息和参考信息
        pre_prompt = f"Reference: {reference}\nStudent Information: {student_data}\nChecker Feedback: {checker_reply}\n"
    else:
        print("Subsequent iteration: Using only checker feedback for reply generation.")
        # 后续迭代时，仅使用检查者反馈
        pre_prompt = f"Checker Feedback: {checker_reply}\n"

    print("-------------------")
    print("writer_model_pre_prompt:\n", pre_prompt)
    print("-------------------")
    
    # 使用生成器模型生成回复
    reply = writer_model.generate_reply(pre_prompt)
    print("Step 4: Writer's reply successfully generated.")
    
    return reply if reply is not None else ""


def generate_checker_reply() -> str:
    """Generates a checker's reply based on the writer's reply."""
    tmp_reply = shared_message_pool.get('tmp_reply')
    reference = shared_message_pool.get('reference')
    
    if not tmp_reply:
        print("Error: Writer's reply is missing or invalid.")
        return ""
    
    if reference is None:
        print("Warning: Reference data is missing, using default reference.")
        reference = "No reference data available."

    print("Step 5: Generating checker's reply based on writer's reply...")
    pre_prompt = f"Reference:{reference}\nWriter_reply:{tmp_reply}\n"
    
    print("-------------------")
    print("checker_model_pre_prompt:\n", pre_prompt)
    print("-------------------")
    
    checker_reply = checker_mddel.generate_reply(pre_prompt)
    
    if checker_reply is None:
        print("Error: No checker reply generated.")
        return ""
    
    print("Step 5: Checker reply successfully generated.")
    return checker_reply

def main():
    email_path = os.path.join(DATA_DIR, "mails/example.txt")
    max_iterations = 5
    iteration = 0
    reference = reference_data_client.find_all()

    # 在共享池中存入参考信息
    shared_message_pool.add('reference', reference)
    
    final_reply = ""
    print(reference)
    
    while iteration < max_iterations:
        try:
            iteration += 1
            print(f"--- Iteration {iteration} ---")

            # 读取邮件内容并存入共享池
            example_email = read_email_from_file(email_path)
            shared_message_pool.add('original_email', example_email)

            # 使用 Reader 模型生成回复
            reader_reply = generate_reader_reply()
            shared_message_pool.add('reader_reply', reader_reply)

            # 处理邮件并存入学生数据库
            student_data = process_student_email()
            shared_message_pool.add('student_data', student_data)

            # 使用 Writer 模型生成草稿，结合学生信息和检查者建议
            tmp_reply = generate_writer_reply(iteration == 1)
            shared_message_pool.add('tmp_reply', tmp_reply)
            print(f"Writer reply: {tmp_reply}")
            final_reply = tmp_reply

            # Step 5: 使用 Checker 模型检查最终草稿
            checker_reply = generate_checker_reply()
            shared_message_pool.add('checker_reply', checker_reply)
            print(f"Checker reply: {checker_reply}")

        except Exception as e:
            print(f"Error in processing: {e}")
            break

    print("Max iterations reached. Exiting...")

    # 将最终回复写入文件
    with open(os.path.join(DATA_DIR, "out.txt"), "w", encoding="utf-8") as file:
        file.write(final_reply)

if __name__ == "__main__":
    main()
