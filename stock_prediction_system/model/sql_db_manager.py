import logging
from psycopg2 import connect, DatabaseError
import yaml

class ConfigLoader:
    def __init__(self, config_path='../config/path_config.yaml'):
        self.config = self.load_config(config_path)

    def load_config(self, config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config

class PostgreSQLManager:
    def __init__(self, config):
        self.db_name = config['database']['postgres']['name']
        self.user = config['database']['postgres']['user']
        self.password = config['database']['postgres']['password']
        self.conn = None

    def __enter__(self):
        try:
            self.conn = connect(
                host="localhost",
                database=self.db_name,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor()
            logging.info("PostgreSQL connection opened.")
        except DatabaseError as e:
            logging.error(f"PostgreSQL connection error: {e}")
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
            logging.info("PostgreSQL connection closed.")

    def execute_query(self, query, params=None):
        """執行傳入的 SQL 查詢並處理參數化查詢"""
        try:
            self.cursor.execute(query, params)
            if query.strip().lower().startswith("select"):
                results = self.cursor.fetchall()
                logging.info(f"Query returned {len(results)} results.")
                return results
            else:
                self.conn.commit()
                logging.info(f"Query executed: {query}")
        except DatabaseError as e:
            logging.error(f"PostgreSQL query error: {e}")
            raise

    def create_table(self, table_name, columns):
        """根據動態傳入的表名稱和欄位資訊創建表"""
        columns_str = ', '.join([f"{col} {dtype}" for col, dtype in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str});"
        self.execute_query(query)

    def insert_data(self, table_name, data):
        """根據傳入的表名和數據字典動態生成插入語句"""
        columns = ', '.join(data.keys())
        values = ', '.join([f"%({key})s" for key in data.keys()])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values}) RETURNING id;"
        result = self.execute_query(query, data)
        return result[0][0]  # 返回插入數據的 ID

    def read_data(self, table_name, conditions=None, columns="*"):
        """根據條件查詢數據，可指定欄位"""
        query = f"SELECT {columns} FROM {table_name}"
        if conditions:
            condition_str = ' AND '.join([f"{key}=%s" for key in conditions.keys()])
            query += f" WHERE {condition_str};"
            params = list(conditions.values())
        else:
            query += ";"
            params = None
        return self.execute_query(query, params)

    def update_data(self, table_name, data, conditions):
        """根據條件更新數據"""
        update_str = ', '.join([f"{key}=%s" for key in data.keys()])
        condition_str = ' AND '.join([f"{key}=%s" for key in conditions.keys()])
        query = f"UPDATE {table_name} SET {update_str} WHERE {condition_str};"
        params = list(data.values()) + list(conditions.values())
        self.execute_query(query, params)

    def delete_data(self, table_name, conditions):
        """根據條件刪除數據"""
        condition_str = ' AND '.join([f"{key}=%s" for key in conditions.keys()])
        query = f"DELETE FROM {table_name} WHERE {condition_str};"
        params = list(conditions.values())
        self.execute_query(query, params)


if __name__ == "__main__":
    # 加載配置
    config_loader = ConfigLoader()
    config = config_loader.config

    # 使用 PostgreSQLManager
    with PostgreSQLManager(config) as postgres_manager:
        postgres_manager.create_table('employees', {
            'id': 'SERIAL PRIMARY KEY',
            'name': 'TEXT',
            'age': 'INT'
        })

        new_employee_id = postgres_manager.insert_data('employees', {
            'name': 'Bob',
            'age': 25
        })
        logging.info(f"Inserted PostgreSQL employee ID: {new_employee_id}")

        employee = postgres_manager.read_data('employees', conditions={'id': new_employee_id})
        logging.info(f"Queried PostgreSQL employee: {employee}")

        postgres_manager.update_data('employees', {'age': 26}, {'id': new_employee_id})
        updated_employee = postgres_manager.read_data('employees', conditions={'id': new_employee_id})
        logging.info(f"Updated PostgreSQL employee: {updated_employee}")

        postgres_manager.delete_data('employees', {'id': new_employee_id})

