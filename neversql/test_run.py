
from retreiver import similarity_search
from augument import create_prompt
from constants import SCHEMA_COLLECTION, GOLDEN_QUERY_COLLECTION
from typing import List
from llm import BedrockLLM

if __name__ == '__main__':
    query = "Show the stadium name and the number of concerts in each stadium."
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
    print("PROMPT:\n")
    print(prompt)
    print("\n", "="*30, "\n")
    print("LLM Respose:")
    print(BedrockLLM().llm(prompt))
    
    # "SELECT T2.name ,  count(*) FROM concert AS T1 JOIN stadium AS T2 ON T1.stadium_id  =  T2.stadium_id GROUP BY T1.stadium_id"