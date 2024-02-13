sudo docker pull qdrant/qdrant 
sudo docker network create vector-database-network
sudo docker run --network vector-database-network --name qdrant-container -p 6-333:6333 -v /home/ubuntu/qdrant_server/:/qdrant/storage -d qdrant/qdrant
sudo docker run --network vector-database-network -p 80:80 sentence-embedding-model:latest_2