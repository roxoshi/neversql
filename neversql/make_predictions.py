from tqdm import tqdm
from retreiver import similarity_search
from augument import create_prompt
from constants import SCHEMA_COLLECTION, GOLDEN_QUERY_COLLECTION
from typing import List
from llm import BedrockLLM
import re
import argparse

def predict(query):
    nearest_schemas = similarity_search(query, 3, SCHEMA_COLLECTION)
    retreived_schemas: List[str] = nearest_schemas['documents']
    schema_text = "\n".join(retreived_schemas[0])
    retreived_databases = nearest_schemas['metadatas'][0]
    retreived_databases = [s['database'] + '\n' for s in retreived_databases]
    
    query_with_schema = f"Question - {query}\n Schemas - {schema_text}"
    nearest_queries = similarity_search(query_with_schema, 3, GOLDEN_QUERY_COLLECTION,
                                        metadata_filter={"database": {"$in": retreived_databases}})
    retreived_queries = nearest_queries['documents']
    retreived_queries = "\n".join(retreived_queries[0])
    prompt = create_prompt(query, schema_text, retreived_queries)
    result_query = BedrockLLM().llm(prompt)
    result_query = result_query.replace("\n", " ").replace("\t", " ")
    result_query = re.sub(' +', ' ', result_query)
    return result_query

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='SQL RAG',
        description='Generate SQL predictions for the file with questions',
        epilog='no')
    parser.add_argument('-qf', '--questionfile', help="path of text file with questions", required=True)
    parser.add_argument('-sqlf', '--sqlfile', help="path of output sql file", required=True)
    args = vars(parser.parse_args())
    with open(args["questionfile"], 'r') as file:
        questions = file.readlines()
    answers = []
    with open(args["sqlfile"], "w") as f:
        for q in tqdm(questions):
            f.write(f"{predict(q)}\n")
       