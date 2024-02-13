from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

import os
import numpy as np


app = Flask(__name__)

# Đảm bảo rằng MODEL_WEIGHTS_PATH môi trường được đặt chính xác
model_path = os.getenv('MODEL_WEIGHTS_PATH', '.')
model = SentenceTransformer(model_path + '/vietnamese-sbert')
# Sửa địa chỉ host nếu cần, ví dụ sử dụng 'host.docker.internal' nếu chạy Docker trên Mac hoặc Windows
client = QdrantClient(host='qdrant-container', port=6333)

@app.route('/', methods=['POST'])
def embed_query():
    try:
        # Lấy query từ request body
        data = request.json
        query = data.get('query')
        collection_name = data.get('collection')

        if not query or not collection_name:
            return jsonify({"error": "Query or collection name is missing"}), 400

        # Embed query thành vector
        vector = model.encode([query])[0]  # Chỉ lấy vector đầu tiên
        # Tạo hoặc tái tạo collection với cấu hình vector
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=len(vector), distance=Distance.COSINE),
        )

        # Tạo điểm dữ liệu để upload
        points = [
            PointStruct(
                id=1,  # Xem xét sử dụng ID động hoặc duy nhất
                vector=vector.tolist(),
                payload={}
            )
        ]

        # Upload điểm dữ liệu
        client.upsert(
            collection_name=collection_name,
            points=points
        )
        # # Trả về vector (tuỳ vào yêu cầu của bạn, bạn có thể không muốn trả về vector)
        return jsonify({"vector": vector.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
