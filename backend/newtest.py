import os
import torch
from transformers import BartForConditionalGeneration, BartTokenizer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def diagnose_model(model_path, sample_text):
    """Diagnose issues with model loading and generation."""
    logger.info(f"Diagnosing model at: {model_path}")
    
    # Check if path exists
    if not os.path.exists(model_path):
        logger.error(f"Model path does not exist: {model_path}")
        return
    
    try:
        # Step 1: Try to load the model
        logger.info("Attempting to load model...")
        model = BartForConditionalGeneration.from_pretrained(model_path, local_files_only=True)
        logger.info("Model loaded successfully")
        
        # Step 2: Try to load the tokenizer
        logger.info("Attempting to load tokenizer...")
        tokenizer = BartTokenizer.from_pretrained(model_path, local_files_only=True)
        logger.info("Tokenizer loaded successfully")
        
        # Step 3: Check model structure
        logger.info(f"Model type: {type(model)}")
        logger.info(f"Model config: {model.config}")
        
        # Step 4: Move to device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {device}")
        model = model.to(device)
        
        # Step 5: Tokenize input
        logger.info("Tokenizing input text...")
        inputs = tokenizer(sample_text, return_tensors="pt", max_length=1024, truncation=True)
        input_length = inputs["input_ids"].shape[1]
        logger.info(f"Input length: {input_length} tokens")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Step 6: Try generation with different parameters
        logger.info("Attempting generation with default parameters...")
        try:
            with torch.no_grad():
                summary_ids = model.generate(**inputs)
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            logger.info(f"Generated summary (default params): {summary}")
        except Exception as e:
            logger.error(f"Error during default generation: {str(e)}")
        
        # Try with minimal parameters
        logger.info("Attempting generation with minimal parameters...")
        try:
            with torch.no_grad():
                summary_ids = model.generate(
                    inputs["input_ids"],
                    max_length=100,
                    num_beams=1
                )
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            logger.info(f"Generated summary (minimal params): {summary}")
        except Exception as e:
            logger.error(f"Error during minimal generation: {str(e)}")
        
        # Try with different parameters
        logger.info("Attempting generation with alternative parameters...")
        try:
            with torch.no_grad():
                summary_ids = model.generate(
                    inputs["input_ids"],
                    max_length=200,
                    min_length=10,
                    length_penalty=1.0,
                    num_beams=2,
                    early_stopping=True
                )
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            logger.info(f"Generated summary (alternative params): {summary}")
        except Exception as e:
            logger.error(f"Error during alternative generation: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error during model diagnosis: {str(e)}")

if __name__ == "__main__":
    # Path to your problematic model
    problematic_model_path = r"D:/SummAIze/backend/fine_tuned_bart_multinews"  # Update this to your new model path
    
    # Path to your working model (for comparison)
    working_model_path = r"D:/SummAIze/backend/fine_tuned_bart"  # Update this to your old model path
    
    # Sample text for testing
    sample_text = "In a historic move, a coalition of global leaders has reached a tentative agreement to combat climate change by significantly reducing carbon emissions over the next two decades. The agreement, which follows years of intense negotiations, aims to limit global temperature rise to 1.5°C above pre-industrial levels. However, critics argue that the agreement lacks strict enforcement mechanisms, raising concerns about its effectiveness. Some developing nations have expressed skepticism, stating that wealthier countries should bear a greater share of the financial burden. Despite these concerns, environmental advocates have praised the agreement as a crucial step forward, emphasizing the need for global cooperation in addressing climate change."
    
    # Diagnose problematic model
    logger.info("\n\n===== DIAGNOSING PROBLEMATIC MODEL =====\n")
    diagnose_model(problematic_model_path, sample_text)
    
    # Diagnose working model for comparison
    logger.info("\n\n===== DIAGNOSING WORKING MODEL (FOR COMPARISON) =====\n")
    diagnose_model(working_model_path, sample_text)
