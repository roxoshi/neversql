import json
import pandas as pd
import sqlite3


def execution_match(generated_query: str, validation_query: str,
                    database_path: str) -> bool:
    con = sqlite3.connect(database_path)
    generated_data = pd.read_sql_query(generated_query, con)
    validation_data = pd.read_sql_query(validation_query, con)
    con.close()
    data_dff = generated_data.compare(validation_data)
    if data_dff.empty:
        return True
    return False


def exact_match(generated_query: str, validation_query: str):
    return generated_query.lower().strip() == validation_query.lower().strip()
