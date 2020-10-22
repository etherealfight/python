import requests
from flask_cors import CORS
import random
import jieba.analyse
import jieba
from bs4 import BeautifulSoup
from lxml import etree
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.route('/', methods=['GET'])
def getPic():
    url = "https://www.liepin.com/zhaopin"
    user_Agent = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
        'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
        'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)']
    ua = random.choice(user_Agent)
    headers = {
        'User-Agent': ua
    }

    name = request.args.get('keyword')
    cityId = request.args.get('dps')
    print(name)
    print(cityId)

    hrefList = []
    # 爬取相应职位链接
    try:
        for j in range(1):
            param = {
                'key': name,
                'dqs': cityId,
                'curPage': j
            }
            page = requests.get(url=url, params=param, headers=headers)
            print("当前爬取的是：%s %s" % (url, param))
            soup = BeautifulSoup(page.text, "html.parser")
            soup = soup.find_all("h3")
            for i in soup:
                if i.has_attr("title"):
                    href = i.find_all("a")[0]["href"]
                    if href.startswith('h'):
                        hrefList.append(href)
                        print(href)
        # 保存职位链接到文件中
        print(len(hrefList))
        with open('./href.txt', 'w', encoding='utf-8') as fp:
            fp.write(str(hrefList))
    except(ValueError, ArithmeticError):
        print("爬取链接失败")

        # 爬取职业详情要求
        try:
            texts = ''
            for item in hrefList:
                response = requests.get(url=item, headers=headers)
                tree = etree.HTML(response.text)
                data = tree.xpath(
                    '//div[@class="job-item main-message job-description"]/div[@class="content content-word"]/text()')
                # print(data)
                for i in data:
                    print(str(i))
                    texts = texts + str(i) + '\n'
            with open('./job_detail.txt', 'w', encoding='utf-8') as fp:
                fp.write(texts)
        except(ValueError, ArithmeticError):
            print("爬取职业详情要求失败")
        # 数据清洗分词
    try:
        stopwordList = [line.strip() for line in open('./stopWords_Case.txt', encoding='UTF-8').readlines()]
        wordList = jieba.cut(str(texts), cut_all=False)
        print(wordList)
        cutedtext = ''
        for word in wordList:
            if word not in stopwordList:
                if word != '\t' and word != '\n' and word != ' ':
                    cutedtext += word
                    cutedtext += " "
        print(cutedtext)
    except(ValueError, ArithmeticError):
        print("数据清洗分词失败")
        # 关键词提取
    try:
        keywords = jieba.analyse.extract_tags(cutedtext, topK=40, withWeight=False, allowPOS=())
        print(str(keywords))
        with open('./text.txt', 'w', encoding='utf-8') as fp:
            fp.write(str(cutedtext))
    except(ValueError, ArithmeticError):
        print("关键词提取失败")
        # 词云生成
    try:
        mytext = ''
        with open('./text.txt', 'r', encoding='utf-8') as f:
            mytext = f.read()
        wordcloud = WordCloud(background_color="white", max_font_size=40, font_path='./cjkFonts 手寫4.ttf')
        wordcloud.generate(mytext)
        plt.figure()
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()
        wordcloud.to_file('wordcloud.jpg')
        return jsonify({
            'url': 'wordcloud.jpg'
        })
    except(ValueError, ArithmeticError):
        print("词云生成失败")


if __name__ == '__main__':
    app.run(debug=True)
