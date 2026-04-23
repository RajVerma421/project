from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


print("Loading tokenizer...")
MODEL_NAME = "microsoft/phi-2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

print("Downloading / loading model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto"
)

print("Creating pipeline...")
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=300
)

print("Model ready!")