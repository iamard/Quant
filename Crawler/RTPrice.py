# coding=utf-8

from Crawler import Crawler

class RTPrice(Crawler):
    def __init__(self, symbol_list):
        # Initialize Crawler class
        Crawler.__init__(self)

        # URL to create base connection
        self.__base  = 'http://mis.twse.com.tw/stock/index.jsp'

        # Real URL to acquire information
        self.__query = 'http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch='
        for symbol in symbol_list:
            self.__query += ('tse_{}.tw|'.format(symbol))

    def quote_price_info(self):
        data = self._handle_get_request(self.__base)
        if data == None:
            return None

        data = self._handle_get_request(self.__query)
        if data == None:
            return None

        data = self._parse_json_response(data)
        if data == None:
            return None
        return data['msgArray']

if __name__ == "__main__":
    realTime = RTPrice(["0050"])
    data = realTime.quote_price_info()
    print data