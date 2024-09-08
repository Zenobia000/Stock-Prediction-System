import os
import pandas as pd
import numpy as np
import plotly.express as px

from stock_prediction_system.controller.google_real_time_news import CnyesNewsSpider
from stock_prediction_system.utils.extract_path import PathSetting
from stock_prediction_system.controller.stock_list import GetStockList

# 初始化
class Preflight:
    def __init__(self, name):
        self.name = name

    def execute(self):
        print(self.name, "run...")

        # process procedure
        return self._initial_setting()

    def _initial_setting(self):
        path_setting = PathSetting()
        path_setting.initialize_path()

        return None

# 抓取股票列表 and Save stock list to csv
class stock_lists_download:
    def __init__(self, name):
        self.name = name

    def execute(self):
        print(self.name, "run...")

        # process procedure

        return self._stock_lists_download()

    def _stock_lists_download(self):
        path_setting = PathSetting()
        stock_list = GetStockList()
        stock_list.download_stock_list_to_csv(path_setting.get_files_path('stocks_list_path'))
        return None

# 每日財經新聞抓取
class stock_news_extraction:
    def __init__(self, name, start_time, end_time):
        '''
        :param name:
        :param start_time:
        :param end_time:

        example
        start_time="2024-09-02 00:00:00",
        end_time="2024-09-04 23:59:59"

        '''

        self.name = name
        self.start_time = start_time
        self.end_time = end_time

    def execute(self):
        print(self.name, "run...")

        # process procedure

        return self._stock_news_extraction()

    def _stock_news_extraction(self):

        cnyes_news_spider = CnyesNewsSpider()
        all_news_data_json = cnyes_news_spider.fetch_all_news_within_timeframe(
            start_time=self.start_time,
            end_time=self.end_time
        )
        return all_news_data_json

# 統計財經新聞中被提及股票和產業次數
class count_stock_times_in_news:
    def __init__(self, name, all_news_data_json):
        self.name = name
        self.all_news_data_json = all_news_data_json

    def execute(self):
        print(self.name, "run...")

        # process procedure
        return self._count_stock_times_in_news()

    def _count_stock_times_in_news(self):
        path_setting = PathSetting()
        stock_list_all = pd.read_csv(path_setting.get_files_path("stocks_list_path"), encoding="utf-8-sig")
        stock_lists = stock_list_all[(stock_list_all["市場別"] == "上市") & (pd.notna(stock_list_all["產業別"]))]

        # 儲存符合條件的股票和產業名稱出現次數
        stock_occurrences = []
        for article in self.all_news_data_json:
            article_title = article.get("title", "")
            article_content = article.get("content", "")
            matched_stocks = set()  # 每篇文章中可能有多支股票匹配，用集合來避免重複

            for _, row in stock_lists.iterrows():
                stock_name = row["股票名稱"]
                stock_code = row["股票代碼"]

                # 將 title 和 content 的檢查合併，減少重複邏輯
                if any(term in article_title or term in article_content for term in [stock_name, stock_code]):
                    matched_stocks.add((stock_name, stock_code, row["產業別"]))

            # 將每篇文章中提到的股票累加至結果列表
            for stock_name, stock_code, industry in matched_stocks:
                stock_occurrences.append({
                    "股票名稱": stock_name,
                    "股票代碼": stock_code,
                    "產業別": industry,
                    "出現次數": 1  # 每次匹配就增加一次
                })

            # 將出現次數的資料轉為 DataFrame
            df = pd.DataFrame(stock_occurrences)

        return df

# 統計財經新聞中被提及股票和產業次數
class plot_statistic_result:
    def __init__(self, name, compare_result_in_news):
        self.name = name
        self.compare_result_in_news = compare_result_in_news

    def execute(self):
        print(self.name, "run...")

        # process procedure
        return self._plot_statistic_result()

    def _plot_statistic_result(self):
        # 聚合相同股票名稱+股票代碼的出現次數
        df = self.compare_result_in_news
        df_stock_count = df.groupby(['股票名稱', '股票代碼', '產業別'])['出現次數'].sum().reset_index()

        # 1. 統計於新聞標題出現最多次的前10大 "股票代碼+股票名稱" 並繪製成長條圖
        top_10_stocks = df_stock_count.nlargest(10, '出現次數')
        fig1 = px.bar(top_10_stocks, x='股票名稱', y='出現次數', title='新聞標題出現最多次的前10大股票名稱')

        # 2. 統計於新聞標題出現最多次的前3大產業名稱 並繪製成長條圖
        df_industry_count = df.groupby('產業別')['出現次數'].sum().reset_index()
        top_industries = df_industry_count.nlargest(3, '出現次數')
        fig2 = px.bar(top_industries, x='產業別', y='出現次數', title='新聞標題出現最多次的前3大產業名稱')

        # 顯示結果
        fig1.show()
        fig2.show()


if __name__ == '__main__':
    path_setting = PathSetting()
    print(path_setting.get_files_path("stocks_list_path"))

