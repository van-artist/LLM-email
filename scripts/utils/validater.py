#type:ignore
from jsonschema import validate, ValidationError

student_email_schema = {
    "type": "object",
    "properties": {
        "subject": {"type": "string"},
        "sender": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "university": {"type": "string"},
                "degree": {"type": "string"},
                "email": {"type": "string"}
            },
            "required": ["name", "university", "degree", "email"]
        },
        "application_intent": {
            "type": "object",
            "properties": {
                "program": {"type": "string"},
                "interests": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["program", "interests"]
        },
        "background": {
            "type": "object",
            "properties": {
                "projects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "results": {"type": "string"}
                        },
                        "required": ["title", "results"]
                    }
                },
                "courses": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["projects", "courses"]
        },
        "request": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "appreciation": {"type": "string"}
            },
            "required": ["type", "appreciation"]
        }
    },
    "required": ["subject", "sender", "application_intent", "background", "request"]
}


def validate_student_email(data):
    try:
        validate(instance=data, schema=student_email_schema)
        print("Validation successful!")
    except ValidationError as e:
        print(f"Validation error: {e.message}")
