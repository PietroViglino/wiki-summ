from llama_cpp import Llama
from deep_translator import GoogleTranslator
from modules.utils import split_text

N_CTX=1200
LLM=Llama(model_path='LLM/llama-2-7b-chat.Q4_K_M.gguf', n_gpu_layers=-1, n_ctx=2048)

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
    system_message = "Generate tags as a string with each tag separated by a comma\
        for the input text that you will receive.\
        The tags have to be meaningful keywords extracted or deducted from the text that will then be used for searching.\
        There should be no more than 20 tags, the most signifcant.\
        You have to absolutely avoid any kind of introduction or conclusion, your response should start with '|',\
        end with '|' and have all the 20 tags in between, separated by a comma.\
        Unless the tags are names of people or places (starting with the capital letter) they should be in english."
    user_message = text
    prompt = f"""<s>[INST] <<SYS>>
    {system_message}
    <</SYS>>
    {user_message} [/INST]"""
    output = LLM(prompt, max_tokens=0)
    res = output['choices'][0]['text']
    res = res.strip()
    return res

def summs_tags(text):
    text_b = bytes(text, 'utf-8')
    tokens = LLM.tokenize(text_b)
    splitted_tokens = [tokens[i:i+N_CTX] for i in range(0, len(tokens), N_CTX)]
    summ = ''
    tags = ''
    for t in splitted_tokens:
        t = LLM.detokenize(t)
        sum_part = simple_summ(t) + ' '
        summ += sum_part
        tags += generate_tags(t)
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
    trad = ''
    splitted_summ = split_text(summ_cleaned, 500)
    for block in splitted_summ:
        trad += GoogleTranslator(source='en', target='it').translate(block) + ' '
    # tags from string to list
    tags = list(set([_.strip() for _ in tags.split('|') if _ != '' and len(_) < 25]))
    # formatting all strings
    tags = [_.encode('utf8').decode('utf8') for _ in tags if _ != '']
    summ_cleaned = summ_cleaned.encode('utf8').decode('utf8')
    trad = trad.encode('utf8').decode('utf8')
    return summ_cleaned, trad, tags