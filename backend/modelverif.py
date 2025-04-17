from transformers import BartForConditionalGeneration, BartTokenizer

model_path = "D:/SummAIze/backend/fine_tuned_bart"

model = BartForConditionalGeneration.from_pretrained(model_path, local_files_only=True)
tokenizer = BartTokenizer.from_pretrained(model_path, local_files_only=True)

print("Model and tokenizer loaded successfully! 🚀")
