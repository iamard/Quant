import requests
import json

class Crawler:
    def __init__(self):
        self.__headers = {'Accept-Encoding': 'gzip,deflate',
                          'Accept-Language': 'zh-TW',
                          'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.4.8.1000 Chrome/30.0.1599.101 Safari/537.36'}
        self.__session = requests.Session()                    
                    
    def _handle_get_request(self, URL, code = 'cp950'):
        with self.__session as session:
            data = session.get(URL, headers = self.__headers)
            if data.status_code != requests.codes.ok:
                return None 
            return data.content.decode(code, 'ignore')
        return None

    def _handle_post_request(self, URL, data = None, code = 'cp950'):
        with self.__session as session:
            data = session.post(URL, data = data, headers = self.__headers)
            if data.status_code != requests.codes.ok:
                return None 
            return data.content.decode(code, 'ignore')
        return None

    def _parse_json_response(self, content):
        try:
            data = json.loads(content)
        except Exception, e:
            print e
            data = None
        return data