# app/core/granite_client.py

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load the tokenizer and model once when the module loads
MODEL_NAME = "ibm-granite/granite-3.2-2b-instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

# Optionally, move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def query_granite(prompt: str, max_tokens: int = 600, temperature: float = 0.7) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(
        **inputs,
        max_length=max_tokens,
        temperature=temperature,
        do_sample=True,
        top_p=0.9,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
    )
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_text
