# [allegray](https://bgm.tv/user/allegray)

## 爬取所有上市角色的发行价和上市时间 [gen_price.py](https://github.com/sanyifund/scripts/tree/master/python/gen_price.py)
爬取所有上市角色的发行价和上市时间。早期交易记录数据缺失，故部分角色暂时没有爬到发行价与上市时间。

## 爬取所有正在ico中的角色 [ico_monitor.py](https://github.com/sanyifund/scripts/tree/master/python/ico_monitor.py))
爬取所有正在ico中的角色及其相关信息。

## 爬取小圣杯开启以来新注册bangumi的用户 [new_bgm_user.py](https://github.com/sanyifund/scripts/tree/master/python/new_bgm_user.py.py))
0.有bug
1.得到新注册用户的小圣杯id与bgmid的对应关系。  
2.爬过一遍后，下次再运行本爬虫就会只爬新增的用户。  
3.最后的结果保存在'mapId.xlsx'中。其他三个文件是中间产物，也不要删，某些情况下能提升爬虫速度。  
4.gen_all_tinygrailId_flag 设置为1时更新'new_user_tinygrail_id.xlsx'文件，设置为0时不更新，直接读取。  
  gen_all_names_flag同理。

## 追踪一个用户的全市所有交易记录 [stk_single.py](https://github.com/sanyifund/scripts/tree/master/python/stk_single.py))
追踪一个用户的全市所有交易记录。

## 查找某角色所有的挂单、历史交易、股东股份 [tinygrail_utils.py](https://github.com/sanyifund/scripts/tree/master/python/tinygrail_utils.py))
查找某角色所有的挂单、历史交易、股东股份。但是查不到没股的用户。

## 查找某角色所有的挂单、历史交易、股东股份增强版 [tinygrail_utils_plus.py](https://github.com/sanyifund/scripts/tree/master/python/tinygrail_utils_plus.py))
查找某角色所有的挂单、历史交易、股东股份。可以查到没股的用户。

## 爬取用户的小圣杯id与bgmid的对应关系 [user.py](https://github.com/sanyifund/scripts/tree/master/python/user.py))
0.有bug  
1.功能：爬取六个榜单所有的股东或注资人（其实只用爬4个榜单。1个涨幅榜3个ico榜）。  
2.每个页面会等待5秒钟，超时会重启driver。  
3.爬过一遍后，下次再运行本爬虫就会只爬新增的用户。  
4.最后的结果保存在'mapId.xlsx'中。其他三个文件是中间产物，也不要删，某些情况下能提升爬虫速度。  
5.gen_all_name_flag 设置为1时更新'all_name.xlsx'文件，设置为0时不更新，直接读取。  
  gen_all_bgmid_flag, gen_all_tinygrailId_flag同理。  






