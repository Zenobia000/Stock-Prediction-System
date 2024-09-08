version: '3.8'

services:
  mongodb:
    image: mongo:latest
    container_name: mongodb
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: root
      MONGO_INITDB_DATABASE: mydatabase  # 初始化資料庫
    ports:
      - "27017:27017"
    volumes:
      - D:/python_workspace/docker_service/db-data/mongodb:/data/db

  postgres:
    image: postgres:latest
    container_name: postgresdb
    environment:
      POSTGRES_USER: root
      POSTGRES_PASSWORD: root
      POSTGRES_DB: mydatabase
    ports:
      - "5432:5432"
    volumes:
      - D:/python_workspace/docker_service/db-data/postgres:/var/lib/postgresql/data

volumes:
  mongodb_data:
  postgres_data:
