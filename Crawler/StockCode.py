# coding=utf-8

from Crawler import Crawler
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

class StockCode(Crawler):
    def __init__(self):
        # Initialize Crawler class
        Crawler.__init__(self)

        # URL to query stock codes
        self.__query = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=2"

    def quote_stock_code(self, dump = None):
        data = self._handle_get_request(self.__query, 'cp950')
        if data == None:
            return None

        soup   = BeautifulSoup(data, 'html.parser')
        table  = soup.find('table', {'class': 'h4'})
        rows   = table.findAll('tr')

        data  = np.empty((0, 5))
        type  = ""
        for row in rows:
            cols = row.findAll('td')
            if len(cols) < 7:
                type = cols[0].text.strip()
            elif type == u"股票":
                list = cols[0].text.split()
                data = np.append(data, np.array([[list[0], list[1], cols[2].text, cols[3].text, cols[4].text]]), axis = 0)

        frame = pd.DataFrame(data)
        frame.columns = ['證券代號', '證券名稱', '上市日', '市場別', '產業別']
        frame = frame.set_index('證券代號')

        if dump == "csv":
            frame.to_csv("StockCode.csv", encoding = 'utf8')
        elif dump == "xlsx":
            frame.to_excel("StockCode.xlsx")

        print frame.head()
            
        return frame


if __name__ == "__main__":
    crawler = StockCode()
    frame   = crawler.quote_stock_code(dump = 'xlsx')
    print frame.head(10)