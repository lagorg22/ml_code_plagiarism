import os
import torch
from transformers import AutoTokenizer, AutoModel
import faiss
import numpy as np
import pickle
import json
from tqdm import tqdm

# Configuration
CODEFILES_DIR = "codefiles"  # Directory with processed code files
EMBEDDINGS_DIR = "embeddings"  # Directory to store embeddings and metadata
MODEL_NAME = "microsoft/codebert-base"
MAX_LENGTH = 512  # Maximum sequence length for CodeBERT
BATCH_SIZE = 4  # Adjust based on your CPU memory

# Create output directory if it doesn't exist
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

# Load model and tokenizer
print("Loading CodeBERT model and tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

# Set model to evaluation mode
model.eval()

def get_embedding(code_text):
    """Generate an embedding for a given code snippet"""
    # Tokenize the code
    inputs = tokenizer(code_text, padding="max_length", truncation=True, 
                       max_length=MAX_LENGTH, return_tensors="pt")
    
    # Get the model outputs
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Use the [CLS] token embedding as the code representation
    # The [CLS] token is the first token in the sequence
    embedding = outputs.last_hidden_state[:, 0, :].numpy()
    return embedding[0]  # Return the embedding as a 1D array

def process_files_in_batches():
    """Process all code files and generate embeddings in batches"""
    # Get list of all code files                                                                                    #extensions are temporary for testing
    all_files = [f for f in os.listdir(CODEFILES_DIR) if os.path.isfile(os.path.join(CODEFILES_DIR, f)) if f.endswith(('.js', '.html', '.xml'))]
    
    # Prepare to store embeddings and metadata
    all_embeddings = []
    metadata = []
    
    print(f"Processing {len(all_files)} code files...")
    for i in tqdm(range(0, len(all_files), BATCH_SIZE)):
        batch_files = all_files[i:i+BATCH_SIZE]
        
        for file_name in batch_files:
            file_path = os.path.join(CODEFILES_DIR, file_name)
            
            # Read code content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code_content = f.read()
            
            # Generate embedding
            try:
                embedding = get_embedding(code_content)
                all_embeddings.append(embedding)
                
                # Store metadata
                metadata.append({
                    "file_name": file_name,
                    "original_path": file_path,
                    "embedding_index": len(all_embeddings) - 1,
                    "code_len": len(code_content)
                })
            except Exception as e:
                print(f"Error processing {file_name}: {str(e)}")
    
    return np.array(all_embeddings), metadata

def create_faiss_index(embeddings):
    """Create a FAISS index from embeddings"""
    print("Creating FAISS index...")
    # Get the dimensionality of the embeddings
    d = embeddings.shape[1]
    
    # Create the index - using L2 distance (Euclidean)
    index = faiss.IndexFlatL2(d)
    
    # Add the embeddings to the index
    index.add(embeddings)
    
    return index

def main():
    # Generate embeddings for all code files
    embeddings, metadata = process_files_in_batches()
    
    # Create FAISS index
    index = create_faiss_index(embeddings)
    
    # Save the FAISS index
    print("Saving FAISS index...")
    faiss.write_index(index, os.path.join(EMBEDDINGS_DIR, "code_embeddings.index"))
    
    # Save metadata
    print("Saving metadata...")
    with open(os.path.join(EMBEDDINGS_DIR, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Save raw embeddings for future use if needed
    print("Saving raw embeddings...")
    with open(os.path.join(EMBEDDINGS_DIR, "raw_embeddings.pkl"), "wb") as f:
        pickle.dump(embeddings, f)
    
    print(f"Successfully processed {len(metadata)} files. Embeddings saved to {EMBEDDINGS_DIR}")

if __name__ == "__main__":
    main()