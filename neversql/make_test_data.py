import os
import json
import random

def main():
    all_data = json.load(open('data/spider/dev.json', 'r'))
    n_samples = 10
    ix_samples = random.sample(range(0, len(all_data)-1), n_samples)
    sample_data = []
    for i in ix_samples:
        sample_data.append(all_data[i])
    with open('data/spider/dev_sample.json', 'w') as file:
        json.dump(sample_data, file, indent=4)

    print(f"total questions in sample dataset: {len(sample_data)}")

if __name__ == '__main__':
    main()

