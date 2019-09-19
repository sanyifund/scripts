"""
查找某角色所有的挂单、历史交易、股东股份。但是查不到没股的用户。
"""

import os
import time
import json
import pandas as pd
from selenium import webdriver

class Grail(object):

    def __init__(self, char_id, char_name):
    
        brower_path = r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
        driver = webdriver.Chrome(brower_path)
        
        driver.get("https://www.tinygrail.com/api/chara/users/"+char_id+"/1/1000")
        j = driver.find_element_by_xpath('/html/body/pre').text
        d = json.loads(j)
        
        self.shareholders = d['Value']['Items']
        self.char_id = char_id
        self.char_name = char_name
        self.driver = driver

      
    def get_shds(self):
    
        char_id = self.char_id
        char_name = self.char_name
        driver = self.driver
        shareholders = self.shareholders
        
        shareholderNames = [i['Name'] for i in shareholders]
        shareholderNicknames = [i['Nickname'] for i in shareholders]

        bgmids = []
        for i in shareholderNames:
            driver.get('http://mirror.api.bgm.rin.cat/user/'+i)
            j = driver.find_element_by_xpath('/html/body/pre').text
            d = json.loads(j)
            bgmids.append(d['id'])
            

        holdings = []
        for i in bgmids:
            driver.get('https://www.tinygrail.com/api/chara/user/assets/'+str(i)+'/true')
            j = driver.find_element_by_xpath('/html/body/pre').text
            d = json.loads(j)
            
            time.sleep(0.1)
            
            characters = d['Value']['Characters']
            for character in characters:
                if character['Name'] == char_name:
                    holdings.append(character['State'])

        shds = [('http://mirror.api.bgm.rin.cat/user/'+str(bgmid), bgmid, name, num)
                for bgmid, name, num in zip(bgmids, shareholderNicknames, holdings)]

        df = pd.DataFrame(shds, columns=['url', 'bgmid', 'nickname', 'holdings'])
        
        save_path = "./result/"+char_name+"_shds.xlsx"
        df.to_excel(save_path, index=False)
        
        return df
        
        
    def get_pendings(self, shds_path):
    
        char_id = self.char_id
        char_name = self.char_name
        driver = self.driver
        
        df_shds = pd.read_excel(shds_path)
        ids = df_shds['bgmid'].values
        nicknames = df_shds['nickname'].values
        asks = []
        bids = []

        for c, i in enumerate(ids):
            driver.get("https://www.tinygrail.com/api/chara/user/{characterId}/{userId}".format(
                characterId=char_id, userId=str(i)
                ))
            j = driver.find_element_by_xpath('/html/body/pre').text
            d = json.loads(j)
            
            time.sleep(0.1)
            
            ask_rec = d['Value']['Asks']
            bid_rec = d['Value']['Bids']

            if ask_rec:
                asks += [('ask', i, nicknames[c], k['Begin'], k['Price'], k['Amount'])
                         for k in ask_rec]
            if bid_rec:
                bids += [('bid', i, nicknames[c], k['Begin'], k['Price'], k['Amount'])
                         for k in bid_rec]
                         
        df_ask = pd.DataFrame(asks, columns=['pending', 'id', 'nickname', 'begin', 'price', 'amount'])
        df_bid = pd.DataFrame(bids, columns=['pending', 'id', 'nickname', 'begin', 'price', 'amount'])
        df_ask.set_index(['pending', 'id', 'nickname', 'begin'], inplace=True)
        df_bid.set_index(['pending', 'id', 'nickname', 'begin'], inplace=True)
        df_ab = pd.concat([df_ask,df_bid]).sort_values(['price'], ascending=False)
        
        save_path = './result/'+ char_name + '_pending.xlsx'
        df_ab.to_excel(save_path, index=True)

        return df_ab 

        
    def get_trades(self, shds_path):
            char_id = self.char_id
            char_name = self.char_name
            driver = self.driver
            
            df_shds = pd.read_excel(shds_path)
            ids = df_shds['bgmid'].values
            nicknames = df_shds['nickname'].values

            asks = []
            bids = []
            for c, i in enumerate(ids):
                driver.get("https://www.tinygrail.com/api/chara/user/{characterId}/{userId}".format(
                            characterId=char_id, userId=str(i)
                ))
                j = driver.find_element_by_xpath('/html/body/pre').text
                d = json.loads(j)
                
                time.sleep(0.1)
                
                ask_rec = d['Value']['AskHistory']
                bid_rec = d['Value']['BidHistory']

                if ask_rec:
                    asks += [('ask', i, nicknames[c], k['TradeTime'], k['SellerId'], k['BuyerId'], k['Price'], k['Amount'])
                              for k in ask_rec]
                if bid_rec:
                    bids += [('bid', i, nicknames[c], k['TradeTime'], k['SellerId'], k['BuyerId'],  k['Price'], k['Amount'])
                              for k in bid_rec]   
                                     
            df_ask = pd.DataFrame(asks, 
                                  columns=['trade', 'id', 'nickname', 'trade time','seller id','buyer id', 'price', 'amount'])
            df_bid = pd.DataFrame(bids, 
                                  columns=['trade', 'id', 'nickname', 'trade time','seller id','buyer id', 'price', 'amount'])

            df_ask.set_index(['trade', 'id', 'nickname'], inplace=True)
            df_bid.set_index(['trade', 'id', 'nickname'], inplace=True)
            df_ab = pd.concat([df_ask, df_bid]).sort_values(['trade time'], ascending=False)
            
            save_path = './result/'+ char_name + '_trades.xlsx'
            df_ab.to_excel(save_path, index=True)

            return df_ab 
            
if __name__ == "__main__":
    
#    import argparse
#    parser = argparse.ArgumentParser()
#    parser.add_argument('-id', '--char_id', type=str)
#    parser.add_argument('-name', '--char_name', type=str)
#    parser.add_argument('-sf', '--shds_flag', type=int, default=1)
#    parser.add_argument('-pf', '--pending_flag', type=int, default=1)
#    args = parser.parse_args()
#    char_id = args.char_id
#    char_name = args.char_name
#    shds_flag = args.shds_flag
#    pending_flag = args.pending_flag
    
    '''====== input ======'''
    char_id = "5926"
    char_name = "高槻弥生"
    shds_flag = 1
    pending_flag = 1
    '''======  end  ======'''
    
    grail = Grail(char_id, char_name)
    
    shds_path = "./result/" + char_name + "_shds.xlsx"
    pending_path = "./result/" + char_name + "_pending.xlsx"
    trades_path = './result/' + char_name + '_trades.xlsx'
    
    # get shareholders table
    if not os.path.isfile(shds_path) or shds_flag == 1:
        df_shds = grail.get_shds()
        
    # get pendings
    if not os.path.isfile(pending_path) or shds_flag == 1 or pending_flag == 1:
        df_pendings = grail.get_pendings(shds_path)
        
    # get trades
    if not os.path.isfile(trades_path) or shds_flag == 1 or pending_flag == 1:
        df_trades = grail.get_trades(shds_path)
        

    
    from IPython.display import display
    display(
            pd.read_excel(shds_path),
            pd.read_excel(pending_path, index_col=[0,1,2,3]), 
            pd.read_excel(trades_path, index_col=[0,1])
        )