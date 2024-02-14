sudo docker pull qdrant/qdrant 
sudo docker network create vector-database-network
sudo docker run --network vector-database-network --name qdrant-container -p 6-333:6333 -v /home/ubuntu/qdrant_data/:/qdrant/storage -d qdrant/qdrant
sudo docker run --network vector-database-network -p 80:80 -v /home/ubuntu/temp_data/:/home/ubuntu/temp_data/ sentence-embedding-model:latest_2
