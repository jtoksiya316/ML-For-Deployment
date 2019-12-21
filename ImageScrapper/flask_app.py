import sys
import os
from flask_cors import CORS,cross_origin
from flask import Flask, render_template, request,jsonify

from utils import GoogleImageScrapper

# Creating an instance of Flask app as "app"
app = Flask(__name__)


@app.route('/')
@cross_origin()
def home():
	""" This method routes to index.html view once we route to our base url"""
	return render_template('index.html')


@app.route('/showImages')
@cross_origin()
def show_images(search_str, file_type, img_folder):
	try:
		# Fetching downloaded files from static folder
		ls_img_files = os.listdir(img_folder)
		ls_context = []
		for img_file in ls_img_files:
			if img_file.split('.')[1] == file_type:
				ls_context.append(img_file)

		try:
			if(len(ls_context)>0): # if there are images present, show them on a wen UI
				return render_template('showImage.html',user_images = ls_context)
			else:
				return "Please try with a different string" # show this error message if no images are present in the static folder
		except Exception as e:
			print('no Images found ', e)
			return "Please try with a different string"

	except Exception as e:
		print('show_images() Exception: {}'.format(e))


@app.route('/searchImages', methods=['GET','POST'])
def searchImages():
	search_str = None
	try:
		if request.method == 'POST':
			print("Within searchImages -> POST")
			search_str = request.form['search_str'] # assigning the value of the input keyword to the variable keyword
		else:
			print("Please enter Image Name to be searched!!!")
		print('Image Name: ', search_str)

		# My CODE
		ls_img_links = []
		obj_scrapper = GoogleImageScrapper(search_str) #, file_type='jpg', num_of_downloads=5)
		print('STEP 1: Configuration Info ')
		print('#'*40)
		obj_scrapper.get_base_info()

		print('\nSTEP 2: Getting Page Source as Raw HTML')
		print('#'*40)
		raw_html_output = obj_scrapper.get_raw_html()
		if raw_html_output != None:
			print('\nSTEP 3: Collecting Images Links as per File Type')
			print('#'*40)
			ls_img_links = obj_scrapper.get_images_links_of_one_type(raw_html_output)

			# Delete existing file_type images from static folder
			print('\nSTEP 4: Deleting existing "file type" image files from static folder')
			print('#'*40)
			obj_scrapper.delete_existing_files()

			# Downloading each file based on num_of_downloads param
			print('\nSTEP 5: Downloading Images and storing it in static folder')
			print('#'*40)
			obj_scrapper.download_images(ls_img_links, search_str)
			print('Completed with task!!!')

			# fetching file type
			f_type = obj_scrapper.get_file_type()
			dwnld_folder = obj_scrapper.get_download_folder()
			return show_images(search_str, f_type, dwnld_folder)
		else:
			print('Not able to get raw html from URL: {}'.format(url))
	except Exception as e:
		print('searchImages() Exception: {}'.format(e))


if __name__ == '__main__':
	app.run(debug=True)

