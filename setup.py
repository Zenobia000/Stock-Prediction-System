from setuptools import setup, find_packages

setup(
    name="my_project",  # 專案名稱 套件名稱
    version="0.1.0",  # 專案版本
    author="Your Name",
    author_email="your.email@example.com",
    description="A short description of your project",
    long_description=open("README.md").read(),  # 專案詳細說明，通常來自README文件
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/my_project",  # 專案的源碼地址或主頁
    packages=find_packages(),  # 自動查找專案中的所有Python包
    install_requires=[  # 定義安裝依賴
        "requests>=2.20",
        "numpy>=1.18.0"
    ],
    classifiers=[  # 用於定義項目類型的分類信息
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',  # Python 版本要求
)
