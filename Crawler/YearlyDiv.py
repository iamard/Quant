# coding=utf-8

from Crawler import Crawler
import pandas as pandas

class YearlyDiv(Crawler):
    def __init__(self):
        # Initialize Crawler class
        Crawler.__init__(self)

        # URL to query yearly dividend
        self.__query = "http://mops.twse.com.tw/server-java/t05st09sub?step=1&TYPEK=sii&YEAR={YEAR}&first"

    def quote_yearly_dividend(self, year, dump = None):
        query = self.__query.format(YEAR = year - 1911)
        data  = self._handle_get_request(query)
        if data == None:
            return None

        data  = pandas.io.html.read_html(data, attrs = {'class': 'hasBorder'})

        frame = None
        for index in range(len(data)):
            if len(data[index]) == 1:
                continue
            if index == 1:
                frame = data[index][0:][2:]
            else:
                remain = data[index][0:][2:]
                frame = frame.append(remain)

        frame.columns = ['公司代號名稱', \
                         '資料來源', \
                         '期別', \
                         '董事會決議通過股利分派日', \
                         '股東會日期', \
                         '期初未分配盈餘/待彌補虧損(元)', \
                         '本期淨利(淨損)(元)', \
                         '可分配盈餘(元)', \
                         '分配後期末未分配盈餘(元)',
                         '盈餘分配之現金股利(元/股)', \
                         '法定盈餘公積、資本公積發放 之現金(元/股)', \
                         '股東配發之現金(股利)總金額(元)', \
                         '盈餘轉增資配股(元/股)', \
                         '法定盈餘公積、資本公積轉增資配股(元/股)', \
                         '股東配股總股數(股)', \
                         '摘錄公司章程-股利分派部分', \
                         '備註', \
                         '普通股每股面額']
        frame = frame.set_index('公司代號名稱')

        if dump == "csv":
            frame.to_csv("{YEAR}-Dividend.csv".format(YEAR = year), encoding = 'utf8')
        elif dump == "xlsx":
            frame.to_excel("{YEAR}-Dividend.xlsx".format(YEAR = year))

        return frame


if __name__ == "__main__":
    crawler = YearlyDiv()
    crawler.quote_yearly_dividend(2016, dump = "csv")
