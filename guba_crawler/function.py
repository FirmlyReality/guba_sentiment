import requests
from lxml import etree
from bs4 import BeautifulSoup
import pandas as pd
import traceback
import time, re

def get_html(url):
    time.sleep(0.4)
    print("Get Url: "+str(url))
    retry = 0
    while True and retry < 3:
        try:
            html = requests.get(url)
        except Exception as e:
            print(traceback.format_exc())
            print("Connect Failed. Sleep 30s then Retry...")
            time.sleep(30)
        else:
            if str(html.status_code) != "200":
                print("Error "+ str(html.status_code))
                print("Connect Failed. Sleep 30s then Retry...")
                time.sleep(30)
                retry += 1
            else:
                return html
    return None

#返回指定个股吧指定页的所有讨论帖的id、标题、作者、url
def get_guba_list(code='600000',page=1):
    url = 'http://guba.eastmoney.com/list,' + code + '_' +str(page)+ '.html'
    retry = 0
    success = False
    while not success and retry < 5:
        try:
            html = get_html(url)
            if html is None:
                return None
            bs = BeautifulSoup(html.text,"lxml")
            art = bs.select('#articlelistnew')[0]
            success = True
        except Exception as err:
            print(traceback.format_exc())
            retry += 1
            print("Connect Failed. Sleep 30s then Retry...")
            time.sleep(30)
    if not success:
        print("Error! Exit!")
        exit(0)
    divs = art.findAll('div')
    code_list = []
    tieziid_list = []
    title_list = []
    author_list = []
    url_list = []
    tag_list = []
    read_list = []
    post_list = []
    updatet_list = []
#由于网页结构的原因，要设置个分支    
    for i in range(1,len(art.findAll('div'))-1):
        if len(divs[i].findAll('em')) != 0:
            continue
        if len(divs[i].findAll('span')) == 6:
            url = divs[i].findAll('span')[2].findAll('a')[0]['href']
            if url.split(",")[1] != code:
                continue
            try:
                updatet_list.append(divs[i].select(".l5")[0].text)
            except Exception as e:
                continue
            try:
                read_list.append(divs[i].findAll('span')[0].text)
            except Exception as e:
                read_list.append('0')
            try:
                post_list.append(divs[i].findAll('span')[1].text)
            except Exception as e:
                post_list.append('0')
            try:
                tieziid_list.append(divs[i].findAll('span')[2].findAll('a')[0]['href'].split(',')[2].split('.')[0])
            except Exception as e:
                tieziid_list.append('-1')
            try:
                url_list.append(divs[i].findAll('span')[2].findAll('a')[0]['href'])
            except Exception as e:
                url_list.append('/')
            try:
                title_list.append(divs[i].findAll('span')[2].findAll('a')[0]['title'])
            except Exception as e:
                title_list.append(' ')
            try:
                author_list.append(divs[i].findAll('span')[3].text)
            except Exception as e:
                author_list.append(' ')

            code_list.append(code)
        elif len(divs[i].findAll('span')) == 7:
            url = divs[i].findAll('span')[2].findAll('a')[0]['href']
            if url.split(",")[1] != code:
                continue
            try:
                updatet_list.append(divs[i].select(".l5")[0].text)
            except Exception as e:
                continue
            try:
                read_list.append(divs[i].findAll('span')[0].text)
            except Exception as e:
                read_list.append('0')
            try:
                post_list.append(divs[i].findAll('span')[1].text)
            except Exception as e:
                post_list.append('0')
            try:
                tieziid_list.append(divs[i].findAll('span')[2].findAll('a')[0]['href'].split(',')[2].split('.')[0])
            except Exception as e:
                tieziid_list.append('-1')
            try:
                url_list.append(divs[i].findAll('span')[2].findAll('a')[0]['href'])
            except Exception as e:
                url_list.append('/')
            try:
                title_list.append(divs[i].findAll('span')[2].findAll('a')[0]['title'])
            except Exception as e:
                title_list.append(' ')
            try:
                author_list.append(divs[i].findAll('span')[4].text)
            except Exception as e:
                author_list.append(' ')   
            code_list.append(code)
    data = pd.DataFrame()
    data['code'] = code_list
    data['read'] = read_list
    data['replys'] = post_list
    data['title'] = title_list
    data['author'] = author_list
    data['url'] = url_list
    data['update_time'] = updatet_list
    data.index = tieziid_list
    return data

def filter_content(soup):
    content = str(soup)
    content = re.sub(r'<div.*?>|</div>',r'',content)
    content = re.sub(r'<br>|<br/>',r'\n',content).strip()
    content = re.sub(r'<.*?>',r'',content).strip()
    for img in soup.findAll('img'):
        try:
            content = content + "[" + img['title'] + "]"
        except Exception as e:
            print(traceback.format_exc())
    return content.replace("\r","")
  
#返回指定帖子的发帖时间以及帖子标题、内容、所有回复。
#时间格式为“%Y-%m-%d %H:%M:%S”    
def get_guba_tiezi(tieziid,replys_num,tiezi_url,start_time=None,end_time=None):
    url = 'http://guba.eastmoney.com' + tiezi_url
    #print("Get Tiezi from url: "+str(url))
    html = get_html(url)
    if html is None:
        return [None,None,None,None]
    bs = BeautifulSoup(html.text,"lxml")
    try:
        tiezi = bs.select('#zwcontent')[0]
    except Exception as e:
        print(traceback.format_exc())
        return [None,None,None,None]
    
    #收集帖子发帖时间
    pub_time_str = tiezi.select('#zwconttb')[0].select('.zwfbtime')[0].text
    timep = re.compile('[\d]+-[\d]+-[\d]+ [\d]+:[\d]+:[\d]+')
    pub_time = re.search(timep, pub_time_str).group()
    if start_time is not None and end_time is not None and (pub_time < start_time or pub_time > end_time):
        #只收集限定时间内的帖子
        return [pub_time,None,None,None]
    
    #收集帖子标题和内容
    try:
        title = tiezi.select('#zwconttbt')[0].text.strip().replace("\r","").replace("\n","")
        content_soup = tiezi.select('#zwconbody')[0].select('.stockcodec')[0]
        content = filter_content(content_soup)
    except Exception as e:
        print(traceback.format_exc())
        return [pub_time,None,None,None]
    #print(content)
    
    #收集回复
    rp_id_list = []
    rp_author_list = []
    rp_time_list = []  
    rp_content_list = []
    rp_rpid_list = []
    tieziid_list = []
    try:
        reply_soup = bs.select('#zwlist')[0]
    except Exception as e:
        print(traceback.format_exc())
        return [pub_time,None,None,None]        
    page = 1
    cnt = 0
    while True:
        reply_list = reply_soup.findAll('div',{'class':'zwli clearfix'})
        if len(reply_list) == 0:
            break
        for i in range(len(reply_list)):
            cnt += 1
            rp_time_str = reply_list[i].select('.zwlitime')[0].text.strip()
            rp_time_str = re.sub(r' +',r' ',rp_time_str)
            rp_time = re.search(timep, rp_time_str).group()
            if start_time is not None and end_time is not None and (rp_time < start_time or rp_time > end_time):
                #只收集限定时间内的回复
                continue
            try:
                rp_time_list.append(rp_time)
            except Exception as e:
                rp_time_list.append(' ')                
            try:
                rp_id_list.append(reply_list[i]['data-huifuid'])
            except Exception as e:
                rp_id_list.append('-1')
            try:
                rp_author_list.append(reply_list[i].select('.zwlianame')[0].text.strip())
            except Exception as e:
                rp_author_list.append(' ')
            try:
                rp_rpid_soup = reply_list[i].select('.zwlitalkboxtext')[0]
                rp_rpid_list.append(rp_rpid_soup['data-huifuid'])
            except Exception as e:
                rp_rpid_list.append('')
            try:
                rp_content_soup = reply_list[i].findAll('div',{'class':'zwlitext stockcodec'})[0]
                rp_content_list.append(filter_content(rp_content_soup))
            except Exception as e:
                rp_content_list.append(' ')
            tieziid_list.append(tieziid)
        
        #切换下一页
        if cnt >= int(replys_num):
            break
        page += 1
        url = 'http://guba.eastmoney.com' + tiezi_url.replace('.','_'+str(page)+'.')
        #print("Get Reply from url: "+str(url))
        rp_html = get_html(url)
        if rp_html is None:
            break
        reply_soup = BeautifulSoup(rp_html.text,"lxml").select('#zwlist')
        if len(reply_soup) < 1:
            break
        reply_soup = reply_soup[0]
        #print(reply_soup)
    
    data = pd.DataFrame()
    data['tieziid'] = tieziid_list
    data['author'] = rp_author_list
    data['time'] = rp_time_list
    data['rp2id'] = rp_rpid_list
    data['content'] = rp_content_list
    data.index = rp_id_list
    return [pub_time,title,content,data]

if __name__ == "__main__":
    pub_time, title, content, data = get_guba_tiezi("172511131",0,"/news,601989,172511131.html")
    resfile = open("test.txt","w")
    resfile.write(title)