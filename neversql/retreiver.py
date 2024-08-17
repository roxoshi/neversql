import os
import logging
import glob
import argparse
import warnings
import chromadb
from typing import List, Optional, Dict, Tuple, Union
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



# CONSTANTS


def clean_string(s):
    return s.lower().replace('\n', '')


def create_file_chunks(sql_file_path: str) -> List[str]:
    with open(sql_file_path, 'r') as f:
        file_text = f.read()
    processed_lines = list(map(clean_string, file_text.split(";\n")))
    return [s for s in processed_lines if s.startswith("create")]


def add_to_db(collection, documents: List[List[Union[str, Dict]]], batch_size=25):
    print("Creating embeddings")
    for i in tqdm(range(0, len(documents), batch_size)):
        batch_docs, metadata = zip(*documents[i:i+batch_size])
        batch_docs, metadata = list(batch_docs), list(metadata)
        logging.info(f"Batch max len: {max([len(x) for x in batch_docs])}")
        id_list = [str(uuid4()) for i in range(len(batch_docs))]
        try:
            collection.add(
                documents = batch_docs,
                ids = id_list,
                metadatas=metadata
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
        # the database dictionary is db name which is used as metadata for retreival
        document: List[str, Dict] = [[doc, {"database": file.split('/')[-2]}] for doc in create_file_chunks(file)]
        all_documents.extend(document)
    logging.info(f"Sample document: {all_documents[0]}")
    return add_to_db(collection, all_documents, batch_size)


def add_from_texts(collection, documents: List[str],
                   id_list: Optional[List[str]] = None, batch_size:int = 25):
    return add_to_db(collection, documents, batch_size)


def similarity_search(query, top_k, collection_name, metadata_filter: Dict = None) -> List[str]:
    client = chromadb.PersistentClient(path=COLLECTIONS_PATH)
    collection = client.get_collection(name=collection_name,
                                        embedding_function=HFEmbeddingFunction(),
                                        )
    result = collection.query(
        query_texts=query,
        n_results=top_k,
        where = None or metadata_filter
    )
    return result


def _test_collection(query, collection_name):
    return similarity_search(query, 2, collection_name)

def main():
    client = chromadb.PersistentClient(path='db-prod/')
    # create collection for schemas
    try:
        collection = client.create_collection(name=SCHEMA_COLLECTION,
                                              embedding_function=HFEmbeddingFunction(),
                                              metadata={"hnsw:space": "cosine", "database": "value"})
    
    
        document_files = glob.glob(f'{SPIDER_PATH}/database/*/schema.sql')  
        add_from_files(collection, document_files, batch_size=15)
        
    except UniqueConstraintError:
        logging.error("Collection already exists so moving on...")        
    # create golden queries collection
    try:
        golden_data_file = f'{SPIDER_PATH}/train_gold.sql'
        with open(golden_data_file, 'r') as file:
            golden_queries = file.readlines()
            golden_queries = [[q.split("\t")[0], {"database":q.split("\t")[1]}] for q in golden_queries]
        # client.delete_collection(name=GOLDEN_QUERY_COLLECTION)
        collection = client.create_collection(name=GOLDEN_QUERY_COLLECTION,
                                              embedding_function=HFEmbeddingFunction(),
                                              metadata={"hnsw:space": "cosine", "database": "value"})
        add_from_texts(collection, golden_queries, batch_size=40)
    except UniqueConstraintError:
        logging.error(f"Collection already exists so moving on...")  


# if __name__ == '__main__':
#     logging.info("Execution begin")
#     parser = argparse.ArgumentParser(
#         prog='SQL RAG',
#         description='Generate SQL queries with natural language',
#         epilog='no')
#     parser.add_argument('-rr', '--reset', help="value=true/false", required=False)
#     args = vars(parser.parse_args())
#     if args['reset'] == 'true':
#         confirm = input("WARNING! Do you want to reset your DB's? (y/n)")
#         if confirm.lower() == 'y':
#             client = chromadb.PersistentClient(path=COLLECTIONS_PATH)
#             try:
#                 client.delete_collection(name=SCHEMA_COLLECTION)
#             except ValueError:
#                 pass
#             try:
#                 client.delete_collection(name=GOLDEN_QUERY_COLLECTION)
#             except ValueError:
#                 pass
#     main()
#     logging.info("Running tests")
#     query = "How many singers do we have?"
#     print(f"Test for {SCHEMA_COLLECTION}",_test_collection(query, SCHEMA_COLLECTION))
#     print(f"Test for {GOLDEN_QUERY_COLLECTION}",_test_collection(query, GOLDEN_QUERY_COLLECTION))
#     print("END....")
