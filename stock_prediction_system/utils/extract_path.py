import os
import yaml

class PathSetting:
    def __init__(self):
        # Load config.yaml file
        self.config_path = '../config/path_config.yaml'
        with open(self.config_path, 'r') as file:
            self.config = yaml.safe_load(file)

    def initialize_path(self):
        # Create subfolders from config.yaml (using absolute paths directly)
        for folder in self.config.get('folders', []):
            for subfolder in folder.get('subfolders', []):
                folder_path = os.path.abspath(subfolder)  # Get the absolute path
                os.makedirs(folder_path, exist_ok=True)

        # Create files from config.yaml
        for file_config in self.config.get('files', []):
            for file_key, file_value in file_config.items():
                file_path = os.path.abspath(file_value)  # Get the absolute path
                file_dir = os.path.dirname(file_path)

                # Ensure the directory exists
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir, exist_ok=True)

        print("create subfolders successfully!")

    def get_files_path(self, key: str):
        # Retrieve file path by key from config.yaml (without prefixing project_name)
        for file in self.config.get('files', []):
            if key in file:
                file_path = os.path.join(file[key])
                # full_path = os.path.abspath(file_path)
                return file_path
        return None

    # 擷取資料夾路徑，並根據子資料夾進行拼接
    def get_folder_path(self, folder_name, subfolder_name=None):
        # 從 config.yaml 中查找對應的資料夾名稱
        for folder in self.config.get('folders', []):
            if folder['name'] == folder_name:
                # 如果指定了子資料夾，則拼接資料夾路徑
                if subfolder_name and subfolder_name in folder.get('subfolders', []):
                    full_path = os.path.join(folder_name, subfolder_name)
                else:
                    full_path = folder_name  # 如果沒有指定子資料夾，僅返回主資料夾路徑
                return os.path.abspath(full_path)
        return None


if __name__ == "__main__":
    # Example usage:
    path_setting = PathSetting()

    # Initialize the project structure (folders and files)
    path_setting.initialize_path()

    # Get specific file path
    stocks_list_path = path_setting.get_files_path('stocks_list_path')
    stocks_folder_path = path_setting.get_folder_path('data', 'features')

    print(f"Stocks list path: {stocks_list_path}")
    print(f"Stocks folder path: {stocks_folder_path}")

