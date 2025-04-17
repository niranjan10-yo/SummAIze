from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Summarization, PDF
from transformers import BartTokenizer, BartForConditionalGeneration
import torch
from sqlalchemy import text
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import re

router = APIRouter(prefix="/summary", tags=["Summarization"])
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load tokenizer and model
def load_model(model_path, fallback_model="facebook/bart-large-cnn"):
    try:
        model = BartForConditionalGeneration.from_pretrained(model_path).to(device)
        tokenizer = BartTokenizer.from_pretrained(model_path)
        print(f"Successfully loaded model from {model_path}")
        return model, tokenizer
    except Exception as e:
        print(f"Error loading model from {model_path}: {str(e)}")
        print(f"Falling back to {fallback_model}")
        model = BartForConditionalGeneration.from_pretrained(fallback_model).to(device)
        tokenizer = BartTokenizer.from_pretrained(fallback_model)
        model.save_pretrained(model_path)
        tokenizer.save_pretrained(model_path)
        return model, tokenizer

# Load both models with better error handling
print("Loading pretrained BART model...")
pretrained_model, tokenizer = load_model("./bart_model")

print("Loading fine-tuned BART model...")
try:
    fine_tuned_model, fine_tuned_tokenizer = load_model("./fine_tuned_bart")
    has_fine_tuned = True
except Exception as e:
    print(f"Could not load fine-tuned model: {str(e)}")
    fine_tuned_model = None
    fine_tuned_tokenizer = None
    has_fine_tuned = False

def chunk_text(text, chunk_size=1024, overlap=100):
    """
    Split text into chunks respecting sentence boundaries when possible.
    """
    # Split by sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_words = sentence.split()
        sentence_length = len(sentence_words)
        
        # If adding this sentence would exceed chunk size and we already have content
        if current_length + sentence_length > chunk_size and current_length > 0:
            # Add the current chunk to our list of chunks
            chunks.append(" ".join(current_chunk))
            
            # Start a new chunk with overlap
            overlap_start = max(0, len(current_chunk) - overlap)
            current_chunk = current_chunk[overlap_start:]
            current_length = len(current_chunk)
        
        # Add the sentence to the current chunk
        current_chunk.extend(sentence_words)
        current_length += sentence_length
    
    # Add the last chunk if it has content
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def ensure_complete_sentence(text):
    """Ensure the text ends with a sentence-ending punctuation."""
    if not text:
        return text
        
    # If the text doesn't end with sentence-ending punctuation, add a period
    if not re.search(r'[.!?]$', text):
        # Find the last sentence-ending punctuation
        match = re.search(r'(.*[.!?])[^.!?]*$', text)
        if match:
            # Return text up to the last complete sentence
            return match.group(1)
        else:
            # If no sentence-ending punctuation found, add a period
            return text + "."
    return text
def summarize_with_fine_tuned(text, model, tokenizer):
    """Direct summarization with fine-tuned model, optimized for longer outputs."""
    print("Using specialized fine-tuned model summarization function")
    
    # For shorter texts, try direct summarization
    if len(text.split()) < 2000:
        print("Text is short enough for direct summarization")
        
        # Truncate to fit model's max input
        inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True).to(device)
        
        # Generate with parameters optimized for longer summaries
        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=500,  # Longer max length
            min_length=100,  # Lower min length
            num_beams=6,     # More beam search paths
            length_penalty=2.0,  # Strongly favor longer outputs
            early_stopping=False,
            repetition_penalty=1.0,  # Less repetition penalty
            no_repeat_ngram_size=2,  # Less restrictive
            do_sample=True,  # Enable sampling
            top_p=0.95,      # Nucleus sampling
            temperature=0.8  # Slightly random
        )
        
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        print(f"Direct fine-tuned summary length: {len(summary.split())} words")
        return ensure_complete_sentence(summary)
    
    # For longer texts, use chunking with special parameters
    else:
        print("Text is too long, using chunked summarization")
        chunks = chunk_text(text)
        summaries = []
        
        # Parameters specifically for fine-tuned model
        min_len = max(100, len(text.split()) // 6)
        max_len = min(800, len(text.split()) // 2)
        
        for chunk in chunks:
            inputs = tokenizer(chunk, return_tensors="pt", max_length=1024, truncation=True).to(device)
            
            summary_ids = model.generate(
                inputs["input_ids"], 
                max_length=max_len, 
                min_length=min_len,
                num_beams=6, 
                length_penalty=2.0,  # Strongly encourage longer outputs
                early_stopping=False,
                repetition_penalty=1.0,  # Less repetition penalty
                no_repeat_ngram_size=2,  # Less restrictive on repeats
                do_sample=True,
                top_p=0.95,
                temperature=0.8
            )
            chunk_summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            print(f"Chunk summary length: {len(chunk_summary.split())} words")
            summaries.append(chunk_summary)
        
        joined_summary = " ".join(summaries)
        return ensure_complete_sentence(joined_summary)



def summarize_large_text(text, model, model_tokenizer=None):
    """
    Generate a summary for large text by chunking and summarizing.
    Fixed to properly handle multiple chunks and ensure complete sentences.
    """
    if model_tokenizer is None:
        model_tokenizer = tokenizer
        
    chunks = chunk_text(text)
    
    # For very long documents, use hierarchical summarization
    if len(chunks) > 3:
        # First level summarization
        first_level_summaries = []
        for chunk in chunks:
            inputs = model_tokenizer(chunk, return_tensors="pt", max_length=1024, truncation=True).to(device)
            summary_ids = model.generate(
                inputs["input_ids"], 
                max_length=300,  # Shorter for first level
                min_length=100,
                num_beams=4,
                length_penalty=1.2,
                early_stopping=False,
                repetition_penalty=1.2
            )
            chunk_summary = model_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            first_level_summaries.append(chunk_summary)
        
        # Second level summarization (summarize the summaries)
        combined_summary = " ".join(first_level_summaries)
        inputs = model_tokenizer(combined_summary, return_tensors="pt", max_length=1024, truncation=True).to(device)
        summary_ids = model.generate(
            inputs["input_ids"], 
            max_length=500,  # Longer for final summary
            min_length=200,
            num_beams=5,
            length_penalty=1.5,
            early_stopping=False,
            repetition_penalty=1.2
        )
        final_summary = model_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return ensure_complete_sentence(final_summary)
    
    # For shorter documents, summarize each chunk and join
    else:
        summaries = []
        input_length = len(text.split())
        min_len = max(150, input_length // 4)  # Adjusted for better length
        max_len = min(600, input_length // 2)  # Increased max length
        
        for chunk in chunks:
            inputs = model_tokenizer(chunk, return_tensors="pt", max_length=1024, truncation=True).to(device)
            summary_ids = model.generate(
                inputs["input_ids"], 
                max_length=max_len, 
                min_length=min_len,
                num_beams=5, 
                length_penalty=1.5,  # Increased to favor longer summaries
                early_stopping=False,  # Changed to ensure completion
                repetition_penalty=1.2, 
                no_repeat_ngram_size=3,
                forced_bos_token_id=model_tokenizer.bos_token_id,
                do_sample=False  # Ensure deterministic output
            )
            chunk_summary = model_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            summaries.append(chunk_summary)
        
        # This return statement was incorrectly indented in your original code
        joined_summary = " ".join(summaries)
        return ensure_complete_sentence(joined_summary)

@router.get("/")
def test_summary():
    return {
        "message": "Summarization module is working!",
        "models_available": {
            "pretrained": True,
            "fine_tuned": has_fine_tuned
        }
    }

class SummaryRequest(BaseModel):
    pdf_id: int
    user_id: int
    model_type: str = "pretrained"  # Changed from "model" to "model_type" for clarity

@router.post("/summarize/")
async def summarize_pdf(
    request: SummaryRequest,
    db: Session = Depends(get_db)):
    
    print(f"🔍 Incoming Request: {request}")  # Debug request
    pdf_id = request.pdf_id
    user_id = request.user_id
    model_type = request.model_type.lower()
    
    print(f"Model type requested: {model_type}")  # Add this debug line
    
    # Validate model type
    if model_type not in ["pretrained", "fine-tuned"]:
        print(f"Invalid model type: {model_type}")
        raise HTTPException(status_code=400, detail=f"Invalid model type: {model_type}. Use 'pretrained' or 'fine-tuned'")
    
    # Check if fine-tuned model is requested but not available
    if model_type == "fine-tuned" and not has_fine_tuned:
        print("Fine-tuned model requested but not available")
        raise HTTPException(status_code=400, detail="Fine-tuned model is not available")
    
    # Force regeneration of summary with the requested model
    # Comment out or remove the existing summary check to always generate a new summary
    # summary_entry = db.query(Summarization).filter(
    #     Summarization.pdf_id == pdf_id
    # ).first()
    # 
    # if summary_entry:
    #     return {"pdf_id": pdf_id, "summary": summary_entry.summary_text, "model_used": "unknown (from database)"}
    
    # Get PDF
    pdf_entry = db.query(PDF).filter(PDF.id == pdf_id).first()
    
    if not pdf_entry:
        print(f"PDF with id {pdf_id} not found.")
        raise HTTPException(status_code=404, detail="PDF not found.")
    elif not pdf_entry.text.strip():
        print(f"PDF with id {pdf_id} is empty.")
        raise HTTPException(status_code=404, detail="PDF is empty.")
    
    # Select model based on request
    if model_type == "fine-tuned":
        print("Using fine-tuned model")
        selected_model = fine_tuned_model
        selected_tokenizer = fine_tuned_tokenizer
    else:
        print("Using pretrained model")
        selected_model = pretrained_model
        selected_tokenizer = tokenizer
    
    # Generate summary
    print(f"Generating summary with {model_type} model")
    summary = summarize_large_text(pdf_entry.text, selected_model, selected_tokenizer)
    print(f"Summary generated: {summary[:100]}...")  # Print first 100 chars of summary
    
    # Save to database - optional, you can comment this out if you don't want to save
    # new_summary = Summarization(
    #     pdf_id=pdf_id, 
    #     user_id=user_id, 
    #     summary_text=summary
    # )
    # 
    # db.add(new_summary)
    # db.commit()
    
    return JSONResponse(
        content={"pdf_id": pdf_id, "summary": summary, "model_used": model_type}, 
        status_code=200
    )

@router.get("/test-models/{pdf_id}")
async def test_models(pdf_id: int, db: Session = Depends(get_db)):
    """Generate summaries with both models without saving to database"""
    
    # Get PDF
    pdf_entry = db.query(PDF).filter(PDF.id == pdf_id).first()
    if not pdf_entry:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    if not pdf_entry.text.strip():
        raise HTTPException(status_code=404, detail="PDF is empty")
    
    # Generate summaries with both models
    pretrained_summary = summarize_large_text(pdf_entry.text, pretrained_model, tokenizer)
    
    result = {
        "pdf_id": pdf_id,
        "filename": pdf_entry.filename,
        "pretrained_summary": pretrained_summary,
        "fine_tuned_summary": None
    }
    
    # Generate fine-tuned summary if available
    if has_fine_tuned:
        fine_tuned_summary = summarize_large_text(pdf_entry.text, fine_tuned_model, fine_tuned_tokenizer)
        result["fine_tuned_summary"] = fine_tuned_summary
    
    return result

@router.get("/get_all_summaries/")
async def get_all_summaries(db: Session = Depends(get_db)):
    try:
        summaries = db.execute(text("""
            SELECT pdfs.id, pdfs.filename, summarization.summary_text 
            FROM pdfs 
            INNER JOIN summarization ON pdfs.id = summarization.pdf_id
        """)).fetchall()
        
        if not summaries:
            raise HTTPException(status_code=404, detail="No summaries found")
        
        return [{"pdf_id": row[0], "filename": row[1], "summary": row[2]} for row in summaries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
