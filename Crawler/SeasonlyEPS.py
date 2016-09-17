# coding=utf-8

from Crawler import Crawler
from bs4 import BeautifulSoup
import pandas as pandas
import numpy as numpy

class SeasonlyEPS(Crawler):
    def __init__(self):
        # Initialize Crawler class
        Crawler.__init__(self)

        # URL to query seasonly EPS
        self.__query  = 'http://mops.twse.com.tw/mops/web/t163sb04?' + \
                'encodeURIComponent=1&step=1&firstin=1&off=1&TYPEK=sii&year={YEAR}&season={SEASON}'

    def quote_seasonly_EPS(self, year, season, dump = None):
        query = self.__query.format(TYPE = type, YEAR = year - 1911, SEASON = str(season).zfill(2))
        data  = self._handle_get_request(query)
        if data == None:
            return None

        soup  = BeautifulSoup(data, 'html.parser')
        data  = numpy.empty((0, 3))
        for table in soup.findAll('table', attrs = {'class' : "hasBorder"}):
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 0:
                    continue
                data = numpy.append(data, numpy.array([[cols[0].text, cols[1].text, cols[-1].text]]), axis = 0)

        frame = pandas.DataFrame(data)
        frame.columns = ['證券代號', '證券名稱', 'EPS']
        frame = frame.set_index('證券代號')
        print frame.head()
                
        if dump == "csv":
            frame.to_csv("{YEAR}_{SEASON}-EPSSeason.csv".format(YEAR = year, SEASON = 1), encoding = 'utf8')
        elif dump == "xlsx":
            frame.to_excel("{YEAR}_{SEASON}-PBRDaily.xlsx".format(YEAR = year, SEASON = 1))

        return frame

if __name__ == "__main__":
    crawler = SeasonlyEPS()
    crawler.quote_seasonly_EPS(2016, 1,  dump = "csv")