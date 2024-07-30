# neversql
A Natural Language to SQL repository of articles, application and its code


## Notes
### 2024-07-28
1. The file `dev.json` in the spider path is what conserns us the most
2. It has the Question and the SQL queries as JSON list object 
3. the dabases have a sqllite files for the database which can act as the actual table that we can run
4. The database also has a schema diagram which we can refer if we don't want to go through the process of loading the whole databases in an sql engine
5. For now we will ignore the actual data in the database and consern ourselves only with the schema

#### To-do
- Embed all schemas and load them into a vector DB
- Before embedding chunk the schemas by table so that each table is a vector in our vector store
- Use the golden queries dataset to create a knowledge graph of tables and the join relationships between them
- Create a RAG pipeline where for each `question` top K table matching the question are found and their schemas are passed to the LLM along with the question and some default instruction prompts
- In this phase we might completely avoid building the knowledge graph and use it in the context. Will save that for later