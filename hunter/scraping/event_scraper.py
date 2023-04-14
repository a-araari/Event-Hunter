import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlparse

from hunter.scraping.website_categories import *


class EventScraper():
	"""
	A web scraper for retrieving event data from a school website.
	"""
	def __init__(self, url):
		"""
		Initializes the scraper with the URL of the website to scrape.
		"""
		parsed_url = urlparse(url)
		self.url = url.rstrip('/') + '/'
		self.base_url = parsed_url.scheme + '://' + parsed_url.netloc + '/'

	def get_page_content(self, use_selenium):
		"""
		Fetches the HTML content of the page to scrape using Selenium.
		"""
		if use_selenium:
			options = webdriver.ChromeOptions()
			options.add_argument('headless')
			driver = webdriver.Chrome(options=options)
			driver.get(self.url)
			time.sleep(5)  # Wait for the page to load completely
			page_content = driver.page_source
			driver.quit()
		else:
			page_content = requests.get(self.url).content

		return page_content

	def get_title(self, soup):
		title = None
		if self.base_url in category_1:
			title = getattr(soup.find(class_='em-header-card_title'), 'text', '').strip()
		elif self.base_url in category_2:
			title = getattr(soup.find('h1', class_='summary'), 'text', '').strip()

		return title

	def get_image(self, soup):
		image = None
		if self.base_url in category_1:
			image_element = soup.find(class_='img_card')
			if image_element:
				image = image_element.get('src', None)
		if self.base_url in category_2:
			image_element = soup.find('div', class_='box_image')
			if image_element:
				image = image_element.a.img.get('src', None)

		return image or 'https://upload.wikimedia.org/wikipedia/commons/d/d1/Image_not_available.png'

	def get_description(self, soup):
		description = None
		if self.base_url in category_1:
			description = getattr(soup.find(class_='em-about_description'), 'text', '').strip()

		return description

	def get_date(self, soup):
		date = None
		if self.base_url in category_1:
			date = getattr(soup.find(class_='em-date'), 'text', '').strip()
		elif self.base_url in category_2:
			date = getattr(soup.find(class_='dateright'), 'text', '').strip()
		elif self.base_url in category_3:
			date_ele = soup.find(class_='su-info-group__text')
			if date_ele:
				date = getattr(date_ele.p, 'text', '').strip()

		return date

	def get_price(self, soup):
		price = None
		if self.base_url in category_1:
			price = getattr(soup.find(class_='em-price-tag'), 'text', '').strip()

		return price

	def get_location_text(self, soup):
		location = None
		if self.base_url in category_1:
			location = getattr(soup.find(class_='em-about_location__address'), 'text', '').strip()
		if self.base_url in category_2:
			location_elm = soup.find(class_='location')
			if location_elm:
				location = getattr(location_elm.span, 'text', '').strip()

		return location

	def get_location_coordinates(self, soup):
		longitude, latitude = None, None

		# Extract longitude and latitude values from Google Maps iframe
		iframe = soup.find('iframe', {'id': 'map'})
		if iframe:
			src = iframe.get('src', '')
			if 'center=' in src:
				center = src.split('center=')[1].split('&')[0]
				latitude, longitude = center.split('%2C')

		return longitude, latitude

	def extract_event_details(self, page_content):
		"""
		Extracts events from HTML page
		"""
		soup = BeautifulSoup(page_content, 'html.parser')

		image = self.get_image(soup)
		title = self.get_title(soup)
		description = self.get_description(soup)
		date = self.get_date(soup)
		price = self.get_price(soup)
		location = self.get_location_text(soup)
		longitude, latitude = self.get_location_coordinates(soup)

		event = {
			'title': title,
			'description': description,
			'image': image,
			'date': date,
			'price': price,
			'location': location,
			'latitude': latitude,
			'longitude': longitude
		}
		return event

	def get_event(self, use_selenium=False):
		"""
		Scrapes event data from the website and returns a list of event objects.
		"""
		page_content = self.get_page_content(use_selenium)
		event = self.extract_event_details(page_content)

		return event
