# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 14:21:30 2019

@author: allegra
"""
"""
追踪一个用户的全市所有交易记录。
"""
from selenium import webdriver
import json
import pandas as pd
import time
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException


bgmid = '424658'


option = webdriver.ChromeOptions()
#True为静默模式，False为非静默模式
option.headless = False

brower_path=r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
driver = webdriver.Chrome(brower_path, options=option)
cha_path = './result/char_price.xlsx'

chaids = pd.read_excel(cha_path)['id'].values.tolist()
df_shds = pd.read_excel(cha_path)
nicknames = df_shds['name'].values.tolist()

asks = []
bids = []
for c, chaid in enumerate(chaids):
    driver.get('https://www.tinygrail.com/api/chara/user/{chaid}/{bgmid}'.format(bgmid=bgmid, chaid=chaid))
    j = driver.find_element_by_xpath('/html/body/pre').text
    d = json.loads(j)
    ask_rec = d['Value']['AskHistory']
    bid_rec = d['Value']['BidHistory']
    
    if ask_rec:
        asks += [('ask', chaid, nicknames[c], k['TradeTime'], k['SellerId'], k['BuyerId'], k['Price'], k['Amount'])
                  for k in ask_rec]
    if bid_rec:
        bids += [('bid', chaid, nicknames[c], k['TradeTime'], k['SellerId'], k['BuyerId'],  k['Price'], k['Amount'])
                  for k in bid_rec]


df_ask = pd.DataFrame(asks, columns=['trade', 'id', 'nickname', 'trade time','seller id','buyer id', 'price', 'amount'])
df_bid = pd.DataFrame(bids, columns=['trade', 'id', 'nickname', 'trade time','seller id','buyer id', 'price', 'amount'])

df_ask.set_index(['trade', 'id', 'nickname'], inplace=True)
df_bid.set_index(['trade', 'id', 'nickname'], inplace=True)
df_ab = pd.concat([df_ask, df_bid]).sort_values(['trade time'], ascending=False)

save_path = './result/'+ bgmid + '.xlsx'
df_ab.to_excel(save_path, index=True)