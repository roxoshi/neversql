from typing import List, Optional
from constants import *


SYSTEM_IDENTITY_PROMPT = 'You are a SQL expert agent. Return a SQL query that will answer the \
[QUESTION] from the user. Only use the schemas provided in the [SCHEMAS] section of the prompt \
Use the example sql queries in the [EXAMPLES] section for reference. They are similar to \
the question that is asked. Only return a valid SQL query as output. Do not add anything.'

def create_prompt(query: str, retreived_docs: Optional[str],
                  retreived_queries: Optional[str]) -> str:
    prompt = f'{SYSTEM_IDENTITY_PROMPT}\n\n[SCHEMAS]\n{retreived_docs}\n\n[EXAMPLES]\n\
    {retreived_queries}\n\n[Question]\n{query}'
    return prompt

def add_custom_prompts() -> str:
    return ""

def main():
    from retreiver import similarity_search
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
    return prompt

print(main())

