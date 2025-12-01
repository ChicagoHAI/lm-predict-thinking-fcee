import json
import os

input_file = 'datasets/dolly_15k/databricks-dolly-15k.jsonl'
sample_file = 'datasets/dolly_15k/samples.json'

with open(input_file, 'r') as f:
    lines = [f.readline() for _ in range(5)]

samples = [json.loads(line) for line in lines]

with open(sample_file, 'w') as f:
    json.dump(samples, f, indent=2)

print(f"Created sample file at {sample_file}")
