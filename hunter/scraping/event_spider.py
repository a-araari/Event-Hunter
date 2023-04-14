import asyncio
import requests
from lxml import html
from urllib.parse import urlparse


class EventSpider():
	"""
	A web scraper for retrieving event data from a school website.
	"""
	def __init__(self, url):
		"""
		Initializes the scraper with the URL of the website to scrape.
		"""
		# Ensure that the URL passed is the base url and
		# that it ends with a single slash character
		parsed_url = urlparse(url)
		self.url = url.rstrip('/') + '/'
		self.base_url = parsed_url.scheme + '://' + parsed_url.netloc + '/'

	async def get_page_content(self, url):
		"""
		Fetches the HTML content of the page to scrape
		"""
		print('scraping ' + url)
		response = await asyncio.get_event_loop().run_in_executor(None, requests.get, url)
		if response.status_code == 200:
			return response.content
		else:
			raise Exception('Failed to fetch page content')

	async def extract_events(self, page_content):
		"""
		Extracts events from HTML page
		"""
		tree = html.fromstring(page_content)
		events = set()

		all_events = tree.xpath('//a')

		for event in all_events:
			href = event.get('href')

			if not href or not href.startswith(self.base_url + 'event/'):
				continue
			if '/create' in href:
				continue
			if '/confirm?' in href:
				continue
			events.add(href)

		return events

	async def get_pages(self):
		pages = []
		page_content = await self.get_page_content(f'{self.base_url}/calendar/')
		tree = html.fromstring(page_content)
		a_tags = tree.xpath('//div[@class="em-search-pagination"]//a')

		total = 1
		if a_tags:
			for a in a_tags:
				try:
					count = int(a.text.strip())
					if count > total:
						total = count
				except ValueError:
					print(f"Warning: {a.text.strip()} is not a valid number.")

		for index in range(total):
			pages.append(f'{self.base_url}/calendar/{index}')

		return pages

	async def get_events(self, page):
		"""
		Scrapes event data from the website and returns a list of event objects.
		"""
		events = set()

		if page:
			page_content = await self.get_page_content(f'{self.base_url}/calendar/{page}')
			events.update(await self.extract_events(page_content))
		else:
			pages = await self.get_pages()
			for page_url in pages:
				page_content = await self.get_page_content(page_url)
				events.update(await self.extract_events(page_content))

		# return a sorted list of events based on the length of the links
		return sorted(events, key=lambda s: len(s))

	def run_spider(self):
		return asyncio.get_event_loop().run_until_complete(self.get_events())
