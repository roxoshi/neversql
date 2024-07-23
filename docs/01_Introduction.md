# Natural Language to SQL

## Introduction
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
Assuming this answer is write for now, this is what we want our NLSQL model to achieve, only in much more complex scenarios. To summarize what we want -

*Input*: A text of natural language question or statement (mostly asked by a non-technical user)

*Output*: A syntactically and logically correct SQL query

*Process*: Our LLM based NLSQL model
