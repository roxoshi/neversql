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

# tflog.set_verbosity_error()
# warnings.filterwarnings('ignore')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="basic.log"
)

parser = argparse.ArgumentParser(
    prog='SQL RAG',
    description='Generate SQL queries with natural language',
    epilog='no')

# CONSTANTS
SPIDER_PATH = 'data/spider'
COLLECTION_NAME = 'schema_vectors'

def clean_string(s):
    return s.lower().replace('\n', '')


def create_file_chunks(sql_file_path: str) -> List[str]:
    with open(sql_file_path, 'r') as f:
        file_text = f.read()
    processed_lines = list(map(clean_string, file_text.split(";\n")))
    return [s for s in processed_lines if s.startswith("create")]


def add_to_db(collection, document_files: List[str], id_list: Optional[List[str]] = None):
    all_documents = []
    for file in tqdm(document_files):
        document: List[str] = create_file_chunks(file)
        all_documents.extend(document)
    
    # vectorize and store the chunks in chroma db
    logging.info("Begin chroma collection update")
    batch_size = 5
    print("Creating embeddings")
    for i in tqdm(range(0, len(all_documents), batch_size)):
        batch_docs = all_documents[i:i+batch_size]
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


if __name__ == '__main__':
    print("Hello world")
    client = chromadb.PersistentClient(path='db-prod/')
    # client.reset()
    try:
        collection = client.create_collection(name=COLLECTION_NAME,
                                              embedding_function=HFEmbeddingFunction(),
                                              metadata={"hnsw:space": "cosine"})
        file_path = f'{SPIDER_PATH}/database/*/schema.sql'
        document_files = glob.glob(file_path)        
        collection = add_to_db(collection, document_files)
    except UniqueConstraintError:
        collection = client.get_collection(name=COLLECTION_NAME,
                                           embedding_function=HFEmbeddingFunction(),
                                           )
    
    parser.add_argument('-q', '--query')
    args = parser.parse_args()
    query = args.query
    if not query:
        query = "How many singers do we have?"
    # retreive top k vectors from chromadb based on the question
    result = collection.query(
        query_texts=query,
        n_results=3
    )
    print(result['documents'][0])
