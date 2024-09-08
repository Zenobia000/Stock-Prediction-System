import logging
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
import yaml
import json

# MongoDBManager 定義部分
class ConfigLoader:
    def __init__(self, config_path='D:\python_workspace\Sunny_side_project\stock_war_room_system\config\config.yaml'):
        self.config = self.load_config(config_path)

    def load_config(self, config_path):
        """讀取 YAML 設定檔"""
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config

class MongoDBManager:
    def __init__(self, config):
        """初始化 MongoDB 連接"""
        self.uri = config['database']['mongodb']['uri']
        self.db_name = config['database']['mongodb']['name']
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]

    def get_collection(self, collection_name):
        """取得 MongoDB 集合"""
        return self.db[collection_name]

    def create_many_with_deduplication(self, collection_name, data_list):
        """
        批量插入資料，並處理以下兩種情況：
        1. 資料有唯一值（如 news_id）。
        2. 資料內容完全相同的重複資料。
        """
        try:
            collection = self.get_collection(collection_name)

            # 1. 檢查重複的 news_id
            existing_news_ids = collection.find(
                {"news_id": {"$in": [data['news_id'] for data in data_list]}},
                {"news_id": 1}
            )
            existing_ids = {doc['news_id'] for doc in existing_news_ids}

            # 過濾掉已存在的 news_id 的資料
            new_data_list = [data for data in data_list if data['news_id'] not in existing_ids]

            # 2. 檢查資料內容完全相同的情況
            for data in new_data_list[:]:  # 使用切片來創建副本，以免在迴圈中修改
                existing_doc = collection.find_one({
                    "url": data['url'],
                    "title": data['title'],
                    "content": data['content'],
                    "keyword": data['keyword'],
                    "publish_at": data['publish_at']
                })
                if existing_doc:
                    logging.info(f"Duplicated document found with same content: {data['url']}")
                    new_data_list.remove(data)

            # 插入去重後的資料
            if new_data_list:
                result = collection.insert_many(new_data_list)
                logging.info(f"Inserted new MongoDB document IDs: {result.inserted_ids}")
                return [str(inserted_id) for inserted_id in result.inserted_ids]
            else:
                logging.info(
                    "No new documents to insert. All provided documents are either duplicates or already exist.")
                return []

        except PyMongoError as e:
            logging.error(f"MongoDB batch insertion error with deduplication: {e}")
            raise

    def find_with_filter(self, collection_name, filter_criteria):
        """批量查詢文件"""
        try:
            collection = self.get_collection(collection_name)
            documents = collection.find(filter_criteria)
            return list(documents)
        except Exception as e:
            logging.error(f"MongoDB read error: {e}")
            raise

    def update_many(self, collection_name, filter_criteria, updated_data):
        """批量更新文件"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_many(filter_criteria, {"$set": updated_data})
            logging.info(f"Updated {result.matched_count} documents.")
            return result.matched_count
        except Exception as e:
            logging.error(f"MongoDB update error: {e}")
            raise

    def delete_many(self, collection_name, filter_criteria):
        """批量刪除文件"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_many(filter_criteria)
            logging.info(f"Deleted {result.deleted_count} documents.")
            return result.deleted_count
        except Exception as e:
            logging.error(f"MongoDB delete error: {e}")
            raise

    def create_one(self, collection_name, data):
        """插入單筆文件"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(data)
            logging.info(f"Inserted MongoDB document ID: {result.inserted_id}")
            return str(result.inserted_id)
        except PyMongoError as e:
            logging.error(f"MongoDB insertion error: {e}")
            raise

    def read_one(self, collection_name, document_id):
        """查詢單筆文件"""
        try:
            collection = self.get_collection(collection_name)
            document = collection.find_one({"_id": ObjectId(document_id)})
            if document:
                logging.info(f"MongoDB document found: {document}")
            else:
                logging.warning(f"MongoDB document with ID {document_id} not found.")
            return document
        except PyMongoError as e:
            logging.error(f"MongoDB read error: {e}")
            raise

    def update_one(self, collection_name, document_id, updated_data):
        """更新單筆文件"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_one({"_id": ObjectId(document_id)}, {"$set": updated_data})
            if result.matched_count > 0:
                logging.info(f"MongoDB document with ID {document_id} updated.")
            else:
                logging.warning(f"MongoDB document with ID {document_id} not found.")
            return result.matched_count
        except PyMongoError as e:
            logging.error(f"MongoDB update error: {e}")
            raise

    def delete_one(self, collection_name, document_id):
        """刪除單筆文件"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one({"_id": ObjectId(document_id)})
            if result.deleted_count > 0:
                logging.info(f"MongoDB document with ID {document_id} deleted.")
            else:
                logging.warning(f"MongoDB document with ID {document_id} not found.")
            return result.deleted_count
        except PyMongoError as e:
            logging.error(f"MongoDB delete error: {e}")
            raise

if __name__ == "__main__":
    # 加載配置
    config_loader = ConfigLoader()
    config = config_loader.config

    # 創建 MongoDBManager 實例
    mongo_manager = MongoDBManager(config)

    file_path = "D:\python_workspace\Sunny_side_project\stock_war_room_system\data\processed\stock_news_extraction.json"
    with open(file_path, 'r') as file:
        data_list = json.load(file)  # 將 JSON 資料解析成 Python 字典

    # # 批量新增文件 demo data
    # data_list = [
    #     {'news_id': 5708339, 'url': 'https://news.cnyes.com/news/id/5708339', 'title': '日銀成員再談鷹調...',
    #      'content': '...', 'keyword': ['升息', '日元', '薪資'], 'publish_at': '2024-09-05 11:25:01'},
    #     {'news_id': 5708340, 'url': 'https://news.cnyes.com/news/id/5708340', 'title': '全球股市上漲...',
    #      'content': '...', 'keyword': ['股市', '經濟'], 'publish_at': '2024-09-05 12:25:01'}
    # ]

    # 批量插入資料
    inserted_ids = mongo_manager.create_many_with_deduplication('stock_news', data_list)
    logging.info(f"Inserted news IDs: {inserted_ids}")

    # 查詢資料
    filter_criteria = {"news_id": {"$in": [5708339, 5708340]}}
    documents = mongo_manager.find_with_filter('stock_news', filter_criteria)
    for doc in documents:
        logging.info(f"Found document: {doc}")

    # 批量更新資料
    update_criteria = {"news_id": {"$in": [5708339, 5708340]}}
    updated_data = {"status": "archived"}
    updated_count = mongo_manager.update_many('stock_news', update_criteria, updated_data)
    logging.info(f"Updated {updated_count} documents.")

    # 再次查詢以確認更新結果
    updated_documents = mongo_manager.find_with_filter('stock_news', update_criteria)
    for doc in updated_documents:
        logging.info(f"Updated document: {doc}")

    # 批量刪除資料
    # delete_criteria = {"news_id": {"$in": [5708339, 5708340]}}
    # deleted_count = mongo_manager.delete_many('stock_news', delete_criteria)
    # logging.info(f"Deleted {deleted_count} documents.")

