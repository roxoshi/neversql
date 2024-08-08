from typing import List
import os
import re
import logging
import glob
import argparse
import warnings
from tqdm import tqdm
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_chroma import Chroma
from transformers import logging as tflog

tflog.set_verbosity_error()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="basic.log"
)

warnings.filterwarnings('ignore')

def clean_string(s):
    return s.lower().replace('\n','')

def create_file_chunks(sql_file_path: str) -> List[str]:
    with open(sql_file_path, 'r') as f:
        file_text = f.read()
    processed_lines = list(map(clean_string, file_text.split(";\n")))
    return [s for s in processed_lines if s.startswith("create")]

def get_all_paths(directory: str):
    return glob.glob(f'{directory}/database/*/schema.sql')

def get_directory_chunks(directory: str):
    for path in get_all_paths(directory):
        yield create_file_chunks(path)

def store_vectors(documents: List[str]):
    model_name = "dunzhang/stella_en_400M_v5"
    model_kwargs = {"device": "cuda", "trust_remote_code": True}
    encode_kwargs = {"normalize_embeddings": True}
    hf = HuggingFaceBgeEmbeddings(model_name=model_name,
                                  model_kwargs=model_kwargs,
                                  encode_kwargs=encode_kwargs
                                  )
    db = Chroma.from_texts(documents, hf)
    return db


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='SQL RAG',
        description='Generate SQL queries with natural language',
        epilog='no')

    parser.add_argument('-q', '--query')
    
    os_path = os.getcwd()
    data_path = 'data/spider'
    # create chunks of table schemas
    file_path = f'{data_path}/database/*/schema.sql'
    all_files = glob.glob(file_path)
    all_documents = []
    for f in tqdm(all_files):
        document: List[str] = create_file_chunks(f)
        all_documents.extend(document)
    # vectorize and store the chunks in chroma db
    db = store_vectors(all_documents)
    args = parser.parse_args()
    query = args.query
    if not query:
        query = "How many singers do we have?"
    # retreive top k vectors from chromadb based on the question
    docs = db.similarity_search(query=query, k=4)
    logging.info("Run complete. Sample document below: ")
    print("Top 1 document from search")
    print(docs[0].page_content)
