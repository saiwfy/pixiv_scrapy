# -*- coding: utf-8 -*-
import scrapy
import codecs
import sys
import urllib2
import os

reload(sys) 
sys.setdefaultencoding('utf-8')

class ToshiSpider(scrapy.Spider):
	name = 'toshi'
	allowed_domains = ['pixiv.net']
	start_urls = ['https://www.pixiv.net/member_illust.php?id=20787']


	def __init__(self):
		self.headers = {
			"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"Accept-Encoding":"gzip, deflate, sdch, br",
			"Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4",
			"Cache-Control":"no-cache",
			"Connection":"keep-alive",
			"Host":"www.pixiv.net",
			"Pragma":"no-cache",
			"Referer":"https://www.pixiv.net/member.php?id=637016",
			"Upgrade-Insecure-Requests":"1",
			"User-Agent":"Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
		}
		self.cookies = {
			'p_ab_id':r'6',
			'p_ab_id_2':r'5',
			'login_ever':r'yes',
			'is_sensei_service_user':r'1',
			'module_orders_mypage':r'%5B%7B%22name%22%3A%22recommended_illusts%22%2C%22visible%22%3Afalse%7D%2C%7B%22name%22%3A%22everyone_new_illusts%22%2C%22visible%22%3Afalse%7D%2C%7B%22name%22%3A%22following_new_illusts%22%2C%22visible%22%3Afalse%7D%2C%7B%22name%22%3A%22mypixiv_new_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22fanbox%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22featured_tags%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22contests%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22sensei_courses%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22spotlight%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22booth_follow_items%22%2C%22visible%22%3Atrue%7D%5D',
			'stacc_mode':r'unify',
			'_ga':r'GA1.2.853190753.1497579996',
			'_gid':r'GA1.2.1297729081.1500610016',
			'PHPSESSID':r'1803671_6ee4fdb8be6fcb03dfb0fd064090b9cb',
			'__utmt':r'1',
			'__utma':r'235335808.853190753.1497579996.1500609696.1500618711.8',
			'__utmb':r'235335808.12.10.1500618711',
			'__utmc':r'235335808',
			'__utmz':r'235335808.1499149462.5.5.utmcsr=bbs.ngacn.cc|utmccn=(referral)|utmcmd=referral|utmcct=/read.php',
			'__utmv':r'235335808.|2=login%20ever=yes=1^3=plan=normal=1^5=gender=male=1^6=user_id=1803671=1^9=p_ab_id=6=1^10=p_ab_id_2=5=1^11=lang=zh_tw=1'
		}

	def start_requests(self):

		# for url in self.start_urls:
		# 	yield scrapy.Request(url=url,  meta={'cookiejar': self.cookies},callback=self.parse)
		for i, url in enumerate(self.start_urls):
			yield scrapy.Request(url, meta = {'cookiejar': i},
				headers = self.headers,
				cookies = self.cookies,
				callback = self.parse)

	def parse(self, response):
		for sel in response.css('#wrapper > div.layout-a > div.layout-column-2 > div > div:nth-child(8) > ul > li'):
			detail_url = sel.css('a::attr(href)')[0].extract()
			if detail_url is not None:
				yield scrapy.Request(response.urljoin(detail_url),meta={'cookiejar': response.meta['cookiejar']},callback=self.parse_detail)
				#测试单张图
				#yield scrapy.Request('https://www.pixiv.net/member_illust.php?mode=medium&illust_id=61384715',meta={'cookiejar': response.meta['cookiejar']},callback=self.parse_detail)
		#翻页
		nextpage = response.css('#wrapper > div.layout-a > div.layout-column-2 > div > ul:nth-child(6) > div > span.next > a::attr(href)').extract_first()
		if nextpage is not None:
			yield response.follow(nextpage,meta={'cookiejar': response.meta['cookiejar']},callback=self.parse)


	def parse_detail(self,response):
		#title和文件夹名字
		foldername = response.css('#wrapper > div.layout-a > div.layout-column-2 > div > section.work-info > h1::text')[0].extract()

		if response.body.find('查看更多') > 0:
			#多张图的情况
			medium_link = response.css('#wrapper > div.layout-a > div.layout-column-2 > div > div.works_display > a._work.manga.multiple::attr(href)').extract_first()
			if medium_link is not None:
				yield response.follow(medium_link,meta={'cookiejar': response.meta['cookiejar'],'foldername':foldername},callback=self.parse_manga)
				#print original_img
		else:
			#单张图的情况
			original_img = response.css('.original-image::attr(data-src)').extract_first()
			self.download_img(original_img,foldername)

		# fp = codecs.open('2.html','w','utf-8')
		# fp.write(response.body)
		# fp.close()

	def parse_manga(self,response):
		for sel in response.css('#main > section > div'):
			manga_big_link = sel.css('a::attr(href)').extract_first()
			if manga_big_link is not None:
				yield response.follow(manga_big_link,meta={'cookiejar': response.meta['cookiejar'],'foldername':response.meta['foldername']},callback=self.parse_manga_big)

	def parse_manga_big(self,response):
		original_url = response.css('body > img::attr(src)').extract_first()
		self.download_img(original_url,response.meta['foldername'])
		# return {
		# 	"original_url":response.css('body > img::attr(src)').extract_first()
		# }

	def download_img(self,imgsrc,foldername):
#https://i.pximg.net/img-original/img/2017/02/11/00/09/24/61384715_p0.jpg
		download_header = {
			# ":authority":"i.pximg.net",
			# ":method":"GET",
			# ":path":"/img-original/img/2017/02/11/00/09/24/61384715_p0.jpg",
			# ":scheme":"https",
			"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
			"accept-encoding":"gzip, deflate, sdch, br",
			"accept-language":"zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4",
			"cache-control":"no-cache",
			"pragma":"no-cache",
			"referer":"https://www.pixiv.net/",
			"upgrade-insecure-requests":"1",
			"user-agent":"Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
		}
		filename = imgsrc.split("/img/")[1].replace("/","")
		foldername = foldername.replace('/','')
		if os.path.exists(foldername):
			pass
		else:
			os.mkdir(foldername)
			
		if os.path.exists(foldername+"/"+filename):
			pass
		else:
			f = open(foldername+"/"+filename,'wb') #创建文件对象准备写入，还可以更精简
			src_req = urllib2.Request(imgsrc,headers = download_header) #创建request对象
			f.write(urllib2.urlopen(src_req).read()) #用Request对象返回数据作为对象写入文件
			f.close()