# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 19:23:31 2019

@author: allegra
"""
"""
0.有bug
1.功能：爬取六个榜单所有的股东或注资人（其实只用爬4个榜单。1个涨幅榜3个ico榜）。
2.每个页面会等待5秒钟，超时会重启driver。
3.爬过一遍后，下次再运行本爬虫就会只爬新增的用户。
4.最后的结果保存在'mapId.xlsx'中。其他三个文件是中间产物，也不要删，某些情况下能提升爬虫速度。
5.gen_all_name_flag 设置为1时更新'all_name.xlsx'文件，设置为0时不更新，直接读取。
  gen_all_bgmid_flag, gen_all_tinygrailId_flag同理。
"""

from selenium import webdriver
import json
import os
import pandas as pd
import time
import threading
from queue import Queue
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import re

option = webdriver.ChromeOptions()
#True为静默模式，False为非静默模式
option.headless = False

class User(object):
    
    def __init__(self):
        self.brower_path=r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
        
        self.mCharacterIds=[]
        self.icoCharacterIds=[]
        self.shareholderNames=[]
        self.oldnames={}
        self.shareholderNicknames=[]
        self.bgmids=[]
        self.tinygrailIds=[]
        self.murl=['https://www.tinygrail.com/api/chara/mrc/1/1000']
        self.ico_urls=['https://www.tinygrail.com/api/chara/mvi/1/1000',
                       'https://www.tinygrail.com/api/chara/mpi/1/1000',
                       'https://www.tinygrail.com/api/chara/rai/1/1000']
        
        self.qURL = Queue()
        self.qIco_url = Queue()
        self.qmCharacterId = Queue()
        self.qicoCharacterId = Queue()
        self.qShareholderName = Queue()
        self.qBgmid = Queue()
        
        self.name_path = './result/all_name.xlsx'
        self.bgmid_path = './result/all_bgmid.xlsx'
        self.tinygrailId_path = './result/all_tinygrailId.xlsx'
        self.mapid_path = './result/mapId.xlsx'
        
        self.quit = False
        
    def put_url(self):
        [self.qURL.put(url) for url in self.murl]
        [self.qIco_url.put(ico_url) for ico_url in self.ico_urls]
        
    def put_characterId(self):
        [self.qmCharacterId.put(mCharacterId) for mCharacterId in self.mCharacterIds]
        [self.qicoCharacterId.put(icoCharacterId) for icoCharacterId in self.icoCharacterIds]

    def put_shareholderName(self):
        [self.qShareholderName.put(shareholderName) for shareholderName in self.shareholderNames]

    def put_bgmid(self):
        [self.qBgmid.put(bgmid[1]) for bgmid in self.bgmids]
        
    def get_characterIds(self):
        #爬取6个榜单的角色
        driver = webdriver.Chrome(self.brower_path, options=option)
        flag=1
        while not self.qIco_url.empty():
            #队列为空的时候结束循环
            if flag:
                #这里判断一下的目的是，如果报错了的话，重启浏览器后接着上一次的继续爬，不要跳过出错的那次
                if not self.qURL.empty():
                    url = str(self.qURL.get())
                else:
                    url = str(self.qIco_url.get())
            flag = 1
            driver.get(url)
            try:
                WebDriverWait(driver, 5, 0.5).until(lambda x: x.find_element_by_xpath("/html/body/pre"))
                json_ = driver.find_element_by_xpath('/html/body/pre').text
                dict_ = json.loads(json_)
                Characters=dict_['Value']
                for Character in Characters:
                    if re.findall(r'chara/..i', url):
                        if Character['Id'] not in self.icoCharacterIds:
                            self.icoCharacterIds.append(Character['Id'])
                    else:
                        if Character['Id'] not in self.mCharacterIds:
                            self.mCharacterIds.append(Character['Id'])
            except (NoSuchElementException, TimeoutException, WebDriverException):
                #报错，重启浏览器
                flag = 0
                driver.quit()
                driver = webdriver.Chrome(self.brower_path, options=option)
                
        driver.quit()
        
    def get_names(self):
        #爬取6个榜单的角色的股东或注资人的name和nickname
        if os.path.isfile(self.mapid_path):
            df_oldnames = pd.read_excel(self.mapid_path)
            self.oldnames = df_oldnames.set_index("name").to_dict()["bgmid"]
            
        driver = webdriver.Chrome(self.brower_path, options=option)
        flag=1
        while not self.qicoCharacterId.empty():
            if flag:
                #这里判断一下的目的是，如果报错了的话，重启浏览器后接着上一次的继续爬，不要跳过出错的那次
                if not self.qmCharacterId.empty():
                    #先爬上市角色的股东
                    CharacterId = ('mchar', str(self.qmCharacterId.get()))
                else:
                    #再爬ico角色注资的人
                    CharacterId = ('icochar', str(self.qicoCharacterId.get()))
            flag = 1
            if CharacterId[0] == 'mchar':
                driver.get("https://www.tinygrail.com/api/chara/users/{CharacterId}/1/1000".format(
                        CharacterId=CharacterId[1]))
            else:
                driver.get("https://www.tinygrail.com/api/chara/initial/users/{CharacterId}/1/1000".format(
                        CharacterId=CharacterId[1]))
            try:
                WebDriverWait(driver, 5, 0.5).until(lambda x: x.find_element_by_xpath("/html/body/pre"))
                json_=driver.find_element_by_xpath('/html/body/pre').text
                dict_=json.loads(json_)
                shareholders=dict_['Value']['Items']
                for i in shareholders:
                    if i['Name'] not in self.shareholderNames and i['Name'] not in self.oldnames and '.' not in i['Name']:
                        self.shareholderNames.append(i['Name'])
                        if 'Nickname' in i:
                            self.shareholderNicknames.append(i['Nickname'])
                            print(i['Nickname'], i['Name'])
                        elif 'NickName' in i:
                            self.shareholderNicknames.append(i['NickName'])
                            print(i['NickName'], i['Name'])
            except (NoSuchElementException, TimeoutException, WebDriverException):
                #报错，重启浏览器
                flag = 0
                driver.quit()
                driver = webdriver.Chrome(self.brower_path, options=option)
                
        if self.shareholderNames:        
            driver.quit()
            #生成股东或注资人name和nickname表格
            dict_name = {'name':self.shareholderNames, 'nickname':self.shareholderNicknames}
            df_name = pd.DataFrame(dict_name)
            df_name = df_name[['name','nickname']]
            if os.path.isfile(self.name_path):
                #将旧数据和新数据合并
                df_old = pd.read_excel(self.name_path)
                df_name = pd.concat([df_name, df_old])
                #去重
                df_name = df_name.drop_duplicates(['name'])
            df_name.to_excel(self.name_path, index=False)
            print('已生成新的all_name.xlsx文件')
        else:
            driver.quit()
            self.quit = True
            
        
    def get_bgmids(self):
        #爬取name到bgmid的映射表
        driver = webdriver.Chrome(self.brower_path, options=option)
        flag = 1
        while not self.qShareholderName.empty():
            if flag:
                #这里判断一下的目的是，如果报错了的话，重启浏览器后接着上一次的继续爬，不要跳过出错的那次
                shareholderName = str(self.qShareholderName.get())
            flag = 1
            driver.get('http://mirror.api.bgm.rin.cat/user/{shareholderName}'.format(shareholderName=shareholderName))
            try:
                WebDriverWait(driver, 5, 0.5).until(lambda x: x.find_element_by_xpath("/html/body/pre"))
                json_=driver.find_element_by_xpath('/html/body/pre').text
                dict_=json.loads(json_)
                self.bgmids.append([shareholderName, dict_['id'], 'https://bgm.tv/user/'+str(dict_['id'])])
            except (NoSuchElementException, TimeoutException, WebDriverException):
                #报错，重启浏览器
                flag = 0
                driver.quit()
                driver = webdriver.Chrome(self.brower_path, options=option)
            except KeyError:
                print(dict_)
        driver.quit()
        
        df_bgmid = pd.DataFrame(self.bgmids)
        df_bgmid.columns = ['name', 'bgmid', 'url']
        if os.path.isfile(self.bgmid_path):
            #将旧数据和新数据合并
            df_old = pd.read_excel(self.bgmid_path)
            df_bgmid = pd.concat([df_bgmid, df_old])
            #去重
            df_bgmid = df_bgmid.drop_duplicates(['bgmid'])
        df_bgmid.to_excel(self.bgmid_path, index=False)
        print('已生成新的all_bgmid.xlsx文件')
            
    def get_tinygrailIds(self):
        #爬取bgmid到小圣杯id的映射表
        driver = webdriver.Chrome(self.brower_path, options=option)
        flag = 1
        while not self.qBgmid.empty():
            
            if flag:
                #这里判断一下的目的是，如果报错了的话，重启浏览器后接着上一次的继续爬，不要跳过出错的那次
                bgmid = str(self.qBgmid.get())
            flag = 1
            driver.get("https://www.tinygrail.com/api/chara/user/assets/{bgmid}".format(bgmid=bgmid))
            try:
                WebDriverWait(driver, 5, 0.5).until(lambda x: x.find_element_by_xpath("/html/body/pre"))
                json_=driver.find_element_by_xpath('/html/body/pre').text
                dict_=json.loads(json_)
                self.tinygrailIds.append([dict_['Value']['Id'], bgmid])
            except (NoSuchElementException, TimeoutException, WebDriverException):
                #报错，重启浏览器
                flag = 0
                driver.quit()
                driver = webdriver.Chrome(self.brower_path, options=option)
        
        driver.quit()
        
        df_tinygrailId = pd.DataFrame(self.tinygrailIds)
        df_tinygrailId.columns = ['tinygrailId', 'bgmid']
        if os.path.isfile(self.tinygrailId_path):
            #将旧数据和新数据合并
            df_old = pd.read_excel(self.tinygrailId_path)
            df_tinygrailId = pd.concat([df_tinygrailId, df_old])
            #去重
            df_tinygrailId = df_tinygrailId.drop_duplicates(['bgmid'])
        df_tinygrailId.to_excel(self.tinygrailId_path, index=False)
        
    def gen_mapid(self):
        df_tinygrailId = pd.read_excel(self.tinygrailId_path)
        df_name = pd.read_excel(self.name_path)
        df_bgmid = pd.read_excel(self.bgmid_path)
        #合并新表和旧表
        df_merge = pd.merge(df_tinygrailId, df_bgmid)
        df_merge = pd.merge(df_merge, df_name).sort_values(['tinygrailId'], ascending=False)
        dfs = df_merge[['tinygrailId', 'nickname', 'url', 'bgmid', 'name']]
        dfs.to_excel(self.mapid_path, index=False)
        print('已生成新的mapId.xlsx文件。完成。')
        print('新增用户数：'+str(df_tinygrailId.shape[0]-len(self.oldnames)))
        print('共爬到'+str(df_tinygrailId.shape[0])+'名用户')

    def my_treading(self, func, nThreads):
        threads=[]
        for _ in range(nThreads):
            thread = threading.Thread(target=func)
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

if __name__=="__main__":
    
    ti=time.time()

    usr = User()
    #gen_all_name_flag 设置为1时更新'all_name.xlsx'文件，设置为0时不更新，直接读取。
    #gen_all_bgmid_flag, gen_all_tinygrailId_flag同理。
    gen_all_name_flag, gen_all_bgmid_flag, gen_all_tinygrailId_flag = 1,1,1
    nThreads=1
    
    if gen_all_name_flag == 0 and os.path.isfile(usr.name_path):
        #如果设置不生成all_name.xlsx文件且路径中存在all_name.xlsx文件，则读取已有的文件
        shdns = pd.read_excel(usr.name_path)['name'].values.tolist()
        shdnns = pd.read_excel(usr.name_path)['nickname'].values.tolist()
        [(usr.shareholderNames.append(shdn), usr.shareholderNicknames.append(shdnn)) 
            for shdn, shdnn in zip(shdns, shdnns) if shdn not in usr.oldnames and '.' not in shdn]
        if len(usr.shareholderNames) == 0:
            usr.quit = True
    else:
        #否则运行爬虫
        #爬取6个榜单的角色id，爬取股东或注资人name和nickname
        usr.put_url()
        usr.my_treading(usr.get_characterIds, nThreads = 1)
        
        usr.put_characterId()
        usr.my_treading(usr.get_names, nThreads = nThreads)
        
    if usr.quit == False:
        if gen_all_bgmid_flag == 0 and os.path.isfile(usr.bgmid_path):
            #如果设置不生成all_bgmid.xlsx文件且路径中存在all_bgmid.xlsx文件，则读取已有的文件
            bgmids = pd.read_excel(usr.bgmid_path)['bgmid'].values.tolist()
            [usr.bgmids.append(bgmid) for bgmid in bgmids if bgmid not in usr.oldnames.values()]
            if len(usr.bgmids) == 0:
                usr.quit = True
        else:
            #否则运行爬虫
            #爬取name到bgmid的映射表
            usr.put_shareholderName()
            usr.my_treading(usr.get_bgmids, nThreads = nThreads)
            
    if usr.quit == False:
        if gen_all_tinygrailId_flag == 0 and os.path.isfile(usr.tinygrailId_path):
            #如果设置不生成all_tinygrailId.xlsx文件且路径中存在all_tinygrailId.xlsx文件，则读取已有的文件
            usr.gen_mapid()
        else:
            #否则运行爬虫
            #爬取bgmid到小圣杯id的映射表
            usr.put_bgmid()
            usr.my_treading(usr.get_tinygrailIds, nThreads = nThreads)
            
            usr.gen_mapid()
    else:
        print('无新用户')
    
    to=time.time()
    print('execute time: '+str(to-ti)+'s')

