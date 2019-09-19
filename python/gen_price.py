import os
import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

option = webdriver.ChromeOptions()
#True为静默模式，False为非静默模式
option.headless = False

class Stk(object):

    def __init__(self):
    
        self.brower_path = r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
        self.char_table = []
        self.char_ids = []
        
    def gen_ico_price(self, char_prices):
    
        driver = webdriver.Chrome(self.brower_path, options=option)
        while True:
            driver.get('https://www.tinygrail.com/api/chara/mrc/1/1000')
            try:
                WebDriverWait(driver, 10, 0.5).until(lambda x: x.find_element_by_xpath("/html/body/pre"))
                j = driver.find_element_by_xpath('/html/body/pre').text
                d = json.loads(j)
                
                if char_prices.empty:
                    market_char_id = [(dic["Id"],dic["Name"]) for dic in d["Value"]]
                else:
                    ico_prices = self.get_ico_prices(char_prices)
                    #把ico_prices这个字典中没有的角色存入market_char_id中
                    market_char_id = [(dic["Id"],dic["Name"]) for dic in d["Value"] if dic["Id"] not in ico_prices]
                if market_char_id:
                    for c, (char_id, char_name) in enumerate(market_char_id):
                        if char_id not in self.char_ids:
                            driver.get("https://www.tinygrail.com/api/chara/users/"+str(char_id)+"/1/1000")
                            j = driver.find_element_by_xpath('/html/body/pre').text
                            d = json.loads(j)
                            time.sleep(0.1)
                            shareholders = d['Value']['Items']
                            shareholderNames = [i['Name'] for i in shareholders]
                            
                            lll = len(shareholderNames)
                            print(lll)
                            for cc, i in enumerate(shareholderNames):
                                driver.get('http://mirror.api.bgm.rin.cat/user/'+i)
                                j = driver.find_element_by_xpath('/html/body/pre').text
                                d = json.loads(j)
                                user_id = d['id']
                                
                                driver.get("https://www.tinygrail.com/api/chara/user/{characterId}/{userId}".format(
                                            characterId=char_id, userId=str(user_id)
                                ))
                                j = driver.find_element_by_xpath('/html/body/pre').text
                                d = json.loads(j)
                
                                time.sleep(0.1)
                                bid_rec = d['Value']['BidHistory']
                                
                                flag = 0
                                if bid_rec:
                                    for k in bid_rec:
                                        if k['SellerId'] == 0:
                                            market_price = k['Price']
                                            market_time = k['TradeTime']
                                            flag = 1
                                            break
                
                                if flag == 1:
                                    break
                                
                            if cc == len(shareholderNames)-1:
                                market_price = '-'
                                market_time = '-'
                            print(len(market_char_id) - c, (char_name,market_price,char_id,market_time))
                            self.char_table.append((char_name,market_price,'https://bgm.tv/character/'+str(char_id),char_id,market_time))
                            self.char_ids.append(char_id)
                            df_char_price = pd.DataFrame(self.char_table, columns=["name", "price", 'url', "id", "time"])
                    if not char_prices.empty:
                        df_char_price = pd.concat([df_char_price,char_prices]).sort_values(['price'],ascending=False)
                    df_char_price.to_excel("./result/char_price.xlsx", index=False)
                    driver.quit()
                    return self.get_ico_prices(df_char_price)
                else:
                    print('无新角色')
                    driver.quit()
                    return self.get_ico_prices(char_prices)
            except (NoSuchElementException, TimeoutException, WebDriverException):
                #报错，重启浏览器
                driver.quit()
                driver = webdriver.Chrome(self.brower_path, options=option)
        
    def get_ico_prices(self, char_prices):
        # ico_prices, dict {id:price}
        ico_prices = char_prices.set_index("id").to_dict()["price"]
        return ico_prices
    
if __name__=="__main__":
    ti=time.time()

    prices_path = "./result/char_price.xlsx"
    char_prices=pd.DataFrame()
    
    stker = Stk()
    if os.path.isfile(prices_path):
        #如果有char_price.xlsx文件的话，读取已有的角色发行价
        char_prices = pd.read_excel(prices_path)
        
    #往char_price.xlsx中增加没有的新上市角色
    #第一次运行这个代码的话会很慢，运行一次生成char_price.xlsx后就很快了
    ico_prices = stker.gen_ico_price(char_prices)
    
    to=time.time()
    print(str(to-ti)+'s')
    