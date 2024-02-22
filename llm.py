from llama_cpp import Llama
from deep_translator import GoogleTranslator
from utils import split_text


N_CTX=1200
LLM = Llama(model_path='LLM/llama-2-7b-chat.Q4_K_M.gguf', n_gpu_layers=-1, n_ctx=2048)


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

def summarize(text):
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
    summ = clean_summ(summ)
    if '\n' in summ[:70]:
        summ = summ.split('\n')
        summ = ''.join(summ[1:])
    trad = ''
    splitted_summ = split_text(summ, 500)
    for block in splitted_summ:
        trad += GoogleTranslator(source='en', target='it').translate(block) + ' '
    return summ, trad

def clean_summ(summ):
    system_message = "Please clean the following text, as it is now badly written with some mistakes and repetitions.\
        It is very important that you only output the cleaned text as if it was an article, you shouldn't simulate an answer.\
        Omit everything that isn't the cleaned text, like your introduction, conclusion or your notes.\
        Do never make references to Wikipedia.\
        You should present the cleaned content as if it was a touristic guide's article.\
        Never address the user (the reader of the touristic guide). \
        Avoid any kind of introduction and be serious."
    prompt = f"""<s>[INST] <<SYS>>
    {system_message}
    <</SYS>>
    {summ} [/INST]"""
    output = LLM(prompt, max_tokens=0)
    res = output['choices'][0]['text']
    res = res.strip()
    return res

def generate_tags(text):
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