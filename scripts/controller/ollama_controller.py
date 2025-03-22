#type:ignore
import requests
from typing import Optional
from config import config


def call_ollama(
    prompt: str,
    system: str = "",
    stream: bool = False,
    model: Optional[str] = None
) -> str:
    """
    调用本地 Ollama 服务生成回复。

    Args:
        prompt (str): 输入提示词。
        system (str): 可选的系统级指令（用于设定角色）。
        stream (bool): 是否使用流式输出。
        model (Optional[str]): 指定使用的模型名称，不填则用 config 中默认值。

    Returns:
        str: 模型生成的回复文本。
    """
    model_name = model or config.OLLAMA_MODEL
    url = f"{config.OLLAMA_URL}/api/generate"

    payload = {
        "model": model_name,
        "prompt": prompt,
        "system": system,
        "stream": stream
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"[Ollama Error] 请求失败: {e}")
        return "[错误] 本地模型服务不可用或返回异常"
    
