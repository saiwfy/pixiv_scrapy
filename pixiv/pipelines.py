# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline

from scrapy.exceptions import DropItem

from scrapy.http import Request
headers = {
"User-Agent":'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
"Referer":"https://www.pixiv.net", #加入referer 为下载的域名网站

}

# class PixivPipeline(object):
#     def process_item(self, item, spider):
#         return item
class PixivPipeline(ImagesPipeline):

	def get_media_requests(self, item, info):
		for image_url in item['image_urls']:
			yield Request(image_url,headers = headers)

	def item_completed(self, results, item, info):
		image_paths = [x['path'] for ok, x in results if ok]
		if not image_paths:
			raise DropItem("Item contains no images")
			item['image_paths'] = image_paths
			return item