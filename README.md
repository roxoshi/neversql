# neversql
A Natural Language to SQL repository of articles, application and its code

#### To-do
- Embed all schemas and load them into a vector DB
- Before embedding chunk the schemas by table so that each table is a vector in our vector store
- Use the golden queries dataset to create a knowledge graph of tables and the join relationships between them
- Create a RAG pipeline where for each `question` top K table matching the question are found and their schemas are passed to the LLM along with the question and some default instruction prompts
- In this phase we might completely avoid building the knowledge graph and use it in the context. Will save that for later
