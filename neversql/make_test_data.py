import os
import json
import random

def main():
    all_data = json.load(open('data/spider/dev.json', 'r'))
    n_samples = 10
    ix_samples = random.sample(range(0, len(all_data)-1), n_samples)
    sample_data = []
    for i in ix_samples:
        with open('data/gold_questions_sample.txt','a') as f:
            f.write(f"{all_data[i]['question']}\n")
        with open('data/gold_sql_sample.sql','a') as f:
            f.write(f"{all_data[i]['query']}\n")
    #     sample_data.append(all_data[i])
    # with open('data/spider/dev_sample.json', 'w') as file:
    #     json.dump(sample_data, file, indent=4)

    print(f"total questions in sample dataset: {len(ix_samples)}")

if __name__ == '__main__':
    main()

