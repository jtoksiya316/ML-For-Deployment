import requests
from bs4 import BeautifulSoup as bs
import json
import os



class GoogleImageScrapper():
	""" Image scrapper class for Google Image Search """

	def __init__(self, image_name, file_type='jpg', num_of_downloads=5):
		self.url = 'https://www.google.com/search?q={}&source=lnms&tbm=isch'.format(image_name)
		self.file_type = file_type
		self.num_of_downloads = num_of_downloads
		self.headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
		self.image_dwnl_folder = './static'


	# def get_search_url(self):
	# 	try:
	# 		return self.url
	# 	except Exception as e:   
	# 		raise e

	def get_base_info(self):
		print('Following are the settings configured: ')
		print('Search URL:                       ', self.url)
		print('File type:                        ', self.file_type)
		print('Number of files to be downloaded: ', self.num_of_downloads)
		print('Download Folder(relative path):   ', self.image_dwnl_folder)


	def get_file_type(self):
		return self.file_type

	def get_download_folder(self):
		return self.image_dwnl_folder

	
	def get_raw_html(self):
		""" This method return raw html """

		try:
			response = requests.get(self.url, headers=self.headers)
			if response.status_code == 200:
				soup = bs(response.text, 'html.parser')
				return soup
			return None
		except Exception as e:
			raise e


	def get_images_links_of_one_type(self, soup):
		"""  This method scraps all images links based on file type 
			whether 'jpg', 'png', etc. """

		try:
			ls_div_data = soup.find_all('div', {'class': 'rg_meta'})
			ls_image_links = []
			for div_data in ls_div_data:
				link, ext = json.loads(div_data.text)['ou'], json.loads(div_data.text)['ity']
				if ext == self.file_type:
					ls_image_links.append(link)

			return ls_image_links
		except Exception as e:
			raise e


	def get_images_links_of_all_types(self, soup):
		"""  This method scraps all images links of all file types """

		try:
			ls_div_data = soup.find_all('div', {'class': 'rg_meta'})
			dict_images = {}
			ls_temp = []
			dict_temp = {}
			for div_data in ls_div_data:
				link, ext = json.loads(div_data.text)['ou'], json.loads(div_data.text)['ity']
				dict_temp.update({'link': link, 'file_type': ext})
				ls_temp.append(dict_temp)

			dict_images.update({"images_links": ls_temp})				
			return dict_images
		except Exception as e:
			raise e


	def delete_existing_files(self):
		""" This method deletes existing image files to reduce the space issues 
			locally as well as on cloud """

		try:
			ls_files = os.listdir(self.image_dwnl_folder)
			for each_file in ls_files:
				if each_file.split('.')[1] == self.file_type:
					os.remove(os.path.join(self.image_dwnl_folder, each_file))
					print('"{}" file removed successfully'.format(each_file))
		except Exception as e:
			raise e


	def download_images(self, ls_images, search_image):
		""" This method downloads every file type's file """

		try:
			img_count = 1
			for image_link in ls_images:
				print('='*50)
				print('IMAGE LINK: ', image_link)
				if img_count > self.num_of_downloads:
					print('\nNumber of file downloads exceeded {}'.format(self.num_of_downloads))
					break
				
				try:
					resp = requests.get(image_link)
					if resp.status_code == 200:
						
						image_name = '{}_{}.{}'.format(search_image, img_count, self.file_type)
						print('\nImage Name: {}'.format(image_name))
						with open(os.path.join(self.image_dwnl_folder, image_name), 'wb') as fw:
							img_content = bytes(resp.content)
							fw.write(img_content)
							print('\n Downloaded file {} as {} successfully'.format(image_link,image_name))
							img_count = img_count + 1

					else:
						print('\nERROR RESPONSE: ', resp.status_code)

				except Exception as e:
					print('Error in writing file: ',e)
					print(e.text)

		except Exception as e:
			raise e


	

