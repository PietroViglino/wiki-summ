from llama_cpp import Llama
from deep_translator import GoogleTranslator
from modules.utils import split_text
import logging

N_CTX=1200
# LLM=Llama(model_path='LLM/llama-2-7b-chat.Q4_K_M.gguf', n_gpu_layers=-1, n_ctx=2048, verbose=True)
LLM=Llama(model_path='LLM/llama-2-13b-chat.Q4_K_M.gguf', n_gpu_layers=-1, n_ctx=2048, verbose=True)

def simple_summ(text):
    system_message = "Generate a summary of the following text.\
        Do never make references to Wikipedia.\
        Avoid any kind of introduction."
    user_message = text
    prompt = f"""<s>[INST] <<SYS>>
    {system_message}
    <</SYS>>
    {user_message} [/INST]"""
    output = LLM(prompt, max_tokens=0)
    res = output['choices'][0]['text']
    return res

def clean_summ(summ):
    system_message = "Please clean the following text, as it is now badly written with some mistakes and repetitions.\
        You should present the cleaned content as if it was a touristic guide's paragraph.\
        It is very important that you only output the cleaned text as if it was a touristic guide's article, you shouldn't simulate an human's answer.\
        Omit everything that isn't the cleaned text like titles, introductions, conclusions or notes.\
        Remeber: NO TITLES, NO INTRODUCTIONS, NO COMMENTS, NO CONCLUSIONS."
    prompt = f"""<s>[INST] <<SYS>>
    {system_message}
    <</SYS>>
    Please clean this text and present it as if it was a paragraph taken from a touristic guide.\
    Don't introduce your response in any way, just start and end with the cleaned text, as if it was extracted from a touristic guide book.\
    Avoid titles, introductions, conclusions or comments. This is the text to process: {summ} [/INST]"""
    output = LLM(prompt, max_tokens=0)
    res = output['choices'][0]['text']
    res = res.strip()
    return res

def summs(text):
    text_b = bytes(text, 'utf-8')
    tokens = LLM.tokenize(text_b)
    splitted_tokens = [tokens[i:i+N_CTX] for i in range(0, len(tokens), N_CTX)]
    summ = ''
    for t in splitted_tokens:
        t = LLM.detokenize(t)
        sum_part = simple_summ(t) + ' '
        summ += sum_part
    if text == '':
        print('no text')
        return
    # splitting the summary if it exceeds the token limit (N_CTX)
    summ_cleaned = ''
    summ_b = bytes(summ, 'utf-8')
    tokens = LLM.tokenize(summ_b)
    splitted_tokens = [tokens[i:i+N_CTX] for i in range(0, len(tokens), N_CTX)]
    for t in splitted_tokens:
        t = LLM.detokenize(t)
        summ_cleaned += clean_summ(t)
    if '\n' in summ_cleaned[:70]:
        summ_cleaned = summ_cleaned.split('\n')
        summ_cleaned = ''.join(summ_cleaned[1:])
        if '\n' in summ_cleaned[:70]:
            summ_cleaned = summ_cleaned.split('\n')
            summ_cleaned = ''.join(summ_cleaned[1:])
    trad = ''
    splitted_summ = split_text(summ_cleaned, 500)
    logging.debug('Summarizaion completed. Starting translation')
    for block in splitted_summ:
        trad += GoogleTranslator(source='en', target='it').translate(block) + ' '
    return summ_cleaned, trad
