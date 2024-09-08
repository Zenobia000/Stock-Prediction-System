from stock_prediction_system.controller.pipelines import Preflight
from stock_prediction_system.controller.pipelines import stock_lists_download
from stock_prediction_system.controller.pipelines import stock_news_extraction
from stock_prediction_system.controller.pipelines import count_stock_times_in_news
from stock_prediction_system.controller.pipelines import plot_statistic_result

if __name__ == '__main__':

    Preflight("Preflight").execute()

    stock_lists_download("stock_lists_download").execute()

    stock_news_extraction = stock_news_extraction("stock_news_extraction",
                                                  start_time="2024-09-08 00:00:00",
                                                  end_time="2024-09-08 23:59:59").execute()

    statistic_result = count_stock_times_in_news("count_stock_times_in_news", stock_news_extraction).execute()

    plot_statistic_result("plot_statistic_result", statistic_result).execute()

    print("process done")

