from bs4 import BeautifulSoup as bs
import requests
import json

def get_base_url():
	try:
		url = None
		with open('Config.json') as fr:
			file_data = json.loads(fr.read())

		url = file_data['base_url']
		return url
	except Exception as e:
		raise e


def create_search_string_url(base_url, search_str):
	try:
		return '{url}/search?q={search_string}'.format(url=base_url, search_string=search_str)
	except Exception as e:
		raise e

def create_complete_url(base_url, link):
	try:
		return '{}{}'.format(base_url, link)
	except Exception as e:
		raise e	

def get_raw_html_as_text(url):
	try:
		raw_html = requests.get(url)
		return raw_html.text
	except Exception as e:
		raise e	


def get_inner_html_by_class_attr(obj_bs, tag_name, cls_attr_data):
	try:
		attrs = {'class': cls_attr_data}
		
		inner_html = obj_bs.find(tag_name, attrs=attrs)
		return inner_html
	except Exception as e:
		print(e)
		raise e

def get_multiple_inner_html_by_class(obj_bs, tag_name, cls_attr_data):
	try:
		attrs = {'class': cls_attr_data}
		ls_inner_html = obj_bs.find_all(tag_name, attrs=attrs)
		return ls_inner_html
	except Exception as e:
		raise e	


def create_reviews_page_links(base_url, page_uri, page_count):
	try:
		ls_temp = []
		for i in range(1, int(page_count)+1):
			ls_temp.append('{}{}&page={}'.format(base_url, page_uri, i))

		return ls_temp
	except Exception as e:
		raise e


def fetch_rating(obj_bs):
	try:
		return obj_bs.div.div.div.div.text
	except Exception as e:
		raise e	
