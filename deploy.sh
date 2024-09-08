#!/bin/bash

# 參數設置
IMAGE_NAME="stock-war-room-system-image"
CONTAINER_NAME="stock-war-room-system"
HOST_PORT=8888
CONTAINER_PORT=8888
DOCKERHUB_USERNAME="sunnyntuee"
DOCKERHUB_REPO="ispan-project-demo"
TAG="latest"

# 本機資料夾和容器資料夾的綁定
HOST_DATA_DIR="$(pwd)/data"
CONTAINER_DATA_DIR="/app/data"
HOST_NOTEBOOKS_DIR="$(pwd)/notebooks"
CONTAINER_NOTEBOOKS_DIR="/app/notebooks"

# 構建 Docker 映像
echo "Building Docker image..."
docker build -t $IMAGE_NAME .

# 停止並刪除現有容器（如果存在）
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping existing container..."
    docker stop $CONTAINER_NAME
    echo "Removing existing container..."
    docker rm $CONTAINER_NAME
fi

# 啟動新的容器，並加入 volume 綁定
echo "Starting new container with volume bindings..."
docker run -d \
  -p $HOST_PORT:$CONTAINER_PORT \
  --name $CONTAINER_NAME \
  -v $HOST_DATA_DIR:$CONTAINER_DATA_DIR \
  -v $HOST_NOTEBOOKS_DIR:$CONTAINER_NOTEBOOKS_DIR \
  $IMAGE_NAME

# 列出運行中的容器以確認成功部署
echo "Listing running containers..."
docker ps

# # 清理未使用的 Docker 映像和容器
# echo "Cleaning up old images and containers..."
# docker system prune -f

# 標記 Docker 映像，準備上傳到 Docker Hub
echo "Tagging Docker image for Docker Hub..."
docker tag $IMAGE_NAME $DOCKERHUB_USERNAME/$DOCKERHUB_REPO:$TAG

# 推送 Docker 映像到 Docker Hub
echo "Pushing Docker image to Docker Hub..."
docker push $DOCKERHUB_USERNAME/$DOCKERHUB_REPO:$TAG

echo "Deployment and Docker Hub upload complete. Jupyter Notebook is running on http://localhost:$HOST_PORT"
