import requests
import codecs
from urllib.parse import urljoin
from lxml import etree
from modules import useragent


# 地址管理器
class Urls(object):

    def __init__(self):
        '''
        newUrls集合保存未爬取的url
        oldUrls集合保存已爬取的url
        '''
        self.newUrls = set()
        self.oldUrls = set()

    def getNewUrl(self):
        '''
        从未爬取newUrls集合中拿到一个url，并将其放入到已爬取数组
        :return:
        '''
        url = self.newUrls.pop()
        self.oldUrls.add(url)
        return url

    def addNewUrl(self, url):
        '''
        向未爬取newUrls集合中添加一项url
        :param url:
        :return:
        '''
        if url not in self.newUrls and url not in self.oldUrls:
            self.newUrls.add(url)

    def addNewUrls(self, urls):
        '''
        向未爬取newUrls集合中添加多项url
        :param urls:
        :return:
        '''
        for url in urls:
            self.addNewUrl(url)

    def getNewUrlsLength(self):
        '''
        获取未爬取newUrls集合大小
        :return:
        '''
        return len(self.newUrls)


# 页面下载
class Download(object):

    def __init__(self):
        pass

    def download(self, url):
        '''
        下载指定url页面
        :param url:
        :return:
        '''
        user_agent = useragent.getUserAgent()
        # print("user_agent: {}".format(user_agent))
        headers = {
            'User-Agent': user_agent
        }
        s = requests.session()
        r = s.request(method='get', url=url, headers=headers)
        if r.status_code == 200:
            print('\n\n正在抓取地址:%s' % url)
            print('User-Agent:', r.request.headers.get('user-agent'))
            return r.content
        return None


# 页面解析
class Parser(object):

    def __init(self):
        pass

    def parserHTML(self, url, content):
        '''
        用lxml中的etree解析通过requests返回的内容
        :param url:
        :param content:
        :return:
        '''
        html = etree.HTML(content)
        datas = self.getDatas(url, html)
        urls = self.getUrls(url, html)
        print("datas: {}".format(datas))
        print("urls: {}".format(urls))
        return urls, datas

    def getDatas(self, url, html):
        '''
        解析需要爬取的内容
        :param url:
        :param html:
        :return:
        '''
        datas = []
        # item = html.xpath("//div[contains(@class, 'container')]//h3//a[@class='post-title-link']")
        item = html.xpath('//div[@class="container"]//div[@class="post-list"]//article/a[1]')
        # xpath返回的列表，用索引方式取出来，子节点和该节点属性
        for key in item:
            href = key.get('href')  # 取节点属性
            title = key.xpath('./h2/text()')[0]  # 取出来，子节点
            # print(key)
            # print("博客标题: {},博客连接: {}".format(title, href))
            datas.append({
                # 'title': key.text,
                'title': title,  # 获取title
                'url': urljoin(url, href)  # 做url拼接
            })
        return datas

    def getUrls(self, url, html):
        '''
        解析需要继续爬取的urls
        :param url:
        :param html:
        :return:
        '''
        # return [urljoin(url, key) for key in html.xpath("//nav[@id='page-nav']//a[contains(@class, 'page-number')]//@href")]
        return [urljoin(url, key) for key in
                html.xpath("//nav[contains(@class,'page-nav')]/a[contains(@class,'extend next')]/@href")]


# 导出数据到html
class Output(object):

    def __init__(self):
        '''
        定义需要爬取的内容的数组
        '''
        self.datas = []

    def storeDatas(self, datas):
        '''
        将爬取的datas数据存放到self.datas中
        :param datas:
        :return:
        '''
        for key in datas:
            self.datas.append(key)

    def outputHTML(self):
        '''
        将爬取的数据导出到html
        :return:
        '''
        with codecs.open('data.html', 'w', 'utf-8') as file:
            file.write('<meta charset="utf-8"/>')
            for key in self.datas:
                file.write('<p><a target="_blank" href="%s">%s</a>,%s</p>\n' % (key['url'], key['title'], key['url']))


# 调度器
class Scheduler(object):

    def __init__(self):
        '''
        初始化调度器
        '''
        self.urls = Urls()
        self.download = Download()
        self.parserHTML = Parser()
        self.output = Output()

    def crawler(self, root_url):
        '''
        根据入口文件，开始爬取需要的内容和urls
        :param root_url:
        :return:
        '''
        self.urls.addNewUrl(root_url)
        while self.urls.getNewUrlsLength() > 0:
            # try:
            url = self.urls.getNewUrl()
            content = self.download.download(url)
            urls, datas = self.parserHTML.parserHTML(url, content)
            self.urls.addNewUrls(urls)
            self.output.storeDatas(datas)
        # except Exception as e:
        #     print('crawler fail')
        #     print(e)
        self.output.outputHTML()


if __name__ == "__main__":
    # 实例化
    crawler = Scheduler()
    crawler.crawler('http://www.dongwm.com/')
