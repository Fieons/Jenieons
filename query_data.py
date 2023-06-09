from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, AIMessagePromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from config import *
import os

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


def get_chain_for_md_query():
    system_template = "给你一段文字,这段文字是从文件中提取出来的，文件名为: {result_file_name}," \
        "这段文字为:{result_text}。" \
        "再给你一个问题，问题为 :{question}," \
        "我提供的文字未必足以回答问题，你需要先进行判断，并根据不同的情况作出不同的回答：" \
        "情况一：如果我提供的文字不足以回答问题，则回答：“资料不足够" \
        "情况二：如果提供的文字已经足够回答问题，则根据提供的文字和所提的问题进行回答。" 

    system_prompt = SystemMessagePromptTemplate.from_template(system_template)

    ai_template = ""
    ai_prompt = AIMessagePromptTemplate.from_template(ai_template)

    # create the chat prompt template
    chat_prompt = ChatPromptTemplate.from_messages([system_prompt, ai_prompt])

    llm = OpenAI(temperature=0, max_tokens=1000)
    
    return LLMChain(llm=llm, prompt=chat_prompt)


