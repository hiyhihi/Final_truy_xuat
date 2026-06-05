from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
# max sequence = 4000 => chọn top k cho hợp lý 
# Khởi tạo ứng dụng FastAPI
app = FastAPI()

# 1. Khởi tạo Embedding Model (chạy trên CPU)
embedding_model = SentenceTransformer('keepitreal/vietnamese-sbert', device='cpu')

# 2. Setup VectorDB đơn giản lưu trên RAM
vector_db = {
    "chunks": [],
    "embeddings": []
}

# Khởi tạo OpenAI Client trỏ về Proxy của Teacher Server [cite: 128, 129, 131]
# Dùng MSSV làm API KEY [cite: 132]
proxy_client = OpenAI(
    base_url="http://192.168.50.218:8000/api/v1/proxy",
    api_key="B22DCAT149" 
)

# --- KHAI BÁO CÁC SCHEMA ---

class UploadRequest(BaseModel):
    doc_id: Optional[str] = None # [cite: 157]
    text: str # [cite: 158]

class UploadResponse(BaseModel):
    status: str # [cite: 160]
    doc_id: Optional[str] = None # [cite: 161]
    chunks: int # [cite: 162]

class AskRequest(BaseModel):
    question: str # [cite: 194]

class AskResponse(BaseModel):
    answer: str # [cite: 197]
    sources: List[str] = [] # [cite: 198]

# --- XÂY DỰNG ENDPOINTS ---

@app.post("/upload", response_model=UploadResponse)
async def upload_document(req: UploadRequest):
    # Sử dụng Langchain Text Splitter để cắt đoạn văn bản
    print("\n" + "="*50)
    print("📥 NHẬN ĐƯỢC TÀI LIỆU TỪ TEACHER SERVER")
    print(f"- Doc ID: {req.doc_id}")
    # Chỉ in 200 ký tự đầu cho đỡ rối màn hình
    print(f"- Nội dung: {req.text[:200]}...") 
    print("="*50 + "\n")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_text(req.text)
    
    # Tạo embeddings cho các chunks
    embeddings = embedding_model.encode(chunks)
    
    # Lưu vào VectorDB (reset dữ liệu cũ để tránh tràn RAM hoặc nhiễu)
    vector_db["chunks"] = chunks
    vector_db["embeddings"] = embeddings
    
    # Trả về kết quả theo đúng schema [cite: 163, 164, 165, 166, 167, 168]
    return UploadResponse(
        status="success",
        doc_id=req.doc_id,
        chunks=len(chunks)
    )

@app.post("/ask", response_model=AskResponse)
async def ask_question(req: AskRequest):
    print("\n" + "-"*50)
    print(f"❓ TEACHER HỎI: {req.question}")
    # 1. Mã hóa câu hỏi để so sánh
    question_embedding = embedding_model.encode([req.question])
    
    # 2. Tìm kiếm nội dung liên quan (Retrieve) bằng Cosine Similarity
    if len(vector_db["embeddings"]) == 0:
        return AskResponse(answer="A", sources=["No context available"])
        
    similarities = cosine_similarity(question_embedding, vector_db["embeddings"])[0]
    
    # Lấy top 3 chunks có độ tương đồng cao nhất
    top_k_indices = np.argsort(similarities)[-3:][::-1]
    retrieved_contexts = [vector_db["chunks"][i] for i in top_k_indices]
    context_text = "\n---\n".join(retrieved_contexts)
    
    # 3. Tạo Prompt ép LLM trả lời 1 ký tự
    prompt = f"""Câu hỏi trắc nghiệm:
{req.question}

Ngữ cảnh liên quan:
{context_text}

Trả lời bằng 1 ký tự: A, B, C hoặc D. Chỉ viết ký tự, không giải thích."""

    # 4. Gọi LLM qua Proxy [cite: 126, 133, 134, 135, 136]
    response = proxy_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    
    answer_text = response.choices[0].message.content.strip()
    
    # Clean đáp án để đảm bảo đúng quy định 1 ký tự [cite: 190]
    valid_answers = ["A", "B", "C", "D"]
    final_answer = answer_text[0].upper() if answer_text and answer_text[0].upper() in valid_answers else "A"
    
    print(f"✅ LLM TRẢ LỜI ĐÁP ÁN: {final_answer}")
    print("-"*50 + "\n")

    return AskResponse(
        answer=final_answer,
        sources=retrieved_contexts
    )

# uv run uvicorn main:app --host 192.168.50.67 --port 5000
# uv run python trigger.py
