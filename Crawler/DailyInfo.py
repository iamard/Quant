# coding=utf-8

from Crawler import Crawler
from bs4 import BeautifulSoup
import pandas as pandas
import numpy as numpy

class DailyInfo(Crawler):
    def __init__(self):
        # Initialize Crawler class
        Crawler.__init__(self)

        # URL to query daily info
        self.__query  = "http://www.twse.com.tw/ch/trading/exchange/BWIBBU/BWIBBU_d.php"

    def quote_daily_info(self, year, month, day, dump = None):
        date = "{YEAR}/{MONTH}/{DAY}".format(YEAR  = year - 1911, \
                                             MONTH = str(month).zfill(2), \
                                             DAY   = str(day).zfill(2))
        data = {'input_date': date, 'select2': 'ALL', 'order': 'STKNO', 'login_btn': '%ACd%B8%DF'}
        data = self._handle_post_request(self.__query, data)
        if data == None:
            return None

        soup  = BeautifulSoup(data, 'html.parser')
        div   = soup.find('div', {'id':'tbl-containerx'})
        if div == None:
            return None
        table = div.find('table')
        body  = table.find('tbody')
        rows  = body.findAll('tr')

        data  = numpy.empty((0, 5))
        for row in rows:
            cols = row.findAll('td', {'class': 'basic2'})
            data = numpy.append(data, numpy.array([[cols[0].text, cols[1].text, cols[2].text, cols[3].text, cols[4].text]]), axis = 0)

        frame  = pandas.DataFrame(data)
        frame.columns = ['證券代號', '證券名稱', '本益比', '殖利率(%)', '股價淨值比']
        frame  = frame.set_index('證券代號')
        frame  = frame.apply(pandas.to_numeric, errors = 'coerce')

        if dump == "csv":
            frame.to_csv("{YEAR}_{MONTH}_{DAY}-DailyInfo.csv".format(YEAR = year, MONTH = month, DAY = day), encoding = 'utf8')
        elif dump == "xlsx":
            frame.to_excel("{YEAR}_{MONTH}_{DAY}-DailyInfo.xlsx".format(YEAR = year, MONTH = month, DAY = day))

        return frame

if __name__ == "__main__":
    crawler = DailyInfo()
    crawler.quote_daily_info(2016, 7, 12, dump = 'csv')