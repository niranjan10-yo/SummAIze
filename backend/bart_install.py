from transformers import BartTokenizer, BartForConditionalGeneration

# Define the model save path
model_dir = "./bart_model"

# Download and save tokenizer
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
tokenizer.save_pretrained(model_dir)

# Download and save model
model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
model.save_pretrained(model_dir)

print(f"✅ BART model downloaded and saved in {model_dir}!")
