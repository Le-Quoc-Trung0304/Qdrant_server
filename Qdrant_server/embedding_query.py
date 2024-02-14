from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
import os
import numpy as np
#from docx import Document
import fitz
import boto3
import hashlib


app = Flask(__name__)

model_path = os.getenv('MODEL_WEIGHTS_PATH', '.')
model = SentenceTransformer(model_path + '/vietnamese-sbert')
client = QdrantClient(host='qdrant-container', port=6333)

def extract_chunk_from_file(file_path, chunk_size):
    # Xác định phần mở rộng của file
    _, file_extension = os.path.splitext(file_path)
    full_text = ""

    # Xử lý cho PDF
    if file_extension.lower() == '.pdf':
        with fitz.open(file_path) as doc:
                for page in doc:
                    full_text += page.get_text()

    # # Xử lý cho DOCX
    # elif file_extension.lower() == '.docx':
    #     doc = Document(file_path)
    #     for para in doc.paragraphs:
    #         full_text += para.text + '\n'

    # Xử lý cho TXT
    elif file_extension.lower() == '.txt':
        with open(file_path, 'r', encoding='utf-8') as file:
            full_text = file.read()

    else:
        raise ValueError("Unsupported file type!")

    # Logic chia text thành chunks
    chunks = []
    current_pos = 0
    while current_pos < len(full_text):
        adjusted_chunk_size = min(chunk_size, len(full_text) - current_pos)
        end_pos = current_pos + adjusted_chunk_size

        boundary = -1
        for i in range(current_pos + adjusted_chunk_size, current_pos, -1):
            if full_text[i-1:i+1] == '.\n' or (full_text[i-1] == '.' and full_text[i:i+1].isupper()):
                boundary = i
                break

        if boundary == -1:
            for i in range(current_pos + adjusted_chunk_size, current_pos, -1):
                if full_text[i-1] == '.':
                    boundary = i
                    break
            if boundary == -1:
                boundary = current_pos + adjusted_chunk_size

        chunks.append(full_text[current_pos:boundary].strip())
        current_pos = boundary

    return chunks

def download_file_from_s3(bucket_name, user_name, file_name, local_path):

    s3_key = f'{user_name}/{file_name}'
    s3 = boto3.client('s3')
    try:
        s3.download_file(bucket_name, s3_key, local_path)
        print(f"File downloaded successfully to {local_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")

@app.route('/query', methods=['POST'])
def get_query():
    try:
        data = request.json
        query = data.get('query')
        collection_name = 'user_vector_collection'
        user_name = data.get('user_name')
        file_name = data.get('file_name')

        if not query:
            return jsonify({"error": "Query is missing"}), 400

        vector = model.encode([query])[0]

        search_response = client.search(
            collection_name=collection_name,
            query_vector=vector.tolist(),
            query_filter=Filter(
                must=[
                    FieldCondition(key="user_name", match=MatchValue(value=user_name)),
                    FieldCondition(key="file_name", match=MatchValue(value=file_name))
                ]
            ),
            limit=10
        )
        results = []
        # In kết quả
        for hit in search_response:
           results.append(hit.payload)
        return jsonify({"results": results}), 200

    except Exception as e:
            # Xử lý nếu có lỗi xảy ra
            return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['PUT'])
def upload_and_process():
    if request.method == 'PUT':
        try:
            data = request.json
            user_name = data['user_name']
            file_name = data['file_name']
            bucket_name = 'chatbot-user-upload'
            local_path = '/home/ubuntu/temp_data/' + file_name  
            chunk_size = 500 

            download_file_from_s3(bucket_name, user_name, file_name, local_path)
            chunks = extract_chunk_from_file(local_path, chunk_size)
            embeddings = model.encode(chunks)

            vector_size = embeddings[0].shape[0] 
            
            collection_name = 'user_vector_collection'
            
            # client.recreate_collection(
            #     collection_name=collection_name,
            #     vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            # )

            #Tao cac point
            points = []
            for idx, vector in enumerate(embeddings):
                # point_id = f"{user_name}_{file_name}_{idx}"
                # hash_object = hashlib.sha256(point_id.encode())
                # hash_hex = hash_object.hexdigest()
                # hash_int = int(hash_hex, 16)
                point = PointStruct(
                    id=idx,
                    vector=vector.tolist(),
                    payload={"user_name": user_name, "file_name": file_name, "text": chunks[idx]}  # Giả sử bạn có chunks là list các đoạn văn bản
                )
                points.append(point)
            print(points[0])
            # Upload điểm dữ liệu
            client.upsert(
                collection_name=collection_name,
                points=points,
                wait = True,
            )

            return jsonify({'message': 'Xử lý thành công'})
        except Exception as e:
            print(f"Error processing request: {e}")
            return jsonify({'error': 'Lỗi khi xử lý yêu cầu'}), 500
        

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
