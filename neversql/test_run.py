
from retreiver import similarity_search
from augument import create_prompt
from constants import SCHEMA_COLLECTION, GOLDEN_QUERY_COLLECTION
from typing import List
from llm import BedrockLLM

if __name__ == '__main__':
    query = "What is the average, minimum, and maximum age of all singers from France?"
    retreived_schemas: List[str] = similarity_search(query, 3, SCHEMA_COLLECTION)
    schema_text = "\n".join(retreived_schemas[0])
    
    query_with_schema = f"Question - {query}\n Schemas - {schema_text}"
    retreived_queries = similarity_search(query_with_schema, 3, GOLDEN_QUERY_COLLECTION)
    retreived_queries = "".join(retreived_queries[0])
    prompt = create_prompt(query, schema_text, retreived_queries)
    print("PROMPT:\n")
    print(prompt)
    print("\n", "="*30, "\n")
    print("LLM Respose:")
    print(BedrockLLM().llm(prompt))