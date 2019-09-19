# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 19:23:31 2019

@author: allegra
"""
"""
0.有bug
1.功能：爬取六个榜单所有的股东或注资人（其实只用爬4个榜单。1个涨幅榜3个ico榜）。
2.使用了多线程。
3.每个页面会等待10秒钟，超时会重启driver。
4.爬过一遍后，下次再运行本爬虫就会只爬新增的用户。
5.最后的结果保存在'mapId.xlsx'中。其他三个文件是中间产物，也不要删，某些情况下能提升爬虫速度。
6.gen_all_name_flag 设置为1时更新'all_name.xlsx'文件，设置为0时不更新，直接读取。
  gen_all_bgmid_flag, gen_all_tinygrailId_flag同理。
"""

from selenium import webdriver
import json
import os
import pandas as pd
import time
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

option = webdriver.ChromeOptions()
#True为静默模式，False为非静默模式
option.headless = False

class User(object):
    
    def __init__(self):
        self.brower_path=r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
        
        self.tinygrailid_path = './result/new_user_tinygrail_id.xlsx'
        self.name_path = './result/all_name.xlsx'
        self.bgmid_path = './result/all_bgmid.xlsx'
        self.tinygrailId_path = './result/all_tinygrailId.xlsx'
        self.mapid_path = './result/mapId.xlsx'
        
        self.bgmids = []
        self.tinygrailIds = []
        self.oldid = 0
        self.mapids = []
        self.oldbgmids = []
        
    def get_tinygrailIds(self):
        #爬取bgmid到小圣杯id的映射表
        driver = webdriver.Chrome(self.brower_path, options=option)
        flag = 1
        bgmid = 495870
        while bgmid < 497600:
            if flag:
                #这里判断一下的目的是，如果报错了的话，重启浏览器后接着上一次的继续爬，不要跳过出错的那次
                bgmid += 1
                if bgmid <= self.oldid:
                    continue
            flag = 1
            driver.get("https://www.tinygrail.com/api/chara/user/assets/{bgmid}".format(bgmid=bgmid))
            try:
                WebDriverWait(driver, 10, 0.5).until(lambda x: x.find_element_by_xpath("/html/body/pre"))
                json_=driver.find_element_by_xpath('/html/body/pre').text
                dict_=json.loads(json_)
                if 'Value' in dict_:
                    self.tinygrailIds.append([dict_['Value']['Id'], 'https://bgm.tv/user/'+str(bgmid), bgmid])
                    print(dict_['Value']['Id'], bgmid)
            except (NoSuchElementException, TimeoutException, WebDriverException):
                #报错，重启浏览器
                flag = 0
                driver.quit()
                driver = webdriver.Chrome(self.brower_path, options=option)
        
        driver.quit()
        if self.tinygrailIds:
            df_tinygrailId = pd.DataFrame(self.tinygrailIds)
            df_tinygrailId.columns = ['tinygrailId', 'url', 'bgmid']
            if os.path.isfile(self.tinygrailid_path):
                #将旧数据和新数据合并
                df_old = pd.read_excel(self.tinygrailid_path)
                df_tinygrailId = pd.concat([df_old, df_tinygrailId])
                #去重
                df_tinygrailId = df_tinygrailId.drop_duplicates(['bgmid'])
                df_tinygrailId = df_tinygrailId.sort_values(['tinygrailId'], ascending=False)
            df_tinygrailId.to_excel(self.tinygrailid_path, index=False)
            print('已生成新的new_user_tinygrail_id.xlsx文件')
        else:
            print('无新用户')
    
    def get_mapid(self):
        #爬取bgmid到name的映射表
        driver = webdriver.Chrome(self.brower_path, options=option)
        
        df_bgmids = pd.read_excel(usr.tinygrailid_path)
        self.bgmids = df_bgmids['bgmid'].values.tolist()
        self.dict_bgmids = df_bgmids.set_index('bgmid').to_dict()["tinygrailId"]
        self.oldbgmids = pd.read_excel(usr.mapid_path)['bgmid'].values.tolist()
        flag = 1
        while self.bgmids:
            if flag:
                #这里判断一下的目的是，如果报错了的话，重启浏览器后接着上一次的继续爬，不要跳过出错的那次
                bgmid = self.bgmids.pop(0)
                if bgmid in self.oldbgmids:
                    continue 
            flag = 1
            driver.get('http://mirror.api.bgm.rin.cat/user/{bgmid}'.format(bgmid=bgmid))
            try:
                WebDriverWait(driver, 5, 0.5).until(lambda x: x.find_element_by_xpath("/html/body/pre"))
                json_=driver.find_element_by_xpath('/html/body/pre').text
                dict_=json.loads(json_)
                self.mapids.append([self.dict_bgmids[bgmid], dict_['nickname'], 
                                    'https://bgm.tv/user/'+dict_['username'], bgmid, dict_['username']])
            except (NoSuchElementException, TimeoutException, WebDriverException):
                #报错，重启浏览器
                flag = 0
                driver.quit()
                driver = webdriver.Chrome(self.brower_path, options=option)
            except KeyError:
                print(dict_)
        driver.quit()
        
        if self.mapids:
            df_mapid = pd.DataFrame(self.mapids)
            df_mapid.columns = ['tinygrailId', 'nickname', 'url', 'bgmid', 'name']
            if os.path.isfile(self.mapid_path):
                #将旧数据和新数据合并
                df_old = pd.read_excel(self.mapid_path)
                df_mapid = pd.concat([df_old, df_mapid])
                #去重
                df_mapid = df_mapid.drop_duplicates(['bgmid'])
                df_mapid = df_mapid.sort_values(['tinygrailId'], ascending=False)
                
                df_old_name = pd.read_excel(self.name_path)
                df_name = pd.concat([df_old_name, df_mapid[['name','nickname']]])
                df_name = df_mapid.drop_duplicates(['name'])
                df_name.to_excel(self.name_path, index=False)
                print('已生成新的all_name.xlsx文件')
                
                df_old_bgmid = pd.read_excel(self.bgmid_path)
                df_bgmid = pd.concat([df_old_bgmid, df_mapid[['name', 'bgmid', 'url']]])
                df_bgmid = df_bgmid.drop_duplicates(['name'])
                df_bgmid.to_excel(self.bgmid_path, index=False)
                print('已生成新的all_bgmid.xlsx文件')
                
                df_old_tinygrailId = pd.read_excel(self.tinygrailId_path)
                df_tinygrailId = pd.concat([df_old_tinygrailId, df_mapid[['tinygrailId', 'bgmid']]])
                df_tinygrailId = df_tinygrailId.drop_duplicates(['bgmid'])
                df_tinygrailId.to_excel(self.tinygrailId_path, index=False)
                print('已生成新的all_tinygrailId.xlsx文件')
                
            df_mapid.to_excel(self.mapid_path, index=False)
            print('已生成新的mapId.xlsx文件')
            print('新增用户数：'+str(df_mapid.shape[0]-len(self.oldbgmids)))
            print('共爬到'+str(df_mapid.shape[0])+'名用户')
        else:
            print('无新用户')
        
if __name__=="__main__":
    
    ti=time.time()

    usr = User()
    #gen_all_name_flag 设置为1时更新'all_name.xlsx'文件，设置为0时不更新，直接读取。
    #gen_all_bgmid_flag, gen_all_tinygrailId_flag同理。
    gen_all_tinygrailId_flag, gen_all_names_flag = 1, 1
    nThreads=1
    
    if gen_all_tinygrailId_flag == 1:
        if os.path.isfile(usr.tinygrailid_path):
            usr.oldid = pd.read_excel(usr.tinygrailid_path)['bgmid'].values.tolist()[0]
            #爬取name到bgmid的映射表
            usr.get_tinygrailIds()
        else:
            usr.get_tinygrailIds()
    if gen_all_names_flag == 1:
        usr.get_mapid()
    
    to=time.time()
    print('execute time: '+str(to-ti)+'s')

