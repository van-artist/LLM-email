import os

# MODEL_NAME = "meta-llama/Llama-3.2-1B"
LENGTH_MAX_GENERATION = 50
NUM_RETURN_SEQUENCES = 1
MONGGODB_URL="mongodb://localhost:27017/"


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
    "reader": """
            请根据以下的求学邮件内容提取关键信息，并以如下的 JSON 格式输出，确保字段和结构保持一致：
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
            **特别注意**：
            - 如果某些信息无法从邮件中提取，请填入 `null`。
            - 如果邮件中没有明确的求学请求，`request` 字段应标记为 `null`。
            - 如果邮件中未提到申请的背景或课程，也请填入 `null`。
            - 请确保提取的字段准确无误，并保持 JSON 格式的规范。
            - 保证数据字段的完整性，特别是 `sender`、`application_intent` 和 `request` 字段。
            """,

    "writer": """
            基于以下提取的申请人信息、纠错建议和参考信息，撰写一封正式的回复邮件。邮件内容应包括：
            
            1. **对申请人问题的解答**：请回答申请人在邮件中提出的任何问题，特别是关于申请流程、项目详情或研究方向的建议。参考任何相关的**纠错建议**，确保邮件中的回答准确无误。

            2. **对申请人背景的认可**：请对申请人的背景表示认可，提及相关项目和课程，并表达学校对其兴趣的欢迎。可以结合申请人的**学生信息**和**参考信息**，在适当的地方提及学校的优势。例如，您可以在回答申请人关于学校信息的问题时提到我们学校的学院名称、地址、官网等信息。

            3. **提供进一步联系信息**：请告知申请人下一步的申请流程、可能的面试、活动信息或如何保持联系。可以参考以下**参考信息**，包括学校的官网、地址等，帮助申请人更好地了解我们的学校及其流程。

            请注意：参考信息应当仅在必要时插入邮件正文中，不要将所有的参考信息一次性列出在邮件结尾。参考信息应当根据上下文合理分配，并使邮件保持简洁和专业。

            参考信息：
            - 学校名称：{学校名称}
            - 学校地址：{学校地址}
            - 学院名称：{学院名称}
            - 学校邮编：{学校邮编}
            - 学校网址：{学校网址}

            邮件应以招生办的口吻，语气礼貌、正式，且语言清晰、易于理解。确保邮件没有任何歧义或过于模糊的地方，回复要具体并具有帮助性。
        """,

        "checker": """
            你是一个邮件回复质量检查工具，请根据以下标准评估给定的邮件回复：

            1. **准确性**：回复内容是否准确地回答了邮件中的问题或请求？特别是关于申请流程、申请人背景以及学校的具体信息（如学校名称、地址、官网等）的回答。
            2. **清晰度**：回复是否清晰易懂，避免了模糊或歧义？确保语句简洁且逻辑清晰。特别是，参考信息是否在合适的地方使用，避免信息的冗余和重复。尤其要检查邮件末尾的冗余信息，如学校的地址、联系方式等，是否已经在邮件正文中提到过，避免不必要的重复。
            3. **礼貌性**：回复是否符合基本的礼貌规范，语气是否正式且友善？请检查是否有不必要的口语或过于简略的表达。
            4. **格式**：回复的格式是否规范，段落分明，语法正确，标点恰当？检查邮件中参考信息的插入方式，是否影响邮件格式的整洁性。特别注意避免参考信息在邮件结尾多次重复出现。
            5. **相关性**：回复是否与原邮件的内容相关，是否对邮件中的问题做出了有意义的回应？特别是参考信息的插入是否合理，是否有帮助于申请人了解学校的具体情况，避免冗余和无关信息的出现。

            请输出以下信息：
            {
                "accuracy": "评价回复是否准确回答了问题，特别是关于申请人背景和学校的详细信息。",
                "clarity": "评价回复的清晰度，是否简洁且逻辑清晰，是否避免了不必要的重复。",
                "politeness": "评价回复的礼貌性，语气是否友善且正式。",
                "format": "评价回复的格式是否正确，特别是参考信息插入的规范性。",
                "relevance": "评价回复的相关性，是否避免了信息的冗余，特别是参考信息是否在适当位置使用。"
            }

            如果发现回复中存在错误或问题，请提供相应的改进建议，并指出回复中的具体问题，给出修改建议：
            - 例如，如果参考信息（如学校地址、官网等）被不必要地列在邮件的结尾，应该提醒去掉重复信息，只在必要时引用。
            - 如果邮件中的语言或格式不规范，应该提供具体修改建议。尤其注意是否有冗余信息，特别是学校的联系信息、官网地址等是否应整合到邮件正文中，避免不必要的列出。
            
            以下是待检查的邮件回复内容：
        """

}
