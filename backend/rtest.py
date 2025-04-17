from transformers import BartForConditionalGeneration, BartTokenizer
import torch

# Path to your offline fine-tuned model
model_path = r"D:/SummAIze/backend/bart_model"  # Ensure this path is correct

# Load the model and tokenizer from the local directory
model = BartForConditionalGeneration.from_pretrained(model_path, local_files_only=True)
tokenizer = BartTokenizer.from_pretrained(model_path, local_files_only=True)

print("✅ Model and tokenizer loaded successfully!")

def summarize_text(text):
    # Tokenize input text
    print("🔍 Input Text:", text)

    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
    
    print("🔍 Tokenized Input:", inputs)

    # Generate summary using model
    summary_ids = model.generate(
        **inputs, 
        max_length=200, 
        min_length=50, 
        length_penalty=2.0, 
        num_beams=4, 
        early_stopping=True
    )
    print("🔍 Raw Summary IDs:", summary_ids)

    
    # Decode the generated summary
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    print("📝 Generated Summary:", summary)
    return summary

# Example text
text = """Artificial intelligence (AI) is transforming industries by automating tasks, improving efficiency, and enabling new capabilities. 
Companies are investing heavily in AI research, and its applications span across healthcare, finance, and robotics.
However, ethical concerns about bias and transparency remain significant challenges."""
#print("🔍 Model Configuration:", model.config)
print("🔍 Tokenizer Special Tokens:", tokenizer.special_tokens_map)
print("🔍 Tokenizer Vocab Size:", tokenizer.vocab_size)



# Generate summary
summary = summarize_text(text)
print("📝 Generated Summary:", summary)
