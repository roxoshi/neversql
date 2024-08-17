import os
import logging
import glob
import argparse
import warnings
import chromadb
from typing import List, Optional
from chromadb.db.base import UniqueConstraintError
from hf_embeddings import HFEmbeddingFunction
from tqdm import tqdm
from uuid import uuid4
import torch
from transformers import logging as tflog
from constants import *

# tflog.set_verbosity_error()
# warnings.filterwarnings('ignore')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="basic.log",
    filemode='w'
)

parser = argparse.ArgumentParser(
    prog='SQL RAG',
    description='Generate SQL queries with natural language',
    epilog='no')

# CONSTANTS


def clean_string(s):
    return s.lower().replace('\n', '')


def create_file_chunks(sql_file_path: str) -> List[str]:
    with open(sql_file_path, 'r') as f:
        file_text = f.read()
    processed_lines = list(map(clean_string, file_text.split(";\n")))
    return [s for s in processed_lines if s.startswith("create")]


def add_to_db(collection, documents: List[str], batch_size=25):
    print("Creating embeddings")
    for i in tqdm(range(0, len(documents), batch_size)):
        batch_docs = documents[i:i+batch_size]
        logging.info(f"Batch max len: {max([len(x) for x in batch_docs])}")
        id_list = [str(uuid4()) for i in range(len(batch_docs))]
        try:
            collection.add(
                documents = batch_docs,
                ids = id_list
            )
        except:
            logging.info(f"Error schema: {[x for x in batch_docs if len(x) == 4291][0]}")
        torch.cuda.empty_cache()
    logging.info("Chroma collection updated successfully")
    return collection
    

def add_from_files(collection, document_files: List[str], 
                   id_list: Optional[List[str]] = None, batch_size:int = 25):
    all_documents = []
    for file in tqdm(document_files):
        document: List[str] = create_file_chunks(file)
        all_documents.extend(document)
    return add_to_db(collection, all_documents, batch_size)


def add_from_texts(collection, documents: List[str],
                   id_list: Optional[List[str]] = None, batch_size:int = 25):
    return add_to_db(collection, documents, batch_size)


def similarity_search(query, top_k, collection_name) -> List[str]:
    client = chromadb.PersistentClient(path=COLLECTIONS_PATH)
    collection = client.get_collection(name=collection_name,
                                        embedding_function=HFEmbeddingFunction(),
                                        )
    result = collection.query(
        query_texts=query,
        n_results=top_k
    )
    return result['documents']


def _test_collection(query, collection_name):
    return similarity_search(query, 2, collection_name)

def main():
    client = chromadb.PersistentClient(path='db-prod/')
    # create collection for schemas
    try:
        collection = client.create_collection(name=SCHEMA_COLLECTION,
                                              embedding_function=HFEmbeddingFunction(),
                                              metadata={"hnsw:space": "cosine"})
    
    
        document_files = glob.glob(f'{SPIDER_PATH}/database/*/schema.sql')        
        add_from_files(collection, document_files, batch_size=10)
        
    except UniqueConstraintError:
        logging.error("Collection already exists so moving on...")        
    # create golden queries collection
    try:
        golden_data_file = f'{SPIDER_PATH}/train_gold.sql'
        with open(golden_data_file, 'r') as file:
            golden_queries = file.readlines()
        # client.delete_collection(name=GOLDEN_QUERY_COLLECTION)
        collection = client.create_collection(name=GOLDEN_QUERY_COLLECTION,
                                              embedding_function=HFEmbeddingFunction(),
                                              metadata={"hnsw:space": "cosine"})
        add_from_texts(collection, golden_queries, batch_size=35)
    except UniqueConstraintError:
        logging.error(f"Collection already exists so moving on...")  

# main()
# print("Running tests")
# query = "How many singers do we have?"
# print(f"Test for {SCHEMA_COLLECTION}",_test_collection(query, SCHEMA_COLLECTION))
# print(f"Test for {GOLDEN_QUERY_COLLECTION}",_test_collection(query, GOLDEN_QUERY_COLLECTION))
# print("END....")
