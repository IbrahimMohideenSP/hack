import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

# Load small embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Folder where PDFs are stored
PDF_FOLDER = "policy_pdfs"

clauses = []

# Extract text from each PDF
for pdf_file in os.listdir(PDF_FOLDER):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(PDF_FOLDER, pdf_file)
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        # Split into clauses (simple split by ".")
        parts = [p.strip() for p in text.split(".") if len(p.strip()) > 20]
        clauses.extend(parts)

print(f"✅ Extracted {len(clauses)} clauses from PDFs.")

# Create embeddings
embeddings = model.encode(clauses, convert_to_numpy=True)

# Create FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Save index and clauses
faiss.write_index(index, "vector_index.faiss")
with open("clauses.pkl", "wb") as f:
    pickle.dump(clauses, f)

print("✅ FAISS index and clauses saved successfully!")
