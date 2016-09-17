# coding=utf-8

from Crawler import Crawler
from bs4 import BeautifulSoup
import pandas as pandas

class MonthlyRev(Crawler):
    def __init__(self):
        # Initialize Crawler class
        Crawler.__init__(self)

        # URL to query monthly revenue
        self.__query = 'http://mops.twse.com.tw/nas/t21/{TYPE}/t21sc03_{YEAR}_{MONTH}_0.html'

    def quote_monthly_revenue(self, year, month, dump = None):
        typeList = ['sii', 'otc']
        output   = None
        for type in typeList:
            query = self.__query.format(TYPE = type, YEAR = year - 1911, MONTH = month)
            data  = self._handle_get_request(query)
            if data == None:
                return None

            soup   = BeautifulSoup(data, 'html.parser')
            raw    = []
            while(True):
                table = soup.find('table', attrs = {'border': '5'})
                if table == None:
                    break
                rows  = table.find_all('tr')
                for index in range(0, len(rows) - 1):
                    cols  = rows[index].find_all('td')
                    if len(cols) > 0:
                        data = [cols[0].text, \
                                cols[1].text, \
                                cols[2].text.replace(',', ''), \
                                cols[3].text.replace(',', ''), \
                                cols[4].text.replace(',', ''), \
                                cols[5].text.replace(',', ''), \
                                cols[5].text.replace(',', ''), \
                                cols[7].text.replace(',', ''), \
                                cols[8].text.replace(',', ''), \
                                cols[9].text.replace(',', ''), \
                                cols[10].text.replace(',', '')]
                        raw.append(data)
                table.decompose()

        frame = pandas.DataFrame(raw)
        frame.columns = ['公司代號', \
                         '公司名稱', \
                         '當月營收', \
                         '上月營收', \
                         '去年當月營收', \
                         '上月比較增減(%)', \
                         '去年同月增減(%)', \
                         '當月累計營收', \
                         '去年累計營收', \
                         '前期比較增減(%)', \
                         '備註']
        frame = frame.set_index('公司代號')
        
        if dump == "csv":
            frame.to_csv("{YEAR}_{MONTH}-Revenue.csv".format(YEAR = year, MONTH = month), encoding = 'utf8')
        elif dump == "xlsx":
            frame.to_excel("{YEAR}_{MONTH}-Revenue.xlsx".format(YEAR = year, MONTH = month))


if __name__ == "__main__":
    crawler = MonthlyRev()
    crawler.quote_monthly_revenue(2016, 5, dump = "csv")