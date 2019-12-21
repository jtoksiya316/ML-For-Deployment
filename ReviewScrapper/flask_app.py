from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
import re

from bs4 import BeautifulSoup as bs
from lib import *


# Initialising the flask app with the name 'app'
app = Flask(__name__)


@app.route('/')
@cross_origin()
def home():
	try:
		return render_template('index.html')
	except Exception as e:
		print('Exception occured: {}'.format(e))


@app.route('/reviews', methods=['POST','GET'])
@cross_origin()
def index():
	dict_reviews = {}
	ls_reviews = []
	# main_dict = {'ReviewScrapper':[]}
	ls_divs = []
	try:
		if request.method == 'POST':
			print('POST METHOD')
			search_string = request.form['product_name']
			print('search String:{}'.format(search_string))

			BASE_URL = get_base_url()
			SEARCH_URL = create_search_string_url(BASE_URL, search_string)
			flipkart_html_text = get_raw_html_as_text(SEARCH_URL)
			obj_bs = bs(flipkart_html_text, 'html.parser')

			################################################
			# fetching href using div tag's class = 3O0U0u
			search_page_div_data = get_inner_html_by_class_attr(obj_bs, 'div', '_3O0U0u')
			info_href = search_page_div_data.div.div.a # Generic
			DETAILS_PAGE_URL = create_complete_url(BASE_URL, info_href['href'])

			#############################################
			# Finding all_reviews page link and creating a complete URL
			reviews_html = get_raw_html_as_text(DETAILS_PAGE_URL)
			obj_bs = bs(reviews_html, 'html.parser')
			all_reviews_div_data = get_inner_html_by_class_attr(obj_bs, 'div', '_39LH-M')
			if all_reviews_div_data == None:
				return render_template('results.html', reviews=ls_reviews)


			ALL_REVIEWS_PAGE_URL = None
			all_reviews_href_div = get_inner_html_by_class_attr(all_reviews_div_data, 'div', re.compile(r'^swINJg'))

			if all_reviews_href_div != None:
				if all_reviews_href_div.parent.name == 'a':
					ALL_REVIEWS_PAGE_URL = create_complete_url(BASE_URL, all_reviews_href_div.parent['href'])
			else:
				ALL_REVIEWS_PAGE_URL = None

			#############################################
			# Fetching the Reviews Page Count
			ls_reviews_page_links = []
			if ALL_REVIEWS_PAGE_URL != None:
				review_page_count_html = get_raw_html_as_text(ALL_REVIEWS_PAGE_URL)
				obj_bs = bs(review_page_count_html, 'html.parser')
				page_count_data = get_inner_html_by_class_attr(obj_bs, 'div', '_2zg3yZ _3KSYCY')

				if page_count_data == None:
					page_count_num = 1
				else:
					page_count_num = page_count_data.span.text.split(' ')[-1]

				# print(type(page_count_num))
				if page_count_num == 1:
					review_page_uri = ALL_REVIEWS_PAGE_URL
					ls_reviews_page_links = ['{}&page={}'.format(review_page_uri, page_count_num)]
				else:
					if int(page_count_num) > 5:
						page_count_num = 5
						nav_data = get_inner_html_by_class_attr(obj_bs, 'nav', '_1ypTlJ')
						link = get_inner_html_by_class_attr(nav_data, 'a', '_2Xp0TH')
						review_page_uri = link['href'].split('&')[0]
						ls_reviews_page_links = create_reviews_page_links(BASE_URL, review_page_uri, page_count_num)
			else:
				ls_reviews_page_links.append(DETAILS_PAGE_URL)

			#################################################
			# Collecting all the reviews from each page and putting into a dictionary
			for each_review_link in ls_reviews_page_links:
				review_page_html = get_raw_html_as_text(each_review_link)
				obj_bs = bs(review_page_html, 'html.parser')
				if ALL_REVIEWS_PAGE_URL != None:
					ls_divs = get_multiple_inner_html_by_class(obj_bs, 'div', '_1PBCrt')
				
					for div_data in ls_divs:
						div_data_level1 = div_data.find('div', attrs={'class': re.compile(r'^col _390CkK _1gY8H-')})
						ls_data = div_data_level1.children
						ls_rows = []
						for data in ls_data:
							if 'row' in data.attrs['class']:
								ls_rows.append(data)

						if len(ls_rows) == 3:
							# Fetch Rating:
							try:
								rating_data = fetch_rating(div_data)
							except:
								rating_data = 'No Rating'
							
							try:
								name = get_inner_html_by_class_attr(div_data_level1, 'p', '_3LYOAd _3sxSiS')
								customer_name = name.text
							except:
								customer_name = 'No Name'

							# Fetching the Comment heading
							try:
								data =  get_inner_html_by_class_attr(div_data_level1, 'p', '_2xg6Ul')
								comment_heading = data.text
							except:
								comment_heading = 'No Comment Heading'

							# Fetching Comments:
							try:
								data = get_inner_html_by_class_attr(div_data_level1, 'div', 'qwjRop')
								comments = data.div.div.text
							except:
								comments = 'No Comments'

						elif len(ls_rows) == 2:
							# Fetch Rating:
							try:
								data = div_data_level1.find('div', attrs={'class': re.compile(r'^hGSR34 E_uFuv')})
								rating_data = data.text
							except:
								rating_data = 'No Rating'

							# Fetching Customer Name
							try:
								name = get_inner_html_by_class_attr(div_data_level1, 'p', re.compile(r'^_3LYOAd _3sxSiS'))
								customer_name = name.text
							except:
								customer_name = 'No Name'

							# Fetching the Comment heading
							try:
								data =  get_inner_html_by_class_attr(div_data_level1, 'p', '_2xg6Ul')
								comment_heading = data.text
							except:
								comment_heading = 'No Comment Heading'

							# Fetching Comments:
							try:
								data = get_inner_html_by_class_attr(div_data_level1, 'div', '_2t8wE0')
								comments = data.text
							except:
								comments = 'No Comments'

						dict_reviews.update({'Product': search_string, 'Name': customer_name, 'Rating': rating_data, 'Comment Heading': comment_heading, 'Comments':comments})
						ls_reviews.append(dict_reviews)
						dict_reviews = {}
				else:
					ls_divs = get_multiple_inner_html_by_class(obj_bs, 'div', '_3nrCtb')
					for div_data in ls_divs:
						div_data_level1 = div_data.find('div', attrs={'class': re.compile(r'^col _390CkK')})
						ls_row_class_data = div_data_level1.find('div', attrs={'class': re.compile(r'^row')})

						# Fetch Rating:
						try:
							rating_data = fetch_rating(div_data)
						except:
							rating_data = 'No Rating'

						# Fetching Customer Name
						try:
							name = get_inner_html_by_class_attr(div_data_level1, 'p', '_3LYOAd _3sxSiS')
							customer_name = name.text
						except:
							customer_name = 'No Name'

						# Fetching the Comment heading
						try:
							data =  get_inner_html_by_class_attr(div_data_level1, 'p', '_2xg6Ul')
							comment_heading = data.text
						except:
							comment_heading = 'No Comment Heading'

						# Fetching Comments:
						try:
							data = get_inner_html_by_class_attr(div_data_level1, 'div', 'qwjRop')
							comments = data.div.div.text
						except:
							comments = 'No Comments'

						dict_reviews.update({'Product': search_string, 'Name': customer_name, 'Rating': rating_data, 'Comment Heading': comment_heading, 'Comments':comments})
						ls_reviews.append(dict_reviews)
						dict_reviews = {}		

			print('Total reviews: {}'.format(len(ls_reviews)))
			
			# Showing reviews to the user
			return render_template('results.html', reviews=ls_reviews)
	except Exception as e:
		print('Exception occured: {}'.format(e))



if __name__ == '__main__':
	app.run(debug=True)