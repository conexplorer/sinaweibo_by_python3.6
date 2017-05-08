#-*- coding:utf-8 -*-
import re
import urlparse
import urllib
import urllib2
import time
from datetime import datetime
import datetime
import robotparser
import Queue
import time
from lxml import etree
import cookieget
from pymongo import MongoClient
import sys
reload(sys)
sys.setdefaultencoding('utf8')




def get_userurl(userurl, headers):
    time.sleep(6)
    request = urllib2.Request(userurl, headers=headers)
    html = urllib2.urlopen(request).read()
    info = re.findall('私信</a>&nbsp;<a href="(.*?)">资料</a>', html)
    url = 'http://weibo.cn' + info[0]
    return url

def get_userinfo(userid, headers):
    userurl = 'http://weibo.cn/' + userid
    match = re.findall('[a-zA-Z]', userid)
    if not match:
        userurl += '/info'
    else:
        userurl = get_userurl(userurl=userurl, headers=headers)
    print userurl
    time.sleep(6)
    request = urllib2.Request(userurl, headers=headers)
    html = urllib2.urlopen(request).read()

    username = re.findall('昵称:(.*?)<br/>', html)
    usersex = re.findall('性别:(.*?)<br/>', html)
    userregion = re.findall('地区:(.*?)<br/>', html)
    userbri = re.findall('生日:(.*?)<br/>', html)

    if not username:
        print "用户url构建错误，重新构建："
        userurl = 'http://weibo.cn/' + userid
        userurl = get_userurl(userurl=userurl, headers=headers)
        print userurl
        time.sleep(6)
        request = urllib2.Request(userurl, headers=headers)
        html = urllib2.urlopen(request).read()
        username = re.findall('昵称:(.*?)<br/>', html)
        usersex = re.findall('性别:(.*?)<br/>', html)
        userregion = re.findall('地区:(.*?)<br/>', html)
        userbri = re.findall('生日:(.*?)<br/>', html)
    if not username:
        username.append('NONE')
    if not usersex:
        usersex.append('NONE')
    if not userregion:
        userregion.append('NONE')
    if not userbri:
        userbri.append('NONE')

    print username[0], usersex[0], userregion[0], userbri[0]
    userinfo = {'name': username[0], 'gender': usersex[0], 'region': userregion[0], 'birthdate': userbri[0]}
    return userinfo

def get_text(html, headers):
    fulltexturl = re.findall('<a href=\'/comment/(.*?)\'>全文', html)
    datas = []
    selector = etree.HTML(html)
    content = selector.xpath('//span[@class="ctt"]')
    fulltextnum = 0
    bb = []
    b = selector.xpath('//div[@class="c"]/div[1]')
    for it in b:
        bb.append(unicode(it.xpath('string(.)')))
    i = 0
    for it in content:
        try:
            str = bb[i].split(' ​ ')[1][0]
        except:
            str = 'no'
        if (str == '全'):
            fulltext = get_fulltext(url=fulltexturl[fulltextnum], function='fulltext', headers=headers)
            fulltextnum += 1
            datas.append(fulltext)
        else:
            datas.append(unicode(it.xpath('string(.)')))
        i += 1
    return datas

def get_time(html, starttime):
    now_time = datetime.datetime.now()
    btimes = []
    times = []
    selector = etree.HTML(html)
    bbtime = selector.xpath('//span[@class="ct"]')
    for it in bbtime:
        btimes.append(unicode(it.xpath('string(.)')))
    for it in btimes:
        if '分钟' in it:
            num = re.findall('\d+', it)[0]
            yes_time = now_time + datetime.timedelta(minutes=-int(num))
            yes_time = yes_time.strftime('%Y-%m-%d %H:%M')
            times.append(yes_time)
        else:
            if '今天' in it:
                rtime = starttime[0:4] + '-' + starttime[4:6] + '-' + starttime[-2:] + ' ' + it[3:8]
                times.append(rtime)
            else:
                rtime = starttime[0:4] + '-' + starttime[4:6] + '-' + starttime[-2:] + ' ' + it[7:12]
                times.append(rtime)
    return times

def get_idlist(html):
    buseridlist = re.findall('<a class="nk" href="https://weibo.cn/(.*?)">', html)
    return buseridlist

def get_transpond_like_comment(html):
    transponds = re.findall('>转发\[(.*?)]</a>', html)
    likes = re.findall('>赞\[(.*?)\]</a>', html)
    comments = re.findall('>评论\[(.*?)\]</a>', html)
    return transponds, likes, comments


def get_comments(url, headers):
    datas = []
    finallyurl = url + '1'
    time.sleep(6)
    request = urllib2.Request(finallyurl, headers=headers)
    html = urllib2.urlopen(request).read()
    try:
        totalpage = re.findall('<input name="mp" type="hidden" value="(.*?)" />', html)[0]
    except:
        totalpage = '1'
    print "    评论总页数：", totalpage

    for item in range(1, int(totalpage) + 1):
        if item != 1:
            finallyurl = url + str(item)
            time.sleep(10)
            request = urllib2.Request(finallyurl, headers=headers)
            html = urllib2.urlopen(request).read()
        print "    当前评论网页：", finallyurl
        selector = etree.HTML(html)
        content = selector.xpath('//span[@class="ctt"]')
        for it in content:
            datas.append(unicode(it.xpath('string(.)')))
    return datas

def get_comments_urllist(html):
    comments_urllist = []
    bcomments_urllist = re.findall('<a href="https://weibo.cn/comment/(.*?)#cmtfrm" class="cc">评论', html)
    for it in bcomments_urllist:
        comments_urllist.append('https://weibo.cn/comment/' + it + '&page=')
    return comments_urllist


def get_islocation(html, headers):
    fulltexturl = re.findall('<a href=\'/comment/(.*?)\'>全文', html)
    fulltextnum = 0
    locations = []
    aa = []
    bb = []
    selector = etree.HTML(html)
    b = selector.xpath('//div[@class="c"]/div[1]')
    for it in b:
        bb.append(unicode(it.xpath('string(.)')))

    a = selector.xpath('//span[@class="ctt"]')
    for it in a:
        aa.append(unicode(it.xpath('string(.)')))
    for i in range(0, 10):
        try:
            if (bb[i].split(' ​ ')[1][0] == '显'):
                if (bb[i].split(' ​ ')[1][0] == '全'):
                    fulltext = get_fulltext(url=fulltexturl[fulltextnum], function='location', headers=headers)
                    fulltextnum += 1
                    locations.append(fulltext)
                else:
                    locations.append(aa[i].split(' ')[-2])
            else:
                    locations.append('NONE')
        except:
            locations.append('NONE')
    return locations

def get_fulltext(url, function, headers):
    finallyurl = 'https://weibo.cn/comment/' + url

    time.sleep(6)
    request = urllib2.Request(finallyurl, headers=headers)
    html = urllib2.urlopen(request).read()
    selector = etree.HTML(html)
    aa = []
    bb = []
    if (function == 'fulltext'):
        a = selector.xpath('//div[@class="c"]/div[1]/span')
        for it in a:
            aa.append(unicode(it.xpath('string(.)')))
        return aa[0]
    else:
        b = selector.xpath('//div[@class="c"]/div[1]/span/a')
        for it in b:
            bb.append(unicode(it.xpath('string(.)')))
        return bb[0]





def download(keyword, starttime, endtime, cookievalue, cache):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'cookie': cookievalue}

    preurl = "http://weibo.cn/search/mblog?hideSearchFrame=&keyword=" + keyword + '&advancedfilter=1&hasori=1&starttime=' + starttime + '&endtime=' + endtime + '&sort=time&page='
    data = []

    finallyurl = preurl + '1'
    print '当前关键词为：' + keyword
    time.sleep(6)
    request = urllib2.Request(finallyurl, headers=headers)
    html = urllib2.urlopen(request).read()
    try:
        totalpage = re.findall('<input name="mp" type="hidden" value="(.*?)" />', html)[0]
    except:
        totalpage = '1'
    print "内容总页数：", totalpage
    for webpagenum in range(1, int(totalpage)+1):
        try:
            print "当前微博日期为:" + starttime + "   开始爬取第" + str(webpagenum) + "个网页："
            if webpagenum != 1:
                finallyurl = preurl + str(webpagenum)
                time.sleep(6)
                request = urllib2.Request(finallyurl, headers=headers)
                html = urllib2.urlopen(request).read()
            print finallyurl
            datas = get_text(html=html, headers=headers)
            buseridlist = get_idlist(html=html)
            transponds, likes, comments_counts = get_transpond_like_comment(html=html)
            times = get_time(html=html, starttime=starttime)
            comments_urlist = get_comments_urllist(html=html)
            locations = get_islocation(html=html, headers=headers)
            # for it in buseridlist:
            #     print it
            useridlist = []
            for item in buseridlist:
                if item[1] == '/':
                    useridlist.append(item[2:])
                else:
                    useridlist.append(item)
            i = 0
            for text in datas:
                print '第' + str(i+1) + '条微博：'
                userid = useridlist[i]
                transpond = transponds[i]
                like = likes[i]
                comments_count = comments_counts[i]
                time1 = times[i]
                location = locations[i]
                userinfo = get_userinfo(userid=userid, headers=headers)
                if comments_count != '0':
                    print "    开始爬取评论"
                    comments = get_comments(url=comments_urlist[datas.index(text)], headers=headers)
                    print "    评论爬取完成"
                else:
                    comments = 'NONE'
                # for loc in islocations:
                #     print loc
                # if islocations[i] == '显示地图':
                #     location = text.split(' ')[-2]
                # else:
                #     location = 'NONE'
                try:
                    post = {'text': text, 'reposts_count': transpond, 'likes_count': like, 'comments_count': comments_count, 'comments': comments, 'location': location, 'date': time1, 'userinfo': userinfo}
                    cache.insert(post)
                except:
                    print "导入数据库出错，请检查数据库是否开启"
                print "爬取完成"
                i += 1
        except urllib2.HTTPError:
            print "服务器拒绝访问！"
            exit()
        except:
            print "其他错误"


def startscrape(cookie, db, keyword, starttime, endtime):
    my_collection = db['SinaWeiBoData']
    download(keyword=keyword, starttime=starttime, endtime=endtime, cookievalue=cookie, cache=my_collection)
