"""
爬取所有正在ico中的角色及其相关信息。
"""
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 21:33:18 2019

@author: allegra
"""

from selenium import webdriver
import json
import pandas as pd
import time
import os
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

option = webdriver.ChromeOptions()
#True为静默模式，False为非静默模式
option.headless = False

class User(object):
    
    def __init__(self):
        self.brower_path=r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
        
        self.ico_text_path = './result/ico_text.xlsx'
        self.mapid_path = './result/mapId.xlsx'
        self.ico_monitor_path = './result/ico_monitor.xlsx'
        
        self.dict_char_usrs = []
        self.items = []
        self.chars_info = []
        self.driver = webdriver.Chrome(self.brower_path, options=option)
        self.df_ico_monitor = pd.read_excel(self.ico_monitor_path)
        self.dict_ico = self.df_ico_monitor.set_index('角色小圣杯id').to_dict()
        
    def ico_monitor(self):
        #爬取所有ico角色的api文本。只能查到角色的小圣杯id，查不到角色名或者角色bgmid。能查到注资人的一些信息。
        flag = 1
        #把角色小圣杯id从1到2500遍历一遍。小圣杯id前1000的角色如果失败了重新开启的话也需要爬，所以不要把icoid改大。
        icoid = 0
        while icoid < 2500:
            if flag:
                #这里判断一下的目的是，如果报错了的话，重启浏览器后接着上一次的继续爬，不要跳过出错的那次
                icoid += 1
            flag = 1
            self.driver.get("https://www.tinygrail.com/api/chara/initial/users/{icoid}/1/1000".format(icoid=icoid))
            try:
                WebDriverWait(self.driver, 1, 0.5).until(lambda x: x.find_element_by_xpath("/html/body/pre"))
                json_=self.driver.find_element_by_xpath('/html/body/pre').text
                dict_=json.loads(json_)
                if not dict_['Value']['TotalPages'] == 0:
                    self.dict_char_usrs.append({'icoid':icoid, 'text':json_})
                    print(icoid)
                time.sleep(0.05)
            except (NoSuchElementException, TimeoutException, WebDriverException):
                #报错，重启浏览器 
                flag = 0
                self.driver.quit()
                self.driver = webdriver.Chrome(self.brower_path, options=option)
        
        if self.dict_char_usrs:
            df_char_usrs = pd.DataFrame(self.dict_char_usrs)
            df_char_usrs = df_char_usrs[['icoid', 'text']]
            df_char_usrs = df_char_usrs.sort_values(['icoid'], ascending=False)
            df_char_usrs.to_excel(self.ico_text_path, index=False)
            print('已生成新的ico_text.xlsx文件')
        else:
            print('无新角色')
    
    def get_usr_char(self, bgmid, init_usr, total_usrs):
        #找出最早注资用户的bgmid后，查他所有ico的角色，找出注资时间相同的角色，该角色则为所找的角色。
        while True:
            try:
                self.driver.get('https://www.tinygrail.com/api/chara/user/assets/{bgmid}/true'.format(bgmid=bgmid))
                WebDriverWait(self.driver, 5, 0.5).until(lambda x: x.find_element_by_xpath("/html/body/pre"))
                json_=self.driver.find_element_by_xpath('/html/body/pre').text
                dict_=json.loads(json_)
                chars = dict_['Value']['Initials']
                for char in chars:
                    if char['Begin'] == init_usr['Begin']:
                        self.chars_info.append((char['Name'], char['State'], init_usr['NickName'], char['Total'], 
                                                'https://bgm.tv/character/'+str(char['CharacterId']), total_usrs, 
                                                char['Begin'], char['End'], char['CharacterId'], init_usr['InitialId'], 
                                                bgmid, init_usr['UserId'], init_usr['Name']))
                        #找到了后就返回
                        return
                #遍历完后还没找到，说明该角色已退市或上市。返回
                return
            except (NoSuchElementException, TimeoutException, WebDriverException):
                #报错，重启浏览器
                self.driver.quit()
                self.driver = webdriver.Chrome(self.brower_path, options=option)
    
    def get_char_info_from_ico_monitor(self, item, char_icoid, total_usrs):
        char_name = self.dict_ico['角色名'][char_icoid]
        init_fund = self.dict_ico['启动人注资额'][char_icoid]
        init_nickname = self.dict_ico['启动人昵称'][char_icoid]
        char_url = self.dict_ico['url'][char_icoid]
        char_begin = self.dict_ico['开始时间'][char_icoid]
        char_end = self.dict_ico['结束时间'][char_icoid]
        char_bgmid = self.dict_ico['角色bgmid'][char_icoid]
        init_bgmid = self.dict_ico['启动人bgmid'][char_icoid]
        init_grailid = self.dict_ico['启动人小圣杯id'][char_icoid]
        init_name = self.dict_ico['启动人name'][char_icoid]
        char_total_fund = sum([usr['Amount'] for usr in item])
        self.chars_info.append((char_name, init_fund, init_nickname, char_total_fund, char_url, total_usrs, char_begin, char_end, char_bgmid, char_icoid, init_bgmid, init_grailid, init_name))
    
    def get_char_bgm_id(self):
        #爬取角色小圣杯id到bgmid的映射表
        df_items = pd.read_excel(self.ico_text_path)
        self.items = df_items['text'].values.tolist()
        dict_text_icoid = df_items.set_index("text").to_dict()["icoid"]
        df_map_id = pd.read_excel(self.mapid_path)
        #dict。key为name，value为bgmid。
        self.dict_name_bgmid = df_map_id.set_index('name').to_dict()["bgmid"]
        flag = 1
        while self.items:
            print(len(self.items))
            if flag:
                #这里判断一下的目的是，如果报错了的话，重启浏览器后接着上一次的继续爬，不要跳过出错的那次
                text = self.items.pop(0)
                item = json.loads(text)['Value']['Items']
            flag = 1
            char_ico_id = dict_text_icoid[text]
            if os.path.isfile(self.ico_monitor_path) and char_ico_id in self.df_ico_monitor['角色小圣杯id'].values:
                self.get_char_info_from_ico_monitor(item, char_ico_id, len(item))
                continue
            df_item_chars = pd.DataFrame(item)
            #把“开始时间”这一列由字符串转成整数
            df_item_chars_begin = df_item_chars['Begin'].apply(lambda x: x.replace('-', '').replace('T', '').replace(':', ''))
            #找出注资时间最早的人
            init_usr = df_item_chars.loc[df_item_chars_begin.astype('int64').idxmin()]
            if init_usr['Name'] in self.dict_name_bgmid:
                #如果mapId.xlsx里有启动用户的name，则从该表中找出启动用户的bgmid
                bgmid = self.dict_name_bgmid[init_usr['Name']]
                self.get_usr_char(bgmid, init_usr, len(item))
                
            elif not init_usr['Avatar'] == 'http://lain.bgm.tv/pic/user/l/icon.jpg':
                #如果启动用户上传过头像，则从头像的url中提取出启动用户的bgmid
                bgmid = init_usr['Avatar'].split('/')[-1].split('.')[0]
                self.get_usr_char(bgmid, init_usr, len(item))
                
            else:
                #否则通过api根据name查找用户的bgmid
                self.driver.get('http://mirror.api.bgm.rin.cat/user/{name}'.format(name=init_usr['Name']))
                try:
                    WebDriverWait(self.driver, 5, 0.5).until(lambda x: x.find_element_by_xpath("/html/body/pre"))
                    json_=self.driver.find_element_by_xpath('/html/body/pre').text
                    dict_=json.loads(json_)
                    bgmid = dict_['id']
                    self.get_usr_char(bgmid, init_usr, len(item))
                except (NoSuchElementException, TimeoutException, WebDriverException):
                    #报错，重启浏览器
                    flag = 0
                    self.driver.quit()
                    self.driver = webdriver.Chrome(self.brower_path, options=option)
                except KeyError:
                    print(item)
        
        self.driver.quit()
        if self.chars_info:
            df_chars_info = pd.DataFrame(self.chars_info)
            df_chars_info.columns = ['角色名', '启动人注资额', '启动人昵称', '已筹集', 
                                     'url', '参与人数', 
                                     '开始时间', '结束时间', '角色bgmid', '角色小圣杯id', 
                                     '启动人bgmid', '启动人小圣杯id', '启动人name']
            df_chars_info = df_chars_info.sort_values(['参与人数', '已筹集'], ascending=True)
            df_chars_info.to_excel(self.ico_monitor_path, index=False)
            print('已生成新的ico_monitor.xlsx文件')
        else:
            print('无')
    

if __name__=="__main__":
    
    ti=time.time()

    usr = User()
    #gen_ico_text_flag设置为1时更新'ico_text.xlsx'文件，设置为0时不更新直接读取。
    gen_ico_text_flag = 1
    
    if gen_ico_text_flag == 1:
        #爬取所有ico角色
        usr.ico_monitor()
    usr.get_char_bgm_id()
    
    to=time.time()
    print('execute time: '+str(to-ti)+'s')