import requests
import os
from openai import OpenAI


def get_proxies():
    """
    获取代理设置，优先读取环境变量 HTTP_PROXY/HTTPS_PROXY。
    """
    http_proxy = 'http://localhost:10809'
    https_proxy = 'http://localhost:10809'
    proxies = {}
    if http_proxy:
        proxies["http"] = http_proxy
    if https_proxy:
        proxies["https"] = https_proxy
    return proxies if proxies else None

# 调用 OpenAI GPT API


def call_gpt(prompt, api_key=None, model="gpt-4o", proxies=None):
    """
    调用 OpenAI GPT API，返回模型回复。
    :param prompt: 用户输入的提示
    :param api_key: OpenAI API Key（可选，未提供则读取环境变量OPENAI_API_KEY）
    :param model: 使用的GPT模型
    :return: 模型回复内容
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API Key 未设置")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    proxies = proxies or get_proxies()
    response = requests.post(url, headers=headers, json=data, proxies=proxies)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# 调用 Google Gemini API


def call_gemini(prompt, api_key=None, model="gemini-2.5-pro", proxies=None):
    """
    调用 Google Gemini API，返回模型回复。
    :param prompt: 用户输入的提示
    :param api_key: Gemini API Key（可选，未提供则读取环境变量GEMINI_API_KEY）
    :param model: 使用的Gemini模型
    :return: 模型回复内容
    """
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Gemini API Key 未设置")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    proxies = proxies or get_proxies()
    response = requests.post(url, headers=headers, json=data, proxies=proxies)
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

# 调用 DeepSeek API


def call_deepseek(prompt, api_key=None, model="deepseek-r1-250120", proxies=None):
    """
    调用 DeepSeek API，返回模型回复。
    :param prompt: 用户输入的提示
    :param api_key: DeepSeek API Key（可选，未提供则读取环境变量ARK_API_KEY）
    :param model: 使用的DeepSeek模型
    :return: 模型回复内容
    """
    api_key = api_key or os.getenv("ARK_API_KEY")
    if not api_key:
        raise ValueError("DeepSeek API Key 未设置")
    url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# 调用 Qwen-Max API（通义千问，OpenAI兼容模式）


def call_qwen_max(prompt, api_key=None, model="qwen-max-latest", proxies=None, system_message=None):
    """
    调用 Qwen-Max API（OpenAI兼容模式），返回模型回复。
    :param prompt: 用户输入的提示（str 或 list of messages）
    :param api_key: Qwen API Key（可选，未提供则读取环境变量DASHSCOPE_API_KEY 或 QWEN_API_KEY）
    :param model: 使用的Qwen模型
    :param system_message: 可选，system role 内容
    :return: 模型回复内容
    """
    api_key = api_key or os.getenv(
        "DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY")
    if not api_key:
        raise ValueError("Qwen API Key 未设置")
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # 支持 prompt 为字符串或 messages 列表
    if isinstance(prompt, list):
        messages = prompt
    else:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
    data = {
        "model": model,
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    # 兼容 OpenAI 格式
    return result["choices"][0]["message"]["content"]

# 调用本地 vllm server
# def call_vllm(prompt, model="Qwen/Qwen2.5-7B-Instruct", system_message=None, base_url="http://222.29.51.209:7280", return_type="content", **kwargs):
#     """
#     调用本地 vllm server（OpenAI 兼容接口），返回模型回复。
#     :param prompt: 用户输入的提示（str 或 list of messages）
#     :param model: 使用的模型名
#     :param api_key: 可选，API Key（如有需要）
#     :param proxies: 可选，代理设置
#     :param system_message: 可选，system role 内容
#     :param base_url: vllm server 的 base url
#     :return: 模型回复内容
#     """
#     url = f"{base_url}/v1/chat/completions"
#     headers = {"Content-Type": "application/json"}
#     # 支持 prompt 为字符串或 messages 列表
#     if isinstance(prompt, list):
#         messages = prompt
#     else:
#         messages = []
#         if system_message:
#             messages.append({"role": "system", "content": system_message})
#         messages.append({"role": "user", "content": prompt})
#     data = {
#         "model": model,
#         "messages": messages,
#         # "temperature": 0.9,  # 可选，温度参数
#         # "max_tokens": 1024,  # 可选，最大 token 数
#         **kwargs  # 其他可选参数
#     }
#     response = requests.post(url, headers=headers, json=data)
#     response.raise_for_status()
#     result = response.json()
#     if return_type == "json":
#         return result
#     elif return_type == "content":
#         return result["choices"][0]["message"]["content"]
#     else:
#         raise ValueError("return_type 只能为 'json' 或 'content'")


def call_vllm(prompt, model="Qwen/Qwen2.5-7B-Instruct", system_message=None, base_url="http://222.29.51.209:7280", return_type="content", **kwargs):
    """
    调用本地 vllm server（OpenAI 兼容接口），返回模型回复。
    :param prompt: 用户输入的提示（str 或 list of messages）
    :param model: 使用的模型名
    :param api_key: 可选，API Key（如有需要）
    :param proxies: 可选，代理设置
    :param system_message: 可选，system role 内容
    :param base_url: vllm server 的 base url
    :return: 模型回复内容
    """

    openai_api_key = "EMPTY"
    openai_api_base = f'{base_url}/v1'

    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )
    # 支持 prompt 为字符串或 messages 列表
    if isinstance(prompt, list):
        messages = prompt
    else:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs  # 其他可选参数
    )

    if return_type == "raw":
        return response
    elif return_type == "content":
        return response.choices[0].message.content
    else:
        raise ValueError("return_type 只能为 'raw' 或 'content'")


def call_llm(prompt, llm_type, model, api_key=None, proxies=None):
    """
    通用 LLM 调用接口，根据 llm_type 选择 GPT、Gemini、DeepSeek、Qwen 或 vllm。
    :param prompt: 用户输入的提示
    :param llm_type: 'gpt'、'gemini'、'deepseek'、'qwen' 或 'vllm'
    :param api_key: API Key（可选）
    :param model: 模型名（可选）
    :return: 模型回复内容
    """
    if llm_type == "gpt":
        return call_gpt(prompt, api_key=api_key, model=model, proxies=proxies)
    elif llm_type == "gemini":
        return call_gemini(prompt, api_key=api_key, model=model, proxies=proxies)
    elif llm_type == "deepseek":
        return call_deepseek(prompt, api_key=api_key, model=model, proxies=proxies)
    elif llm_type == "qwen":
        return call_qwen_max(prompt, api_key=api_key, model=model, proxies=proxies)
    elif llm_type == "vllm":
        return call_vllm(prompt, model=model)
    else:
        raise ValueError(
            "llm_type 只能为 'gpt'、'gemini'、'deepseek'、'qwen' 或 'vllm'")


if __name__ == "__main__":
    # 示例用法
    # with open('prompt.txt', 'r', encoding='utf-8') as f:
    #     prompt = f.read().strip()
    prompt = "你好，介绍一下人工智能。"
    for llm_type, model in [
        # ("gpt", "gpt-4o"),
        ("gemini", "gemini-2.5-pro"),
        # ("deepseek", "deepseek-r1-250120"),
        # ("qwen", "qwen-max-latest"),
        # ("vllm", "Qwen/Qwen2.5-7B-Instruct")
    ]:
        try:
            print(f"{llm_type.upper()}回复:", call_llm(
                prompt, llm_type, model=model, proxies=get_proxies()))
        except Exception as e:
            print(f"调用{llm_type.upper()}失败:", e)
