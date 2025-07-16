import json
import os
from verl.tools.utils.llm_api_demo import call_vllm

import re
from tqdm import tqdm

filter_prompt_templates = {}
filter_prompt_templates['search_article'] = filter_prompt_templates['search_interpretation'] = """
# 角色
你是一个专业的法律文本比对助手。

# 任务目标
你的任务是：接收一组由大型语言模型（LLM）生成的法律条文（可能包含瑕疵），和一组官方的、正确的法律条文。你需要仔细比对，找出每一个LLM生成的法条在官方正确法条列表中的实质性对应项，并以JSON格式返回所有匹配的正确法条的完整列表。

# 匹配核心原则
比对的重点是法律规则的实质性内容和核心含义，而不是表面的文字完全一致。

# 可容忍的细微差异
在判断实质性匹配时，请容忍以下类型的“无伤大雅”的错误：

编号错误：例如，LLM生成的“第十条”可能实质内容对应的是正确的“第十二条”。
少量文字出入：LLM版本可能存在个别近义词替换、语序微调、或少量文字的遗漏/冗余，但只要不改变法条核心含义即可。
标点符号或格式差异。
# 执行步骤
分析输入：逐一阅读并理解 【大模型生成的法条】 列表中的每一个法条的核心含义。
比对查找：对于每一个LLM生成的法条，在 【正确法条】 列表中遍历查找，看是否存在一个法条与其构成“实质性匹配”。
构建并返回结果：
将所有找到的、对应的正确法条的原文汇总到一个列表中。
如果某个LLM生成的法条在正确法条列表中找不到实质性匹配项，则忽略该法条，不要在结果中包含任何内容。
如果所有LLM生成的法条都找不到匹配项，则返回一个空列表 []。
最终，以严格的JSON格式输出结果列表。

你应生成的输出结果格式如下：
```json
[
    "正确法条（或司法解释）1",
    "正确法条（或司法解释）2"
]
```
【大模型生成的法条】
{llm_articles}

【正确法条】
{correct_articles}

"""

filter_prompt_templates['search_reference_book'] = """
# 任务目标
你的任务是：接收一组由大型语言模型（LLM）生成的法律知识（可能包含错误），和一组从法律辅导书中检索回的法律知识。你需要仔细比对，从检索回的知识中找出可以修正或补充LLM生成的知识的内容，并以JSON格式返回所有匹配的正确知识的完整列表。
# 匹配核心原则
你返回的正确知识必须和 LLM 生成的知识相关，并能修正或补充LLM生成的知识。
# 执行步骤
1. 分析输入：逐一阅读并理解 【大模型生成的知识】 列表中的每一个知识点的核心含义。
2. 比对查找：
对于每一个 LLM 生成的知识，在 【检索回的知识】 列表中遍历查找，看是否存在一个知识点与其构成匹配。
3. 构建并返回结果：
将所有找到的、相关的检索回的知识点的原文汇总到一个列表中。
如果某个 LLM 生成的知识在检索回的知识列表中找不到匹配项，则忽略该知识点，不要在结果中包含任何内容。
如果所有 LLM 生成的知识都找不到匹配项，则返回一个空列表 []。
最终，以严格的JSON格式输出结果列表。
你应生成的输出结果格式如下：
```json
[
    "正确知识1",
    "正确知识2"
]
```
【大模型生成的知识】
{llm_knowledge}
【检索回的知识】
{retrieved_knowledge}
"""

def extract_json_content(text):
    """
    提取字符串中```json和```之间的内容
    """
    # 如果json.loads成功，则直接返回
    try:
        json_content = json.loads(text)
        return text
    except json.JSONDecodeError:
        pass
    pattern = r'```json(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def retrieve(queries, topk, url):
    """
    使用检索器获取与查询相关的法律条文。
    """
    import requests
    try:
        response = requests.post(url, json={"query": queries, "topk": topk}, timeout=3000)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error retrieving articles: {e}")
        return {"result": []}


def retrieve_and_filter(tool_call, topk=3):
    tool_call_name = tool_call['name']
    query_list = tool_call['arguments']['query_list']
    if not query_list:
        return []
    url = retriever_urls[tool_call_name]
    retrieved = retrieve(query_list, topk, url)['result']
    if tool_call_name in ['search_article', 'search_interpretation']:
        retrieved_list = [_['document'] for a in retrieved for _ in a]
        retrieved_set = list(set(retrieved_list))  # 去重
        retrieved_set = sorted(retrieved_set)
        if retrieved_set:
            filter_prompt_template = filter_prompt_templates[tool_call_name]
            filter_prompt = filter_prompt_template.format(
                llm_articles=json.dumps(query_list, ensure_ascii=False),
                correct_articles=json.dumps(retrieved_set, ensure_ascii=False)
            )
            max_retries_filter = 10
            filter_result = []  # Ensure filter_result is always defined
            filter_response = ''
            for filter_attempt in range(1, max_retries_filter + 1):
                try:
                    filter_response = call_vllm(prompt=filter_prompt, model="Qwen/Qwen2.5-32B-Instruct", base_url="http://222.29.51.205:7281")
                    filter_json_content = extract_json_content(filter_response)
                    if filter_json_content is not None:
                        filter_result = json.loads(filter_json_content)
                        break
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Error parsing filter response: {e}")
                    # print(filter_response)
                    filter_result = []
        else:
            filter_result = []
    elif tool_call_name == 'search_reference_book':
        docs = [_['document'] for a in retrieved for _ in a]
        docs = [json.loads(x) for x in sorted(set(json.dumps(d, sort_keys=True, ensure_ascii=False) for d in docs))]
        filter_prompt_template = filter_prompt_templates[tool_call_name]
        filter_prompt = filter_prompt_template.format(
            llm_knowledge=json.dumps(query_list, ensure_ascii=False),
            retrieved_knowledge=json.dumps(docs, ensure_ascii=False)
        )
        max_retries_filter = 10
        filter_response = ''
        filter_result = []  # Ensure filter_result is always defined
        for filter_attempt in range(1, max_retries_filter + 1):
            try:
                filter_response = call_vllm(prompt=filter_prompt, model="Qwen/Qwen2.5-32B-Instruct", base_url="http://222.29.51.205:7281")
                filter_json_content = extract_json_content(filter_response)
                if filter_json_content is not None:
                    filter_result = json.loads(filter_json_content)
                    break
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error parsing filter response: {e}")
                # print(filter_response)
                filter_result = []
    else:
        raise ValueError(f"Unsupported tool call name: {tool_call_name}")
    return filter_result