# views.py
import uuid, time, numpy as np
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
 
from .mongo_utils import get_mongo_db
 
# Import processors / models from your multiple.py (must be import-safe)
from chatbot.MultipleUpload import AdvancedPDFProcessor, AdvancedWordProcessor, AI_MODELS, CONFIG
 
# optionally fallback embedder
from sentence_transformers import SentenceTransformer
 
# Import FAISS index
from .faiss_utils import faiss_index
 
db = get_mongo_db()
documents_col = db["documents"]
chunks_col = db["chunks"]
 
# helper: convert numpy to list (and normalize)
def _normalize_and_list(emb: np.ndarray) -> list:
    norm = np.linalg.norm(emb)
    if norm > 0:
        emb = emb / norm
    return emb.astype(float).tolist()
 
 
@api_view(['POST'])
@permission_classes([AllowAny])
def upload_document(request):
    """
    Multipart/form-data:
      - files: one or more uploaded files
      - username (optional)
      - source (optional)
    """
    files = request.FILES.getlist('files')
    username = request.data.get('username', 'anonymous')
    source = request.data.get('source', 'upload_api')
 
    if not files:
        return Response({"error": "No files provided"}, status=400)
 
    embed_model = AI_MODELS.get('embed_model') if hasattr(AI_MODELS, 'get') else AI_MODELS
    if not embed_model:
        # fallback
        embed_model = SentenceTransformer("all-MiniLM-L6-v2")
 
    saved_documents = []
 
    for f in files:
        file_name = f.name
        file_type = (file_name.split('.')[-1] or "").lower()
        document_id = str(uuid.uuid4())
        uploaded_at = datetime.utcnow().isoformat()
 
        # Insert document metadata
        documents_col.insert_one({
            "_id": document_id,
            "filename": file_name,
            "file_type": file_type,
            "uploaded_by": username,
            "uploaded_at": uploaded_at,
            "source": source,
            "num_chunks": 0
        })
 
        # PROCESS: delegate to multiple.py processors
        chunks = []
        try:
            if file_type == "pdf":
                processor = AdvancedPDFProcessor(
                    ollama_client=AI_MODELS.get('ollama') if isinstance(AI_MODELS, dict) else None
                )
                result = processor.process_pdf_fast(f)
                chunks = result.get('chunks', [])
            elif file_type in ("docx", "doc"):
                processor = AdvancedWordProcessor(
                    ollama_client=AI_MODELS.get('ollama') if isinstance(AI_MODELS, dict) else None
                )
                result = processor.process_word_fast(f)
                chunks = result.get('chunks', [])
            elif file_type in ("csv", "xls", "xlsx"):
                import pandas as pd
                f.seek(0)
                if file_type == "csv":
                    df = pd.read_csv(f)
                else:
                    df = pd.read_excel(f)
                for i, row in df.iterrows():
                    text = " | ".join([f"{c}: {str(row[c])}" for c in df.columns])
                    chunks.append({"id": i, "content": text, "page": 0})
            else:
                # unknown type: read raw bytes
                f.seek(0)
                data = f.read().decode(errors='ignore') if hasattr(f, "read") else ""
                chunks = [{"id": 0, "content": data, "page": 0}]
        except Exception as e:
            documents_col.delete_one({"_id": document_id})
            return Response({"error": f"Processing failed for {file_name}: {str(e)}"}, status=500)
 
        # EMBEDDINGS: batch encode
        texts = [c.get('content', '') for c in chunks]
        embeddings = []
        if texts:
            batch_size = 64
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i+batch_size]
                emb_batch = embed_model.encode(batch_texts, convert_to_numpy=True)
                embeddings.append(emb_batch)
            embeddings = np.vstack(embeddings)
            # normalize
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            embeddings = embeddings / norms
        else:
            embeddings = np.zeros((0, 384))  # fallback
 
        # === Save to Mongo + FAISS ===
        to_insert = []
        faiss_embeddings = []
        faiss_metas = []
 
        for idx, c in enumerate(chunks):
            emb = embeddings[idx] if texts else np.zeros((384,))
            doc = {
                "document_id": document_id,
                "chunk_id": int(c.get('id', idx)),
                "page": int(c.get('page', 0)),
                "content": c.get('content', '')[:5000],
                "embedding": _normalize_and_list(emb),
                "metadata": {
                    "filename": file_name,
                    "file_type": file_type,
                    "uploaded_by": username
                },
                "created_at": datetime.utcnow().isoformat()
            }
            to_insert.append(doc)
 
            faiss_embeddings.append(emb)
            faiss_metas.append({
                "document_id": document_id,
                "page": doc["page"],
                "content": doc["content"],
                "metadata": doc["metadata"]
            })
 
        if to_insert:
            chunks_col.insert_many(to_insert)
            documents_col.update_one({"_id": document_id}, {"$set": {"num_chunks": len(to_insert)}})
 
            # Add to FAISS
            if faiss_embeddings:
                faiss_index.add(np.array(faiss_embeddings, dtype="float32"), faiss_metas)
 
        saved_documents.append({
            "document_id": document_id,
            "filename": file_name,
            "num_chunks": len(to_insert)
        })
 
    return Response({"status": "ok", "documents": saved_documents})
 
 
# ---------------- Query API ----------------
@api_view(['POST'])
@permission_classes([AllowAny])
def query_document(request):
    """
    JSON body:
      {
        "query": "find invoice number",
        "top_k": 5,
        "document_id": "<optional filter>",
        "filename": "<optional filter>"
      }
    """
    data = request.data
    query = data.get("query", "")
    if not query:
        return Response({"error": "No query provided"}, status=400)
 
    top_k = int(data.get("top_k", 5))
    document_id = data.get("document_id", None)
    filename = data.get("filename", None)
 
    # === Embedding model ===
    embed_model = AI_MODELS.get('embed_model') if hasattr(AI_MODELS, 'get') else AI_MODELS
    if not embed_model:
        embed_model = SentenceTransformer("all-MiniLM-L6-v2")
 
    q_emb = embed_model.encode([query], convert_to_numpy=True)[0]
    q_emb = q_emb / np.linalg.norm(q_emb)
 
    # === Search FAISS ===
    results = faiss_index.search(q_emb.astype("float32"), top_k=top_k)
 
    if not results:
        return Response({"results": [], "answer": None})
 
    # Apply filters if given
    if document_id:
        results = [r for r in results if r["document_id"] == document_id]
    if filename:
        results = [r for r in results if r["metadata"].get("filename") == filename]
 
    # === Generate final answer using Ollama if available ===
    final_answer = None
    ollama_client = AI_MODELS.get('ollama') if isinstance(AI_MODELS, dict) else None
    ollama_model = AI_MODELS.get('ollama_model') if isinstance(AI_MODELS, dict) else None
 
    if ollama_client and ollama_model and results:
        try:
            context_text = "\n\n".join([r["content"] for r in results])
            prompt = f"Answer the question based on the following text:\n\n{context_text}\n\nQuestion: {query}"
 
            response = ollama_client.generate(
                model=ollama_model,
                prompt=prompt,
                stream=False
            )
            final_answer = response.get("response", "").strip()
        except Exception as e:
            final_answer = f"[Answer generation failed: {str(e)}]"
 
    return Response({
        "query": query,
        "answer": final_answer,
        "results": results
    })
 
 
@api_view(['GET'])
@permission_classes([AllowAny])
def list_documents(request):
    """
    Returns list of available documents with metadata.
    Optional query params:
      - username=<user>   (to filter by uploader)
      - filename=<name>   (to filter by file name)
    """
    username = request.GET.get("username")
    filename = request.GET.get("filename")
 
    query = {}
    if username:
        query["uploaded_by"] = username
    if filename:
        query["filename"] = filename
 
    docs = list(documents_col.find(query, {"_id": 1, "filename": 1, "file_type": 1,
                                           "uploaded_by": 1, "uploaded_at": 1,
                                           "num_chunks": 1, "source": 1}))
 
    # Convert ObjectId/UUID to string
    for d in docs:
        d["document_id"] = str(d.pop("_id"))
 
    return Response({"documents": docs})