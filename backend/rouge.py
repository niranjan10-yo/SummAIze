import os
import torch
from transformers import BartForConditionalGeneration, BartTokenizer
from rouge_score import rouge_scorer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_model_and_tokenizer(model_path):
    """Load model and tokenizer from the specified path with error handling."""
    try:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path does not exist: {model_path}")
        
        model = BartForConditionalGeneration.from_pretrained(model_path, local_files_only=True)
        tokenizer = BartTokenizer.from_pretrained(model_path, local_files_only=True)
        
        # Move model to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
        logger.info(f"Model loaded successfully and moved to {device}")
        
        return model, tokenizer, device
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

def summarize_text(text, model, tokenizer, device, max_length=200, min_length=50):
    """Generate a summary for the given text using the loaded model."""
    try:
        # Tokenize input text
        inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}  # Move inputs to the same device as model

        # Generate summary using model
        summary_ids = model.generate(
            **inputs, 
            max_length=max_length, 
            min_length=min_length, 
            length_penalty=2.0, 
            num_beams=4, 
            early_stopping=True
        )
        
        # Check if summary was generated
        if len(summary_ids) == 0:
            logger.warning("Model returned no summary. Retrying with adjusted parameters...")
            summary_ids = model.generate(
                inputs["input_ids"], 
                max_length=max_length + 50, 
                num_beams=2
            )

        # Decode the generated summary
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary
    except Exception as e:
        logger.error(f"Error during summarization: {str(e)}")
        raise

def evaluate_model(model_path, texts, reference_summaries):
    """Evaluate a model on multiple text samples and calculate average ROUGE scores."""
    model, tokenizer, device = load_model_and_tokenizer(model_path)
    
    # Initialize ROUGE scorer
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    all_scores = {'rouge1': [], 'rouge2': [], 'rougeL': []}
    
    for i, (text, reference) in enumerate(zip(texts, reference_summaries)):
        logger.info(f"Processing sample {i+1}/{len(texts)}")
        
        # Generate summary
        generated_summary = summarize_text(text, model, tokenizer, device)
        logger.info(f"Generated summary: {generated_summary}")
        
        # Calculate ROUGE scores
        scores = scorer.score(reference, generated_summary)
        
        # Store scores
        for metric, score in scores.items():
            all_scores[metric].append(score)
        
        # Print individual scores
        logger.info(f"Sample {i+1} ROUGE Scores:")
        for key, value in scores.items():
            logger.info(f"{key.upper()}: Precision: {value.precision:.4f}, Recall: {value.recall:.4f}, F1: {value.fmeasure:.4f}")
    
    # Calculate and return average scores
    avg_scores = {}
    for metric, scores_list in all_scores.items():
        avg_precision = sum(score.precision for score in scores_list) / len(scores_list)
        avg_recall = sum(score.recall for score in scores_list) / len(scores_list)
        avg_f1 = sum(score.fmeasure for score in scores_list) / len(scores_list)
        avg_scores[metric] = (avg_precision, avg_recall, avg_f1)
    
    return avg_scores

if __name__ == "__main__":
    # Path to your offline fine-tuned model
    fine_tuned_model_path = r"D:/SummAIze/backend/fine_tuned_bart_multinews"
    
    # Path to the base BART large model (if you have it locally)
    base_model_path = r"D:/SummAIze/backend/bart_model"  # Change this if you have it downloaded locally
    
    # Example texts and reference summaries (you can expand this list)
    texts = [
        "In a historic move, a coalition of global leaders has reached a tentative agreement to combat climate change by significantly reducing carbon emissions over the next two decades. The agreement, which follows years of intense negotiations, aims to limit global temperature rise to 1.5°C above pre-industrial levels. However, critics argue that the agreement lacks strict enforcement mechanisms, raising concerns about its effectiveness. Some developing nations have expressed skepticism, stating that wealthier countries should bear a greater share of the financial burden. Despite these concerns, environmental advocates have praised the agreement as a crucial step forward, emphasizing the need for global cooperation in addressing climate change."
    ]
    
    reference_summaries = [
        "Global leaders have agreed to cut carbon emissions to limit temperature rise to 1.5°C. The deal follows years of negotiation, but critics warn of weak enforcement. Developing nations argue wealthier countries should contribute more. Environmentalists call it a crucial step for climate action."
    ]
    
    # Evaluate fine-tuned model
    logger.info("Evaluating fine-tuned BART model...")
    fine_tuned_scores = evaluate_model(fine_tuned_model_path, texts, reference_summaries)
    
    # Print average scores for fine-tuned model
    logger.info("\n===== Fine-tuned BART Model Average ROUGE Scores =====\n")
    for metric, (precision, recall, f1) in fine_tuned_scores.items():
        logger.info(f"{metric.upper()}: Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
    
    # Evaluate base model if needed
    try:
        logger.info("\nEvaluating base BART model...\n\n")
        base_scores = evaluate_model(base_model_path, texts, reference_summaries)
        
        # Print average scores for base model
        logger.info("\n===== Base BART Model Average ROUGE Scores =====")
        for metric, (precision, recall, f1) in base_scores.items():
            logger.info(f"{metric.upper()}: Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
        
        # Compare models
        logger.info("\n===== Model Comparison (F1 Score Difference) =====")
        for metric in fine_tuned_scores.keys():
            diff = fine_tuned_scores[metric][2] - base_scores[metric][2]
            logger.info(f"{metric.upper()}: {diff:.4f} ({'better' if diff > 0 else 'worse'} than base model)")
    except Exception as e:
        logger.error(f"Error evaluating base model: {str(e)}")
        logger.info("Skipping base model evaluation.")
