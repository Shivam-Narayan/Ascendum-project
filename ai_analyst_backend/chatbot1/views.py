# # views.py
# import uuid, time, numpy as np
# from datetime import datetime
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from django.conf import settings

# from .mongo_utils import get_mongo_db

# # Import processors / models from your multiple.py (must be import-safe)
# from chatbot.MultipleUpload import AdvancedPDFProcessor, AdvancedWordProcessor, AI_MODELS, CONFIG

# # optionally fallback embedder
# from sentence_transformers import SentenceTransformer

# # db = get_mongo_db()
# # documents_col = db["documents"]
# # chunks_col = db["chunks"]

# # # helper: convert numpy to list (and normalize)
# # def _normalize_and_list(emb: np.ndarray) -> list:
# #     norm = np.linalg.norm(emb)
# #     if norm > 0:
# #         emb = emb / norm
# #     return emb.astype(float).tolist()

# # @api_view(['POST'])
# # @permission_classes([AllowAny])
# # def upload_document(request):
# #     """
# #     Multipart/form-data:
# #       - files: one or more uploaded files
# #       - username (optional)
# #       - source (optional)
# #     """
# #     files = request.FILES.getlist('files')
# #     username = request.data.get('username', 'anonymous')
# #     source = request.data.get('source', 'upload_api')

# #     if not files:
# #         return Response({"error": "No files provided"}, status=400)

# #     embed_model = AI_MODELS.get('embed_model') if hasattr(AI_MODELS, 'get') else AI_MODELS
# #     if not embed_model:
# #         # fallback
# #         embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# #     saved_documents = []

# #     for f in files:
# #         file_name = f.name
# #         file_type = (file_name.split('.')[-1] or "").lower()
# #         document_id = str(uuid.uuid4())
# #         uploaded_at = datetime.utcnow().isoformat()

# #         # Insert document metadata
# #         documents_col.insert_one({
# #             "_id": document_id,
# #             "filename": file_name,
# #             "file_type": file_type,
# #             "uploaded_by": username,
# #             "uploaded_at": uploaded_at,
# #             "source": source,
# #             "num_chunks": 0
# #         })

# #         # PROCESS: delegate to multiple.py processors
# #         chunks = []
# #         try:
# #             if file_type == "pdf":
# #                 processor = AdvancedPDFProcessor(ollama_client=AI_MODELS.get('ollama') if isinstance(AI_MODELS, dict) else None)
# #                 result = processor.process_pdf_fast(f)
# #                 chunks = result.get('chunks', [])
# #             elif file_type in ("docx", "doc"):
# #                 processor = AdvancedWordProcessor(ollama_client=AI_MODELS.get('ollama') if isinstance(AI_MODELS, dict) else None)
# #                 result = processor.process_word_fast(f)
# #                 chunks = result.get('chunks', [])
# #             elif file_type in ("csv", "xls", "xlsx"):
# #                 # simple CSV -> create text chunks (you can import a CSV chunk helper from multiple.py if available)
# #                 import pandas as pd
# #                 f.seek(0)
# #                 if file_type == "csv":
# #                     df = pd.read_csv(f)
# #                 else:
# #                     df = pd.read_excel(f)
# #                 # create row-based chunks (simple)
# #                 for i, row in df.iterrows():
# #                     text = " | ".join([f"{c}: {str(row[c])}" for c in df.columns])
# #                     chunks.append({"id": i, "content": text, "page": 0})
# #             else:
# #                 # unknown type: read bytes -> store small chunk of raw text
# #                 f.seek(0)
# #                 data = f.read().decode(errors='ignore') if hasattr(f, "read") else ""
# #                 chunks = [{"id": 0, "content": data, "page": 0}]
# #         except Exception as e:
# #             # cleanup document entry
# #             documents_col.delete_one({"_id": document_id})
# #             return Response({"error": f"Processing failed for {file_name}: {str(e)}"}, status=500)

# #         # EMBEDDINGS: batch encode in manageable batches
# #         texts = [c.get('content', '') for c in chunks]
# #         # optionally respect CONFIG.chunk_size or max length
# #         embeddings = []
# #         if texts:
# #             batch_size = 64
# #             for i in range(0, len(texts), batch_size):
# #                 batch_texts = texts[i:i+batch_size]
# #                 emb_batch = embed_model.encode(batch_texts, convert_to_numpy=True)
# #                 embeddings.append(emb_batch)
# #             embeddings = np.vstack(embeddings)
# #             # normalize
# #             norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
# #             norms[norms == 0] = 1.0
# #             embeddings = embeddings / norms
# #         else:
# #             embeddings = np.zeros((0, 384))  # fallback

# #         # Prepare chunk docs for Mongo
# #         to_insert = []
# #         for idx, c in enumerate(chunks):
# #             doc = {
# #                 "document_id": document_id,
# #                 "chunk_id": int(c.get('id', idx)),
# #                 "page": int(c.get('page', 0)),
# #                 "content": c.get('content', '')[:5000],  # limit field size if necessary
# #                 "embedding": _normalize_and_list(embeddings[idx]) if texts else [],
# #                 "metadata": {
# #                     "filename": file_name,
# #                     "file_type": file_type,
# #                     "uploaded_by": username
# #                 },
# #                 "created_at": datetime.utcnow().isoformat()
# #             }
# #             to_insert.append(doc)

# #         if to_insert:
# #             chunks_col.insert_many(to_insert)
# #             documents_col.update_one({"_id": document_id}, {"$set": {"num_chunks": len(to_insert)}})

# #         saved_documents.append({"document_id": document_id, "filename": file_name, "num_chunks": len(to_insert)})

# #     return Response({"status": "ok", "documents": saved_documents})



# # views.py (append)
# import numpy as np
# from bson import ObjectId

# def _cosine_similarities_matrix(vec, matrix):
#     # vec: 1D numpy, matrix: 2D numpy (n x dim)
#     # both normalized -> dot product is cosine similarity
#     return matrix.dot(vec)


# # @api_view(['POST'])
# # @permission_classes([AllowAny])
# # def query_document(request):
# #     """
# #     JSON body:
# #       {
# #         "query": "find invoice number",
# #         "top_k": 5,
# #         "document_id": "<optional filter>",
# #         "filename": "<optional filter>"
# #       }
# #     """
# #     data = request.data
# #     query = data.get("query", "")
# #     if not query:
# #         return Response({"error": "No query provided"}, status=400)

# #     top_k = int(data.get("top_k", 50))
# #     if "summarize" in query.lower():
# #         top_k = max(top_k, 100)
# #     document_id = data.get("document_id", None)
# #     filename = data.get("filename", None)

# #     # === Embedding model ===
# #     embed_model = AI_MODELS.get('embed_model') if hasattr(AI_MODELS, 'get') else AI_MODELS
# #     if not embed_model:
# #         embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# #     q_emb = embed_model.encode([query], convert_to_numpy=True)[0]
# #     q_emb = q_emb / np.linalg.norm(q_emb)

# #     # === Build Mongo filter ===
# #     mongo_filter = {}

# #     # Priority 1: explicit document_id
# #     if document_id:
# #         mongo_filter["document_id"] = document_id

# #     # Priority 2: filename -> resolve to document_id
# #     elif filename:
# #         doc_meta = documents_col.find_one({"filename": filename})
# #         if doc_meta:
# #             mongo_filter["document_id"] = doc_meta["_id"]

# #     # Optional text filter
# #     if "filter_text" in data:
# #         mongo_filter["$text"] = {"$search": data["filter_text"]}

# #     # === Fetch candidate chunks ===
# #     cursor = chunks_col.find(
# #         mongo_filter,
# #         {"content": 1, "embedding": 1, "document_id": 1, "page": 1, "metadata": 1}
# #     ).limit(2000)

# #     docs = list(cursor)
# #     if not docs:
# #         return Response({"results": [], "answer": None})

# #     embeddings = np.array([d.get("embedding", []) for d in docs], dtype=np.float32)
# #     if embeddings.size == 0:
# #         return Response({"error": "No embeddings found for stored chunks"}, status=500)

# #     # === Similarity search ===
# #     sims = embeddings.dot(q_emb)
# #     top_idx = np.argsort(sims)[-top_k:][::-1]

# #     results = []
# #     for idx in top_idx:
# #         d = docs[int(idx)]
# #         results.append({
# #             "chunk_id": str(d.get("_id")),   # ✅ cast ObjectId to string
# #             "document_id": d.get("document_id"),
# #             "page": d.get("page"),
# #             "content": d.get("content"),
# #             "score": float(sims[idx]),
# #             "metadata": d.get("metadata", {})
# #         })

# #     # === Generate final answer using Ollama if available ===
# #     final_answer = None
# #     ollama_client = AI_MODELS.get('ollama') if isinstance(AI_MODELS, dict) else None
# #     ollama_model = AI_MODELS.get('ollama_model') if isinstance(AI_MODELS, dict) else None

# #     if ollama_client and ollama_model:
# #         try:
# #             context_text = "\n\n".join([r["content"] for r in results])
# #             prompt = f"Answer the question based on the following text:\n\n{context_text}\n\nQuestion: {query}"
            
# #             response = ollama_client.generate(
# #                 model=ollama_model,
# #                 prompt=prompt,
# #                 stream=False
# #             )
# #             final_answer = response.get("response", "").strip()
# #         except Exception as e:
# #             final_answer = f"[Answer generation failed: {str(e)}]"

# #     return Response({
# #         "query": query,
# #         "answer": final_answer,
# #         "results": results
# #     })



# # from sentence_transformers import SentenceTransformer
# # from pymongo import MongoClient
# # import uuid

# # # Connect to Atlas
# # client = MongoClient("mongodb+srv://santoshjalahalli521_db_user:<db_password>@cluster0.7xex5jb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
# # db = client["chatbot_db"]
# # vectors_col = db["vectors"]

# # # Load embedding model
# # model = SentenceTransformer("all-MiniLM-L6-v2")

# # def store_document(filename, content_chunks):
# #     document_id = str(uuid.uuid4())
# #     for i, chunk in enumerate(content_chunks):
# #         emb = model.encode([chunk], convert_to_numpy=True)[0].tolist()
# #         vectors_col.insert_one({
# #             "document_id": document_id,
# #             "page": i+1,
# #             "content": chunk,
# #             "embedding": emb,
# #             "metadata": {"filename": filename}
# #         })




# import uuid
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from sentence_transformers import SentenceTransformer
# from pymongo import MongoClient
# import fitz  # PyMuPDF for PDF reading

# # Connect to Atlas
# client = MongoClient("mongodb+srv://santoshjalahalli521_db_user:yD2LvqIMK6d9WkDm@cluster0.7xex5jb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
# db = client["chatbot_db"]
# vectors_col = db["vectors"]

# # Embedding model
# embed_model = SentenceTransformer("all-MiniLM-L6-v2")


# import os

# UPLOAD_DIR = "uploaded_files"  # or any path you want

# # make sure the directory exists
# os.makedirs(UPLOAD_DIR, exist_ok=True)


# import csv, os
# import docx

# import os
# import uuid
# import csv
# import fitz
# import docx
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response

# UPLOAD_DIR = "uploaded_files"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# def chunk_file(file_path, file_type):
#     chunks = []
#     if file_type == "pdf":
#         doc = fitz.open(file_path)
#         for i, page in enumerate(doc):
#             text = page.get_text("text").strip()
#             if text:
#                 chunks.append({"page": i+1, "content": text})
#     elif file_type == "txt":
#         with open(file_path, "r", encoding="utf-8") as f:
#             text = f.read()
#         chunks.append({"page": 1, "content": text})
#     elif file_type == "csv":
#         with open(file_path, "r", encoding="utf-8") as f:
#             reader = csv.reader(f)
#             rows = [" ".join(row) for row in reader]
#         text = "\n".join(rows)
#         chunks.append({"page": 1, "content": text})
#     elif file_type == "docx":
#         doc = docx.Document(file_path)
#         text = "\n".join([para.text for para in doc.paragraphs])
#         chunks.append({"page": 1, "content": text})
#     else:
#         raise ValueError(f"Unsupported file type: {file_type}")
#     return chunks


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def upload_document(request):
#     file = request.FILES.get("file")
#     if not file:
#         return Response({"error": "No file uploaded"}, status=400)

#     tmp_path = os.path.join(UPLOAD_DIR, file.name)
#     with open(tmp_path, "wb+") as f:
#         for chunk in file.chunks():
#             f.write(chunk)

#     # detect file type
#     ext = file.name.split(".")[-1].lower()

#     try:
#         chunks = chunk_file(tmp_path, ext)
#     except ValueError as e:
#         return Response({"error": str(e)}, status=400)

#     document_id = str(uuid.uuid4())

#     for chunk in chunks:
#         emb = embed_model.encode([chunk["content"]], convert_to_numpy=True)[0].tolist()
#         vectors_col.insert_one({
#             "document_id": document_id,
#             "page": chunk["page"],
#             "content": chunk["content"],
#             "embedding": emb,
#             "metadata": {"filename": file.name}
#         })

#     return Response({"message": f"Uploaded {len(chunks)} chunks", "document_id": document_id})



# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from sentence_transformers import SentenceTransformer
# import numpy as np

# # Atlas Mongo client (already defined earlier)
# # client = MongoClient("your-atlas-connection-string")

# documents_col = db["documents"]   # if you are storing metadata separately
# chunks_col = db["vectors"] 
# # Embedding model (reuse same one as upload)
# embed_model = SentenceTransformer("all-MiniLM-L6-v2")


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def query_document(request):
#     data = request.data
#     query = data.get("query", "")
#     if not query:
#         return Response({"error": "No query provided"}, status=400)

#     top_k = int(data.get("top_k", 5))
#     document_id = data.get("document_id", None)
#     filename = data.get("filename", None)

#     # === Embedding model ===
#     q_emb = embed_model.encode([query], convert_to_numpy=True)[0].tolist()

#     # === Build filter (optional) ===
#     filters = {}
#     if document_id:
#         filters["document_id"] = document_id
#     elif filename:
#         filters["metadata.filename"] = filename   # since filename is stored inside metadata

#     # === Vector search in Atlas ===
#     vector_stage = {
#         "$vectorSearch": {
#             "index": "embedding_index",
#             "path": "embedding",
#             "queryVector": q_emb,
#             "numCandidates": 200,
#             "limit": top_k
#         }
#     }

#     if filters:
#         vector_stage["$vectorSearch"]["filter"] = filters

#     pipeline = [
#         vector_stage,
#         {
#             "$project": {
#                 "_id": {"$toString": "$_id"},
#                 "document_id": 1,
#                 "page": 1,
#                 "content": 1,
#                 "metadata": 1,
#                 "score": {"$meta": "vectorSearchScore"}
#             }
#         }
#     ]

#     results = list(chunks_col.aggregate(pipeline))

#     # === Generate final answer (optional, only if Ollama configured) ===
#     final_answer = None
#     try:
#         ollama_client = AI_MODELS.get('ollama') if isinstance(AI_MODELS, dict) else None
#         ollama_model = AI_MODELS.get('ollama_model') if isinstance(AI_MODELS, dict) else None

#         if results and ollama_client and ollama_model:
#             context_text = "\n\n".join([r["content"] for r in results])
#             prompt = f"Answer the question based on the following text:\n\n{context_text}\n\nQuestion: {query}"
#             response = ollama_client.generate(
#                 model=ollama_model,
#                 prompt=prompt,
#                 stream=False
#             )
#             final_answer = response.get("response", "").strip()
#     except Exception as e:
#         final_answer = f"[Answer generation failed: {str(e)}]"

#     return Response({
#         "query": query,
#         "answer": final_answer,
#         "results": results
#     })
