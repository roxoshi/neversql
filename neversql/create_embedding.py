from typing import List
import os
import re
import logging
import glob

logging.basicConfig(level=logging.INFO)

def clean_string(s):
    return s.lower().replace('\n','')

def create_file_chunks(sql_file_path: str) -> List[str]:
    with open(sql_file_path, 'r') as f:
        file_text = f.read()
    processed_lines = list(map(clean_string, file_text.split(";\n")))
    return [s for s in processed_lines if s.startswith("create")]

def get_all_paths(directory: str):
    return glob.glob(f'{directory}/database/*/schema.sql')

def get_directory_chunks(directory: str):
    for path in get_all_paths(directory):
        yield create_file_chunks(path)

if __name__ == '__main__':
    os_path = os.getcwd()
    data_path = 'data/spider'
    file_path = f'{data_path}/database/academic/schema.sql'
    output: List[str] = create_chunks(file_path)
    
    print("success")
    