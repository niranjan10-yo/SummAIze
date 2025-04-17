from transformers import BartForConditionalGeneration

model_name = "facebook/bart-large-cnn"
save_path = "D:/SummAIze/backend/fine_tuned_bart"

# Download and save missing files
model = BartForConditionalGeneration.from_pretrained(model_name)
model.save_pretrained(save_path)

print("pytorch_model.bin downloaded and saved successfully!")
