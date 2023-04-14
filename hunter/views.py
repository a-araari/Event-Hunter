from django.shortcuts import render

from hunter.scraping.event_spider import EventSpider
from hunter.scraping.event_scraper import EventScraper
from hunter.scraping.website_categories import *


async def index(request):
	context = {}
	url = request.GET.get('url')
	page = request.GET.get('page')
	if url:
		spider = EventSpider(url)
		events = await spider.get_events(None if page == 'all' else page)
		context['events'] = events
		context['url'] = url
		context['page'] = page

	return render(request, 'hunter/index.html', context=context)


def event(request):
	context = {}
	url = request.GET.get('url')
	if url:
		scraper = EventScraper(url)
		event =  scraper.get_event()
		context['event'] = event
		context['url'] = url

	return render(request, 'hunter/event.html', context=context)


def supported_websites(request):
	websites = category_1 + category_2 + category_3
	context = {
		'websites': websites
	}

	return render(request, 'hunter/supported.html', context=context)
