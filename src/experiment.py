import json
import os
import pandas as pd
from openai import OpenAI
import random
import numpy as np
import time
import tiktoken
import re

# Configuration
# Check for OpenRouter first, then OpenAI
API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1" if os.getenv("OPENROUTER_API_KEY") else None
MODEL = "openai/gpt-4o-mini" if os.getenv("OPENROUTER_API_KEY") else "gpt-4o-mini"

# If no key, we can't run. But we are in a simulation where we might have access.
# The prompt says "You can also use openrouter, there is openrouter key in environment variable."
# So I assume OPENROUTER_API_KEY is set.

DATA_PATH = "code/castillo/data/raw_instruct/databricks-dolly-15k.json"
OUTPUT_FILE = "results/experiment_results.json"
NUM_SAMPLES = 50 # Keep it small for speed

print(f"Using Model: {MODEL}")
print(f"Base URL: {BASE_URL}")

if not API_KEY:
    print("WARNING: No API Key found. Experiment will fail.")

try:
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
except Exception as e:
    print(f"Error initializing client: {e}")

try:
    enc = tiktoken.encoding_for_model("gpt-4o-mini")
except:
    enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(enc.encode(text))

def load_data(path, n=100):
    data = []
    with open(path, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    # Filter for open_qa or general_qa
    filtered = [d for d in data if d['category'] in ['open_qa', 'general_qa', 'brainstorming']]
    print(f"Filtered {len(filtered)} samples from {len(data)}")
    random.seed(42)
    return random.sample(filtered, min(n, len(filtered)))

def experiment_loop():
    data = load_data(DATA_PATH, NUM_SAMPLES)
    results = []
    
    print(f"Starting experiment with {len(data)} samples...")
    
    for i, item in enumerate(data):
        instruction = item['instruction']
        context = item.get('context', '')
        full_prompt = f"{instruction}\n\nContext:\n{context}" if context else instruction
        
        try:
            # 1. Exact Prediction Step
            pred_prompt = (
                f"Instruction: {full_prompt}\n\n"
                "How many tokens will the response to this instruction be? "
                "Provide your best estimate as a single number (e.g., 42). Do not include any other text."
            )
            
            pred_response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": pred_prompt}],
                temperature=0,
                max_tokens=10
            )
            pred_text = pred_response.choices[0].message.content.strip()
            
            # Extract number
            numbers = re.findall(r'\d+', pred_text)
            if numbers:
                predicted_length = float(numbers[0])
            else:
                predicted_length = -1
            
            # 2. Bin Prediction Step
            bin_prompt = (
                f"Instruction: {full_prompt}\n\n"
                "Will the response to this instruction be Short (<50 tokens), Medium (50-200 tokens), or Long (>200 tokens)? "
                "Answer with exactly one word: Short, Medium, or Long."
            )
            
            bin_response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": bin_prompt}],
                temperature=0,
                max_tokens=10
            )
            predicted_bin = bin_response.choices[0].message.content.strip().replace('.', '')
            
            # 3. Generation Step
            gen_response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0, 
            )
            actual_text = gen_response.choices[0].message.content
            actual_length = count_tokens(actual_text)
            
            # Determine actual bin
            if actual_length < 50:
                actual_bin = "Short"
            elif actual_length <= 200:
                actual_bin = "Medium"
            else:
                actual_bin = "Long"

            results.append({
                "instruction": instruction,
                "context": context,
                "predicted_length": predicted_length,
                "predicted_bin": predicted_bin,
                "actual_length": actual_length,
                "actual_bin": actual_bin,
                "actual_text": actual_text,
                "prediction_raw": pred_text
            })
            print(f"Sample {i}: Pred={predicted_length} ({predicted_bin}), Actual={actual_length} ({actual_bin})")
            
        except Exception as e:
            print(f"Error on sample {i}: {e}")
            continue

    # Save results
    os.makedirs("results", exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Experiment complete.")

if __name__ == "__main__":
    experiment_loop()
