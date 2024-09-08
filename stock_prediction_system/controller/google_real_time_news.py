import time
import random
import requests
from datetime import datetime
from tqdm import tqdm  # 引入 tqdm 進度條庫

class CnyesNewsSpider():

    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            # 更多 User-Agent 可隨時增加
        ]

    def get_headers(self):
        return {
            'Origin': 'https://news.cnyes.com/',
            'Referer': 'https://news.cnyes.com/',
            'User-Agent': random.choice(self.user_agents),
        }

    def get_newslist_info(self, page=1, limit=30, start_time=None, end_time=None):
        """ 房屋詳情

        :param page: 頁數
        :param limit: 一頁新聞數量
        :param start_time: 起始時間（格式：'YYYY-MM-DD HH:MM:SS'）
        :param end_time: 結束時間（格式：'YYYY-MM-DD HH:MM:SS'）
        :return newslist_info: 新聞資料
        """
        params = {
            'page': page,
            'limit': limit
        }

        # 處理時間篩選
        if start_time:
            params['startAt'] = int(time.mktime(datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").timetuple()))
        if end_time:
            params['endAt'] = int(time.mktime(datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").timetuple()))

        retry_count = 5
        while retry_count > 0:
            try:
                r = requests.get(
                    f"https://api.cnyes.com/media/api/v1/newslist/category/headline",
                    headers=self.get_headers(),
                    params=params
                )
                if r.status_code == requests.codes.ok:
                    newslist_info = r.json()['items']
                    return newslist_info
                else:
                    print(f'請求失敗，狀態碼: {r.status_code}')
                    retry_count -= 1
                    time.sleep(random.uniform(5, 10))  # 延遲一段時間再重試
            except requests.exceptions.RequestException as e:
                print(f'請求失敗，錯誤: {e}')
                retry_count -= 1
                time.sleep(random.uniform(5, 10))  # 延遲一段時間再重試

        return None  # 如果多次重試後仍然失敗，返回 None

    def fetch_all_news_within_timeframe(self, limit=30, start_time=None, end_time=None):
        """ 根據起訖時間抓取所有新聞資料 """
        all_news_data = []
        page = 1
        total_news_count = 0

        # 預先估計新聞總數量（可以根據第一頁的結果來推測）
        initial_newslist_info = self.get_newslist_info(page=1, limit=limit, start_time=start_time, end_time=end_time)
        if initial_newslist_info and 'total' in initial_newslist_info:
            total_news_count = initial_newslist_info['total']
        else:
            print("無法估計新聞總數，將逐頁爬取。")

        # 使用 tqdm 進度條
        with tqdm(total=total_news_count, desc="Fetching News", unit="news") as pbar:
            while True:
                newslist_info = self.get_newslist_info(page=page, limit=limit, start_time=start_time, end_time=end_time)
                if not newslist_info or not newslist_info["data"]:
                    break

                for news in newslist_info["data"]:
                    news_publish_time = datetime.fromtimestamp(news["publishAt"])
                    if news_publish_time > datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S"):
                        continue  # 跳過超過結束時間的新聞
                    if news_publish_time < datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S"):
                        return all_news_data  # 如果新聞時間小於開始時間，則完成抓取

                    news_data = {
                        "news_id": news["newsId"],
                        "url": f'https://news.cnyes.com/news/id/{news["newsId"]}',
                        "title": news["title"],
                        "content": news["content"],
                        "summary": news["summary"],
                        "keyword": news["keyword"],
                        "publish_at": news_publish_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "category_name": news["categoryName"],
                        "category_id": news["categoryId"]
                    }
                    all_news_data.append(news_data)

                    # 更新進度條
                    pbar.update(1)

                if len(newslist_info["data"]) < limit:
                    break  # 如果返回的新聞數量小於限制，意味著沒有更多的新聞了

                page += 1
                time.sleep(random.uniform(3, 7))  # 隨機延遲，避免被反爬蟲機制偵測

        return all_news_data

if __name__ == "__main__":
    cnyes_news_spider = CnyesNewsSpider()
    all_news_data_json = cnyes_news_spider.fetch_all_news_within_timeframe(
        start_time="2024-06-01 00:00:00",
        end_time="2024-06-05 23:59:59"
    )

