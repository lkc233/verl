# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import string
import random

def normalize_answer(s):

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_punc(lower(s)))


def em_check(prediction, golden_answers):
    if isinstance(golden_answers, str):
        golden_answers = [golden_answers]
    normalized_prediction = normalize_answer(prediction)
    score = 0
    for golden_answer in golden_answers:
        golden_answer = normalize_answer(golden_answer)
        if golden_answer == normalized_prediction:
            score = 1
            break
    return score


def subem_check(prediction, golden_answers):
    if isinstance(golden_answers, str):
        golden_answers = [golden_answers]
    normalized_prediction = normalize_answer(prediction)
    score = 0
    for golden_answer in golden_answers:
        golden_answer = normalize_answer(golden_answer)
        if golden_answer in normalized_prediction:
            score = 1
            break
    return score


def extract_solution(solution_str):
    """Extract the equation from the solution string."""
    # Remove everything before the first "Assistant:"
    # if "Assistant:" in solution_str:
    #     solution_str = solution_str.split("Assistant:", 1)[1]
    # elif "<|im_start|>assistant" in solution_str:
    #     solution_str = solution_str.split("<|im_start|>assistant", 1)[1]
    # else:
    #     return None
    # solution_str = solution_str.split('\n')[-1]

    answer_pattern = r'<answer>(.*?)</answer>'
    match = re.finditer(answer_pattern, solution_str, re.DOTALL)
    matches = list(match)
    
    # If there are 0 or exactly 1 matches, return None
    if len(matches) == 0:
        return None
    
    # If there are 2 or more matches, return the last one
    return matches[-1].group(1).strip()


# def compute_score_em(solution_str, ground_truth, method='strict', format_score=0., score=1., extra_info=None):
#     """The scoring function for exact match (EM).

#     Args:
#         solution_str: the solution text
#         ground_truth: the ground truth
#         method: the method to extract the solution, choices are 'strict' and 'flexible'
#         format_score: the score for the format
#         score: the score for the correct answer
#     """
#     answer = extract_solution(solution_str=solution_str)
    
#     do_print = random.randint(1, 64) == 1
#     if do_print:
#         print(f"--------------------------------")
#         print(f"Golden answers: {ground_truth['target']}")
#         print(f"Extracted answer: {answer}")
#         print(f"Solution string: {solution_str}")
    
#     solution_str = solution_str.split("<|im_start|>assistant", 1)[1]
#     if '<search>query</search>' in solution_str:
#         format_score -= 10

#     # 检查是否存在<information>标签
#     has_information = bool(re.search(r'<information>.*?</information>', solution_str, flags=re.DOTALL))

#     # 初始化结果变量
#     has_think_after_last_information = False

#     if has_information:
#         # 找到最后一个<information>标签的结束位置
#         information_matches = list(re.finditer(r'<information>.*?</information>', solution_str, flags=re.DOTALL))
#         last_information_end = information_matches[-1].end() if information_matches else 0

#         # 检查最后一个<information>标签后面是否有<think>标签
#         remaining_text = solution_str[last_information_end:]
#         has_think_after_last_information = bool(re.search(r'<think>.*?</think>', remaining_text, flags=re.DOTALL))

#         if has_think_after_last_information:
#             format_score += 0.3
#     else:
#         format_score += 0.3
#     laws = ['《民法典》', '《中华人民共和国民法典》', '《刑法》', '《中华人民共和国刑法》']
#     solution_str = re.sub(r'<information>.*?</information>', '', solution_str, flags=re.DOTALL)
#     if any(law in solution_str for law in laws):
#         format_score += 0.3
#         search_pattern = r'<search>(.*?)</search>'
#         match = re.finditer(search_pattern, solution_str, re.DOTALL)
#         matches = list(match)
#         if len(matches) > 0:
#             format_score += 0.3
    
    
#     ret_score = 0
#     em_score = 0
#     if answer is None:
#         pass
#     else:
#         if em_check(answer, ground_truth['target']):
#             em_score = score
#     if do_print:
#         print(f"Score: format_score={format_score}, em_score={em_score}")
#     ret_score = format_score + em_score
#     # return ret_score
#     return {"score": ret_score, "extra_info": {"format_reward": format_score, "answer_reward": em_score}}

def compute_score_em(solution_str, ground_truth, method='strict', format_score=0., score=1., extra_info=None):
    """The scoring function for exact match (EM).

    Args:
        solution_str: the solution text
        ground_truth: the ground truth
        method: the method to extract the solution, choices are 'strict' and 'flexible'
        format_score: the score for the format
        score: the score for the correct answer
    """
    answer = extract_solution(solution_str=solution_str)
    
    do_print = random.randint(1, 64) == 1
    if do_print:
        print(f"--------------------------------")
        print(f"Golden answers: {ground_truth['target']}")
        print(f"Extracted answer: {answer}")
        print(f"Solution string: {solution_str}")
    
    # solution_str = solution_str.split("<|im_start|>assistant", 1)[1]
    # solution_str = re.sub(r'<information>.*?</information>', '', solution_str, flags=re.DOTALL)
    # solution_str = re.sub(r'<search>.*?</search>', '', solution_str, flags=re.DOTALL)
    # solution_str = re.sub(r'<think>.*?</think>', '', solution_str, flags=re.DOTALL)
    # solution_str = re.sub(r'<answer>.*?</answer>', '', solution_str, flags=re.DOTALL)
    # solution_str = solution_str.strip()
    # if not solution_str:
    #     format_score += 1.0
    
    
    ret_score = 0
    em_score = 0
    if answer is None:
        pass
    else:
        if em_check(answer, ground_truth['target']):
            em_score = score
    if do_print:
        print(f"Score: format_score={format_score}, em_score={em_score}")
    ret_score = format_score + em_score
    # return ret_score
    return {"score": ret_score, "format_reward": format_score, "answer_reward": em_score}



if __name__ == '__main__':
    solution_str = """
<think>首先我们需要分析各个选项的具体内容，再依据相关法律条文逐一判断其正确性。</think>
<search>我国刑法中关于缓刑、减刑、假释的规定</search>
<information>法条 1：《中华人民共和国刑法》第七十三条: 拘役的缓刑考验期限为原判刑期以上一年以下，但是不能少于二个月。有期徒刑的缓刑考验期限为原判刑期以上五年以下，但是不能少于一年。缓刑考验期限，从判决确定之日起计算。
法条 2：《中华人民共和国刑法》第四十八条: 死刑只适用于罪行极其严重的犯罪分子。对于应当判处死刑的犯罪分子，如果不是必须立即执行的，可以判处死刑同时宣告缓期二年执行。死刑除依法由最高人民法院判决的以外，都应当报请最高人民法院核准。死刑缓期执行的，可以由高级人民法院判决或者核准。
法条 3：《中华人民共和国刑法》第五十一条: 死刑缓期执行的期间，从判决确定之日起计算。死刑缓期执行减为有期徒刑的刑期，从死刑缓期执行期满之日起计算。</information>
<think>综合上述法条分析各个选项：
A选项中，缓刑或假释考验期满后，即原判的刑罚不再执行或被认为执行完毕，其应理解为原判刑罚被免除或视为已执行，不意味着附加刑部分也不被执行，此说法有误导性。因此A项错误。
B选项提到已满75周岁犯罪分子中的“首要分子”能否适用缓刑，在刑法中并无“首要分子”这一概念，仅指犯罪集团的组织、领导者以及积极参加者，并且符合缓刑实质条件的所有犯罪分子，包括首要分子，都可以适用缓刑，故B项描述也是正确的。
C选项中的张某因为限制减刑，死缓考验期满后不得假释。这一说法是正确的，符合《中华人民共和国刑法》第四十八条的解释。
D项关于假释期间犯罪的情况，按照《中华人民共和国刑法》第八十六条规定，对假释的犯罪分子，如果在假释考验期限内再犯新罪，应当撤销假释，按照刑法第六十九条的规定处理，而不是按照第71条数罪并罚。因此D描述也是正确的。
</think>
<answer>D</answer>
"""
    ground_truth = {'target': ['D']}
    print(compute_score_em(solution_str, ground_truth))
