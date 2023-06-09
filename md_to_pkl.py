# 使用langchain 搜索Milvus数据import os

from textsplitter import ChineseTextSplitter, combine_sentences
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.embeddings import HuggingFaceHubEmbeddings
from langchain.vectorstores import Milvus
import os
import json
from config import *

repo_id = "sentence-transformers/paraphrase-xlm-r-multilingual-v1"
hg_embeddings = HuggingFaceHubEmbeddings(repo_id=repo_id, huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN)

# 构建Milvus数据库collection
# 导入目标md文件
# 返回一个tuple，（向量数据库实例，文件名，文件扩展名，connection配置）
def md_to_vector_tup(mdpath:str , connectionargs:dict , embeddings):
    # Load Data
    loader = UnstructuredMarkdownLoader(mdpath)
    raw_documents = loader.load()

    # Split file name , file extension
    file_name_with_extension = os.path.basename(mdpath)
    file_name , file_extension = os.path.splitext(file_name_with_extension)
    
    # Split text 
    textsplitter = ChineseTextSplitter(pdf=False, sentence_size=SENTENCE_SIZE)

    docs_tran = loader.load_and_split(text_splitter=textsplitter)
    docs = combine_sentences(10, docs_tran)
    
    #collection name can only contain numbers, letters and underscores
    #因此需要对文件名称（多数时候是包含中文的）进行编码，之后再解码
    encoded_file_name = ""
    for char in file_name:
        encoded_file_name += "_{:04x}".format(ord(char))
        
    # Load Data to vectorstore
    VectorStore = Milvus.from_documents(
        docs,
        embeddings,
        collection_name = 'cn_{}'.format(encoded_file_name),    #the first character of a collection name must be an underscore or letter
        connection_args = connectionargs ,
    )
    
    return (VectorStore , file_name , file_extension , connectionargs)

# 将所构建的Milvus数据库collection主要信息序列化，以备后续查询时候导航到对应的collection
def vector_store_to_dict(vstp:tuple) -> dict:
    data = {
        "collection_name": vstp[0].collection_name, 
        "fields": vstp[0].fields,
        "index_params": vstp[0].index_params,
        "search_params": vstp[0].search_params,
        "consistency_level": vstp[0].consistency_level,
        "embedding_func": vstp[0].embedding_func.__class__.__name__,
        "file_name":vstp[1],
        "file_type":vstp[2],
        "connection_args": vstp[3],
    }
    return data

def serialize_vector_store(vstp:tuple):
    SerializedPath = 'stores/md_files_pkl/{}.pkl'.format(vstp[1])
    vector_store_dict = vector_store_to_dict(vstp)
    with open(SerializedPath, "w") as f:
        json.dump(vector_store_dict, f)
    


MarkDownPath = "/Users/smart_boy/Nutstore Files/何志勇的坚果云/审计/知识库/人事与薪酬/薪酬舞弊调查方法与防范.md"

ConnectionArgs = {"host": "192.168.0.107", "port": "19530"}

vs_tup = md_to_vector_tup(MarkDownPath , ConnectionArgs , hg_embeddings)

vs_tup[0].col.release()

serialize_vector_store(vs_tup)
