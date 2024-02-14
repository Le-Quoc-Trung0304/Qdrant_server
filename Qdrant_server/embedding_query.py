from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

import os
import numpy as np
import PyPDF2
import boto3
app = Flask(__name__)

# Đảm bảo rằng MODEL_WEIGHTS_PATH môi trường được đặt chính xác
model_path = os.getenv('MODEL_WEIGHTS_PATH', '.')
model = SentenceTransformer(model_path + '/vietnamese-sbert')
# Sửa địa chỉ host nếu cần, ví dụ sử dụng 'host.docker.internal' nếu chạy Docker trên Mac hoặc Windows
client = QdrantClient(host='qdrant-container', port=6333)

# @app.route('/query', methods=['POST'])
# def get_query():
    # try:
    #     # Lấy query từ request body
    #     data = request.json
    #     query = data.get('query')
    #     collection_name = data.get('collection')

    #     if not query or not collection_name:
    #         return jsonify({"error": "Query or collection name is missing"}), 400

    #     # Embed query thành vector
    #     vector = model.encode([query])[0]  # Chỉ lấy vector đầu tiên
    #     # Tạo hoặc tái tạo collection với cấu hình vector
        # client.recreate_collection(
        #     collection_name='First',
        #     vectors_config=VectorParams(size=len(vector), distance=Distance.COSINE),
        # )

#         # Tạo điểm dữ liệu để upload
#         points = [
#             PointStruct(
#                 id=1,  # Xem xét sử dụng ID động hoặc duy nhất
#                 vector=vector.tolist(),
#                 payload={}
#             )
#         ]

#         # Upload điểm dữ liệu
#         client.upsert(
#             collection_name=collection_name,
#             points=points
#         )
#         # # Trả về vector (tuỳ vào yêu cầu của bạn, bạn có thể không muốn trả về vector)
#         return jsonify({"vector": vector.tolist()})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def get_query():
    try:
        # Lấy thông tin từ request body
        data = request.json
        query = data.get('query')
        collection_name = data.get('collection', 'First')  # Mặc định là 'First' nếu không được cung cấp
        user_name = data.get('user_name')
        file_name = data.get('file_name')

        if not query:
            return jsonify({"error": "Query is missing"}), 400

        # Kiểm tra xem collection có tồn tại không, tạo mới nếu không tồn tại
        # collections = client.list_collections()
        # if collection_name not in [col['name'] for col in collections['result']['collections']]:
        #     # Tạo collection mới với cấu hình mặc định hoặc cấu hình cụ thể nếu bạn muốn
        #     client.create_collection(
        #         collection_name=collection_name,
        #         vectors_config=VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE)
        #     )
        #     return jsonify({"error": "No Colection"}), 401
        # Embed query thành vector
        # vector = model.encode([query])[0]  # Chỉ lấy vector đầu tiên

        # # Thực hiện tìm kiếm trên collection dựa trên vector
        # search_response = client.search(
        #     collection_name=collection_name,
        #     query_vector=vector.tolist(),
        #     query_filter={
        #         "must": [
        #             {"key": "user_name", "match": {"value": user_name}},
        #             {"key": "file_name", "match": {"value": file_name}}
        #         ]
        #     },
        #     vector_params=VectorParams(size=len(vector), distance=Distance.COSINE),
        #     top=10
        # )
        search_response = ""
        # Trả về kết quả tìm kiếm
        return jsonify(search_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_chunk_from_pdf(file, chunk_size):
    full_text = ""
    pdf = PyPDF2.PdfReader(file)
    for page in pdf.pages:
        full_text += page.extract_text() if page.extract_text() else ''
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


@app.route('/upload', methods=['PUT'])
def upload_and_process():
    if request.method == 'PUT':
        try:
            data = request.json
            user_name = data['user_name']
            file_name = data['file_name']
            bucket_name = 'chatbot-user-upload'
            local_path = '/home/ubuntu/temp_data' + file_name  
    
            download_file_from_s3(bucket_name, user_name, file_name, local_path)
            return jsonify({'message': 'Xử lý thành công'})
        except Exception as e:
            print(f"Error processing request: {e}")
            return jsonify({'error': 'Lỗi khi xử lý yêu cầu'}), 500
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
