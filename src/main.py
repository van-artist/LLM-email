import os
import re
from dataclasses import asdict
from config import DATA_DIR
from database.schemas.student_email import StudentEmail
from database.database import student_email_data_client, student_data_client, email_to_student
from core.model import writer_model, reader_model


def read_email_from_file(file_path: str) -> str:
    """Reads the email content from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        raise


def generate_email_reply(example_email: str) -> str:
    """Generates a reply to the email using the reader model."""
    reply = reader_model.generate_reply(example_email)
    # Remove markdown JSON syntax
    return re.sub(r"```json|```", "", reply).strip()


def process_student_email(email_json: str) -> int:
    """Processes the email into the student database."""
    email_id = student_email_data_client.insert_from_json(email_json)
    email_dict = student_email_data_client.find(email_id)
    student_email = StudentEmail(**email_dict)
    student_dict = asdict(email_to_student(student_email))
    return student_data_client.insert(student_dict)


def generate_writer_reply(student_data: str) -> str:
    """Generates a writer's reply based on the student's data."""
    return writer_model.generate_reply(student_data)


def main():
    email_path = os.path.join(DATA_DIR, "mails/example.txt")

    try:
        # Step 1: Read the email content
        example_email = read_email_from_file(email_path)

        # Step 2: Generate a reply from the reader model
        reader_reply = generate_email_reply(example_email)

        # Step 3: Process the email and insert student data
        new_student_id = process_student_email(reader_reply)
        print(f"New student ID: {new_student_id}")

        # Step 4: Retrieve student data and generate writer's reply
        student_data = student_data_client.find(new_student_id)
        writer_reply = generate_writer_reply(str(student_data))

        print(writer_reply)
    except Exception as e:
        print(f"Error in processing: {e}")


if __name__ == "__main__":
    main()
