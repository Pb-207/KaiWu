from configparser import ConfigParser
import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

cf = ConfigParser()


# Load openai configs from ini
def load_openai_configs(cfpath):
    cf.read(cfpath)
    try:
        openai.api_key = cf.get('OPENAI', 'openai_api_key')
    except:
        openai.api_key = input('No valid OpenAI API Key, please input OpenAI API Key: ')
    try:
        openai.api_base = cf.get('OPENAI', 'openai_api_base')
    except:
        openai.api_base = 'https://api.openai.com/v1'
    if cf.getboolean('OPENAI', 'enable_proxy'):
        proxies = {
            'http': cf.get('OPENAI', 'proxy_http'),
            'https': cf.get('OPENAI', 'proxy_https')
        }
        openai.proxy = proxies


# Chat interface with LLM
def llm_chain(input1, input2, input3, prompt):
    llm = ChatOpenAI(temperature=cf.getfloat('CHAT', 'temperature'), model_name=cf.get('OPENAI', 'gpt_model'))
    prompt_temp = PromptTemplate(
        input_variables=["INPUT1", "INPUT2", "INPUT3"],
        template=prompt
    )
    chain = LLMChain(llm=llm, prompt=prompt_temp)
    answer = chain.run({
        'INPUT1': input1,
        'INPUT2': input2,
        'INPUT3': input3
    })

    return answer

