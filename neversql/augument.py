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
    query = "How many singers do we have?"
    retreived_schemas: List[str] = similarity_search(query, 3, SCHEMA_COLLECTION)
    schema_text = "\n".join(retreived_schemas[0])
    
    query_with_schema = f"Question - {query}\n Schemas - {schema_text}"
    retreived_queries = similarity_search(query_with_schema, 3, GOLDEN_QUERY_COLLECTION)
    retreived_queries = "".join(retreived_queries[0])
    prompt = create_prompt(query, schema_text, retreived_queries)
    return prompt

