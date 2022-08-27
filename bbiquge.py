# -*- coding:utf-8 -*-
"""
author：Ranger
data：2021年12月06日
笔趣阁网址：https://www.bbiquge.net/

"""

import os
from bs4 import BeautifulSoup  # 网页解析，获取数据
import re  # 正则表达式，进行文字匹配
import urllib.request, urllib.error  # 定制URL，获取网页数据
import gzip  # 对进行过gzip压缩的数据进行解码
from io import BytesIO  # 解码
import xlwt  # 进行Excel操作


# import sqlite3  # 进行SQLite数据库操作


def main():
    mainURL = "https://www.bbiquge.net/top/allvote/"

    allRankingListData(mainURL)

    fictionURL = str(input("请输入想要下载的小说的URL："))# 请输入想要下载的小说的URL
    #
    # # 小说名
    fictionName = str(findFictionName(fictionURL))
    # print(fictionName)
    # 1.得到指定一个URL的网页内容
    # analysisURL(fictionURL)

    # # 2.爬取网页
    fictionDataList = getFictionData(fictionURL)

    # 3.保存目录数据
    # saveName = str(fictionName + ".xls")
    # saveData(fictionDataList, saveName)

    # 4.获取小说章节内容
    sectionOfContent(fictionDataList, fictionURL, fictionName)


# 排行榜数据爬取规则
# 排行榜页数
findLength = re.compile(r'<a class="last" href=".*?">(.*?)</a>')

# 小说类别
findClasses = re.compile(r'<span class="l1">(.*?)</span>')
# 小说链接
findFictionLink = re.compile(r'<span class="l2"><a href="(.*?)" target="_blank">.*?</a></span>')
# 小说名字
findName = re.compile(r'<span class="l2"><a href=".*?" target="_blank">(.*?)</a></span>')
# 小说作者
findAuthor = re.compile(r'<span class="l3">(.*?)</span>')
# 小说最新章节
findSection = re.compile(r'<span class="l4"><a href=".*?" target="_blank">(.*?)</a></span>')
# 小说总字数
findAllWords = re.compile(r'<span class="l5">(.*?)</span>')
# 小说总推荐
findRecommend = re.compile(r'<span class="l6">(.*?)</span>')
# 小说更新日期
findUpdate = re.compile(r'<span class="l7">(.*?)</span>')


# 爬取一页排行榜数据

def getFictionRankingListData(mainURL, a):
    fictionRankingList = []

    mainURL = mainURL + str(a) + ".html"
    html = analysisURL(mainURL)
    # 3.逐一解析数据
    soup = BeautifulSoup(html, "html.parser")
    item = soup.find_all('div', id="articlelist")
    item = str(item)
    # print(item)

    # 小说类别
    classes = re.findall(findClasses, item)
    # 小说链接
    fictionLink = re.findall(findFictionLink, item)
    # 小说名字
    name = re.findall(findName, item)
    # 小说作者
    author = re.findall(findAuthor, item)
    # 小说最新章节
    section = re.findall(findSection, item)
    # 小说总字数
    allWords = re.findall(findAllWords, item)
    # 小说总推荐
    recommend = re.findall(findRecommend, item)
    # 小说更新日期
    update = re.findall(findUpdate, item)

    for i in range(0, 40):
        data = []
        allClasses = classes[i + 1]
        fictionLinks = fictionLink[i]
        names = name[i]
        authores = author[i + 1]
        sectiones = section[i]
        allWordses = allWords[i + 1]
        recommendes = recommend[i + 1]
        updates = update[i + 1]
        data.append(allClasses)
        data.append(fictionLinks)
        data.append(names)
        data.append(authores)
        data.append(sectiones)
        data.append(allWordses)
        data.append(recommendes)
        data.append(updates)
        fictionRankingList.append(data)

    # 打印测试
    # for item in fictionRankingList:
    #     print(item)

    return fictionRankingList


# 爬取所有排行榜数据
def allRankingListData(mainURL):
    html = analysisURL(mainURL)
    fictionRankingList = []

    soup = BeautifulSoup(html, "html.parser")
    last = str(soup.find_all(class_="last"))
    last = re.findall(findLength, last)
    last = int(last[0])
    for i in range(0, 50):      # 只进项前50页信息进行爬取，将50改为last将会对全站的书本排行信息进行爬取
        fictionRankingList += getFictionRankingListData(mainURL, i+1)
        print("\r爬取进度{:.2f}%".format((i / 10) * 100), end="")

    saveFictionData(fictionRankingList)


# 小说主页爬取规则

# 章节链接
findLink = re.compile(r'<a href="(.*?)">.*?</a>')
# 章节名字
findSectionName = re.compile(r'<a href=".*?">(.*?)</a>')


# 2.爬取小说网页

def getFictionData(fictionURL):
    fictionDataList = []

    html = analysisURL(fictionURL)

    # 3.逐一解析数据
    soup = BeautifulSoup(html, "html.parser")

    item = soup.find_all('div', class_="zjbox")
    # print(item)

    item = str(item)

    # 章节链接
    link = re.findall(findLink, item)
    # 章节名字
    sectionName = re.findall(findSectionName, item)

    for i in range(0, len(link)):
        data = []
        links = fictionURL + link[i]
        sectionNames = sectionName[i]
        data.append(links)
        data.append(sectionNames)
        fictionDataList.append(data)

    # # 打印测试
    # for item in fictionDataList:
    #     print(item)

    return fictionDataList


# 小说名字读取

def findFictionName(fictionURL):
    html = analysisURL(fictionURL)
    soup = BeautifulSoup(html, "html.parser")
    # 小说名字读取
    fictionName = soup.find_all(id="info")
    fictionName = str(fictionName)
    fictionName = re.findall(findName, fictionName)
    # print(fictionName)
    return fictionName


# 1.得到指定一个URL的网页内容

def analysisURL(fictionURL):
    head = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    }

    requestfiction = urllib.request.Request(fictionURL, headers=head)

    html = ""
    # response = urllib.request.urlopen(requestfiction)
    # html = response.read()
    # print(html)
    # buff = BytesIO(html)
    # f = gzip.GzipFile(fileobj=buff)
    # html = f.read().decode('gbk')
    # print(html)

    try:
        response = urllib.request.urlopen(requestfiction)
        html = response.read()
        buff = BytesIO(html)
        f = gzip.GzipFile(fileobj=buff)
        html = f.read().decode('utf-8')

    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
        print("time out!")
    # print(html)

    return html


# 保存小说排行榜数据到Excel
def saveFictionData(fictionRankingList):
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)  # 创建workbook对象
    sheet = book.add_sheet('排行榜', cell_overwrite_ok=True)  # 创建工作表
    col = ("类别", "书本链接", "书名", "作者", "最新章节", "总字数", "总推荐", "更新日期")
    for i in range(0, 8):
        sheet.write(0, i, col[i])  # 写入列名

    for i in range(0, len(fictionRankingList)):
        data = fictionRankingList[i]
        for j in range(0, 8):
            sheet.write(i + 1, j, data[j])  # 写入章节数据

    book.save("排行榜.xls")  # 保存
    print("存储成功")


# 保存章节数据到Excel

def saveData(fictionDataList, saveName):
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)  # 创建workbook对象
    sheet = book.add_sheet('目录', cell_overwrite_ok=True)  # 创建工作表
    col = ("章节链接", "章节目录")
    for i in range(0, 2):
        sheet.write(0, i, col[i])  # 写入列名

    for i in range(0, len(fictionDataList)):
        data = fictionDataList[i]
        for j in range(0, 2):
            sheet.write(i + 1, j, data[j])  # 写入章节数据

    book.save(saveName)  # 保存


# 获取章节内容

def sectionOfContent(fictionDataList, fictionURL, fictionName):
    for i in range(0, len(fictionDataList)):
        # 一个章节的内容
        html = analysisURL(fictionDataList[i][0])
        soup = BeautifulSoup(html, "html.parser")
        content = soup.find_all('div', id="content")

        # 5.保存章节内容
        content = str(content)
        # 去掉标签
        content = re.sub(r'<br>', "\n", content)
        content = re.sub(r'<br/>', "\n", content)
        content = re.sub(r'</br>', "\n", content)
        content = re.sub(r'</div>', "", content)
        content = re.sub(r'<div id="content">', "", content)
        fictionName = re.sub('\[\'', "", fictionName)
        fictionName = re.sub('\']', "", fictionName)
        fictionName = fictionName.strip()  # 去掉前后空格
        content = re.sub(r'笔趣阁 www.bbiquge.net，最快更新<a href="' + fictionURL + '">' + fictionName + '</a>最新章节！',
                         "", content)
        content = re.sub('\[', "", content)
        content = re.sub(']', "", content)
        # print(content)

        # 6.写入文档
        txt_create(fictionName, fictionDataList[i][1])
        txt_create(fictionName, content)

        print("\r爬取进度{:.2f}%".format((i + 1) / len(fictionDataList) * 100), end="")


# 创建一个txt文件
def txt_create(name, msg):
    # 自动获取桌面路径
    desktop_path = os.path.join(os.path.expanduser('~'), "Desktop/")
    full_path = desktop_path + name + '.txt'  # 创建一个文档
    file = open(full_path, 'a', encoding='utf-8')
    file.write(msg)
    file.close()


if __name__ == "__main__":
    main()
    # txt_create("text", "Hello World")

    print("\n爬取完毕！")
