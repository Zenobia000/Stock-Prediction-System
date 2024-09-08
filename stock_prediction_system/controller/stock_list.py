import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
from typing import List, Dict
from tqdm import tqdm

from stock_prediction_system.utils.extract_path import PathSetting


class GetStockList:

    def __init__(self) -> None:
        """
        初始化類別並調用私有方法獲取上市和上櫃股票列表。
        """
        self.stock_list: List[Dict[str, str]] = self._crawler_stock_list()
        self.stock_OTC_list: List[Dict[str, str]] = self._crawler_stock_OTC_list()

    def get_all_stock_list(self) -> List[Dict[str, str]]:
        """
        合併上市和上櫃股票列表，並僅保留指定的字段。

        :return: 合併後的股票列表，每個股票包含指定的字段。
        """
        # 合併兩個 JSON 對象列表
        combined_list: List[Dict[str, str]] = self.stock_list + self.stock_OTC_list

        # 只保留指定的 key
        filtered_list: List[Dict[str, str]] = [
            {
                '股票代碼': item.get('股票代碼', ''),
                '股票名稱': item.get('股票名稱', ''),
                '產業別': item.get('產業別', ''),
                '市場別': item.get('市場別', '')
            }
            for item in combined_list
        ]

        return filtered_list

    def download_stock_list_to_csv(self, file_path: str) -> None:
        """
        將合併後的股票列表保存為 CSV 檔案。

        :param file_path: 要保存的完整檔案路徑，包含路徑與檔名。
        """

        # 獲取資料夾路徑
        folder_path = os.path.dirname(file_path)

        # 確保資料夾存在，若不存在則創建
        os.makedirs(folder_path, exist_ok=True)

        # 獲取所有股票列表
        stock_list = self.get_all_stock_list()

        # 將股票列表轉換為 DataFrame
        df = pd.DataFrame(stock_list)

        # 將 DataFrame 保存為 CSV 檔案
        df.to_csv(file_path, index=False, encoding='utf-8-sig')

    def _crawler_stock_list(self) -> List[Dict[str, str]]:
        """
        爬取台灣證券交易所的上市股票列表，並轉換為 JSON 對象。

        :return: 上市股票列表的 JSON 對象，每個股票為一個字典。
        """
        url: str = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
        res: requests.Response = requests.get(url)

        soup: BeautifulSoup = BeautifulSoup(res.text, "lxml")
        tr = soup.findAll('tr')

        # 將爬取的數據整理到列表中
        tds: List[List[str]] = []
        for raw in tqdm(tr, desc="Processing Stock List", unit="tr"):
            data = [td.get_text() for td in raw.findAll("td")]
            if len(data) == 7:
                tds.append(data)

        # 轉換為 DataFrame 並拆分「有價證券代號及名稱」欄位
        stock_list: pd.DataFrame = pd.DataFrame(tds[1:], columns=tds[0])
        stock_list[['股票代碼', '股票名稱']] = stock_list['有價證券代號及名稱 '].str.split(expand=True).iloc[:, :2]

        # 將 DataFrame 轉換為 JSON 格式並返回 JSON 對象
        json_data_stock_list: List[Dict[str, str]] = json.loads(stock_list.to_json(orient='records', force_ascii=False))

        return json_data_stock_list

    def _crawler_stock_OTC_list(self) -> List[Dict[str, str]]:
        """
        爬取台灣櫃檯買賣中心的上櫃股票列表，並轉換為 JSON 對象。

        :return: 上櫃股票列表的 JSON 對象，每個股票為一個字典。
        """
        url: str = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=4'
        res: requests.Response = requests.get(url)

        soup: BeautifulSoup = BeautifulSoup(res.text, "lxml")
        tr = soup.findAll('tr')

        # 將爬取的數據整理到列表中
        tds: List[List[str]] = []
        for raw in tqdm(tr, desc="Processing OTC Stock List", unit="tr"):
            data = [td.get_text() for td in raw.findAll("td")]
            if len(data) == 7:
                tds.append(data)

        # 轉換為 DataFrame 並拆分「有價證券代號及名稱」欄位
        stock_list: pd.DataFrame = pd.DataFrame(tds[1:], columns=tds[0])
        stock_list[['股票代碼', '股票名稱']] = stock_list['有價證券代號及名稱 '].str.split(expand=True).iloc[:, :2]

        # 將 DataFrame 轉換為 JSON 格式並返回 JSON 對象
        json_data_stock_OTC_list: List[Dict[str, str]] = json.loads(
            stock_list.to_json(orient='records', force_ascii=False))

        return json_data_stock_OTC_list

if __name__ == "__main__":
    # stock_list = GetStockList()
    # stock_list.download_stock_list_to_csv('stock_list.csv', './data')

    path_setting = PathSetting()
    stocks_list_path = path_setting.get_files_path('stocks_list_path')

    print(f"Stocks list path: {stocks_list_path}")

