import requests
import os
import time
import asyncio
import aiohttp

class Scraper:
    def __init__(self):
        self.__headers = {'Accept-Encoding': 'gzip, deflate, br',
                          'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
                          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}

        self.out_path  = os.path.dirname(__file__) + "\\scraper_cache\\"

    def _handle_get_request_sync(self, url, params = None, code = 'cp950', \
        retry = 1, succ_sleep = 3, fail_sleep = 30):
        count = 0
        while count < retry:
            try:
                with requests.Session()  as session:
                    with session.get(url = url, params = params, \
                        headers = self.__headers) as response:
                        response.raise_for_status()
                        if succ_sleep > 0:
                            time.sleep(succ_sleep)
                        return response.content.decode(code, 'ignore')
            except Exception as e:
                print(e)
                if fail_sleep > 0:
                    time.sleep(fail_sleep)
            finally:
                count = count + 1

        return None

    def _handle_post_request_sync(self, url, params = None, code = 'cp950', \
        retry = 1, succ_sleep = 3, fail_sleep = 30):
        count = 0
        while count < retry:
            try:
                with requests.Session()  as session:
                    with session.post(url = url, params = params, \
                        headers = self.__headers) as response:
                        response.raise_for_status()
                        if succ_sleep > 0:
                            time.sleep(succ_sleep)
                        return response.content.decode(code, 'ignore')
            except Exception as e:
                print(e)
                if fail_sleep > 0:
                    time.sleep(fail_sleep)
            finally:
                count = count + 1

        return None

    async def _handle_get_request_async(self, url, params = None, code = 'cp950', \
        retry = 1, succ_sleep = 3, fail_sleep = 30):
        count = 0
        while count < retry:
            try:
                async with asyncio.BoundedSemaphore(10), aiohttp.ClientSession() as session:
                    async with session.get(
                        url = url, params = params, headers = self.__headers, raise_for_status = True
                    ) as response:
                        data = await response.read()
                        #print(data)
                        if succ_sleep > 0:
                            await asyncio.sleep(succ_sleep)
                        return data.decode(code, 'ignore')
            except Exception as e:
                print(e)
                if fail_sleep > 0:
                    await asyncio.sleep(fail_sleep)
            finally:
                count = count + 1

        return None

    async def _handle_post_request_async(self, URL, data = None, code = 'cp950', \
        retry = 1, succ_sleep = 3, fail_sleep = 30):
        count = 0
        while count < retry:
            try:
                async with asyncio.BoundedSemaphore(10), aiohttp.ClientSession() as session:
                    async with session.post(url = url, params = params, \
                        headers = self.__headers, raise_for_status = True) as response:
                        data = await response.read()
                        if succ_sleep > 0:
                            await asyncio.sleep(succ_sleep)
                        return data.decode(code, 'ignore')
            except Exception as e:
                print(e)
                if fail_sleep > 0:
                    await asyncio.sleep(fail_sleep)
            finally:
                count = count + 1

        return None
