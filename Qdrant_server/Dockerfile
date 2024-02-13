# Sử dụng một image cơ bản của Python 3.10
FROM python:3.8-slim

# Cài đặt wget, git, gcc, g++ và make - cần thiết để build fairseq và fastBPE
# Thêm git-lfs vào danh sách các gói cần cài đặt
RUN apt-get update && \
    apt-get install -y wget git gcc g++ make git-lfs && \
    apt-get clean

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Cài đặt các thư viện Python cần thiết
RUN pip install sentence-transformers qdrant_client flask PyPDF2

# Cài đặt và sử dụng git lfs
RUN git lfs install && \
    git clone https://huggingface.co/keepitreal/vietnamese-sbert

# Thêm file Python chứa hàm inference vào thư mục làm việc
COPY embedding_query.py /app/embedding_query.py

# Môi trường biến để chỉ đường dẫn mô hình, thay đổi giá trị nếu cần
ENV MODEL_WEIGHTS_PATH="/app"

# Khi container chạy, thực thi Python script (đổi tên file nếu cần)
CMD ["python", "embedding_query.py"]

#sudo docker pull qdrant/qdrant 
#sudo docker network create vector-database-network
#sudo docker run --network vector-database-network --name qdrant-container -p 6-333:6333 -v /home/ubuntu/qdrant_server/:/qdrant/storage -d qdrant/qdrant
#sudo docker run --network vector-database-network -p 80:80 sentence-embedding-model:latest_2