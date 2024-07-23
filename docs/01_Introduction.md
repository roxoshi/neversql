# Introduction
Natural language to SQL(NLSQL) is an application of NLP techniques to generate SQL queries that answer business questions. For example - I have two tables **Logins** and **Users**

`Logins (login_date Datetime, userid Int)`

`Users (userid Int, first_name String, last_name String, active_flag Bool)`

*Question* - Get names of all the users who logged on in the last 30 days

```mysql
SELECT b.first_name + b.last_name AS name
FROM Logins a
LEFT JOIN Users b
ON a.userid = b.userid
WHERE DATEDIF(day, CURRENT_DATE(), login_date) <= 30;
```
Assuming the query is correct for now, this is what we want our NLSQL model to achieve, only in much more complex scenarios. In summary we have three components

*Input*: A text of natural language question or statement (mostly asked by a non-technical user)

*Output*: A syntactically and logically correct SQL query

*Process*: Our LLM based NLSQL model

## Applications of NLSQL
1. Provide capability to non technical users to interact with their data without bothering the data analysts and data engineers for everything. Example below
```markdown
**Manager**: Hey can you pull a list of top 10 users who made the most purchases on our platform last month
**Data Analyst**: You can use the automatic query tool that Rajat built for us
**Manager**: Nevermind, I can do it faster in excel
```
2. Making text to SQL bots part of your application - e.g. customer can ask queries about their past order on the Amazon app.
3. You are an executive who took VC money saying you will revolutionize data analytics with AI so you decide to lay off some of the data analysts in your team and replace them with this tool. An example
```markdown
**VC owned CEO**: What is the 3 months rolling average of sales for my company in the last 12 months
**Bot**: cries in window functions
```
