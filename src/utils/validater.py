from jsonschema import validate, ValidationError

# 定义 JSON schema
schema = {
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
                "interests": {"type": "array", "items": {"type": "string"}}
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
                "courses": {"type": "array", "items": {"type": "string"}}
            }
        },
        "reason_for_applying": {"type": "string"},
        "request": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "appreciation": {"type": "string"}
            }
        },
        "closing": {"type": "string"}
    },
    "required": ["subject", "sender", "application_intent", "background", "reason_for_applying", "request", "closing"]
}

# 验证 JSON 输出
def validate_json(output_json):
    try:
        validate(instance=output_json, schema=schema)
        return True
    except ValidationError as e:
        print("JSON格式不符合要求:", e)
        return False
