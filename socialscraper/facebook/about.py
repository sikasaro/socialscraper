import logging, requests, lxml.html
from ..base import ScrapingError
from .models import *

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

ABOUT_URL = "https://www.facebook.com/%s/info"

import pdb

def get(browser, current_user, graph_name):

	# shit gets weird when graph_name == current_user.username
	if current_user.username == graph_name:
		raise ScrapingError("don't scrape yourself plz")

	ret = {
		"family": {},
		"experiences": {},
		"relationships": {},
		"places": {},
		"contact": {},
		"basic": {},
		"about": [],
		"quotes": [],
		"event": {}
	}

	def get_text(element_list):
		if element_list: return element_list[0].text_content()

	def get_previous(element_list):
		if element_list: return [element_list[0].getprevious()]

	def get_rows(data):
		for table in data.cssselect('tbody'): 
			for row in table.cssselect('tr'): 
				yield row

	def get_cells(data):
		for table in data.cssselect('tbody'): 
			for row in table.cssselect('tr'): 
				for cell in row.cssselect('td'):
					yield cell

	def parse_experience(cell):
		for experience in cell.cssselect(".experienceContent"):
			experience_title = get_text(experience.cssselect(".experienceTitle"))
			# experience_title_url = experience.cssselect(".experienceTitle")[0]
			experience_body = get_text(experience.cssselect(".experienceBody"))
			# pdb.set_trace()
			yield experience_title, experience_body

	def parse_generic_cell(cell):
		previous_cell = get_previous(cell.cssselect('.aboutSubtitle'))
		name_url = previous_cell[0].cssselect('a')[0].get('href') if previous_cell[0].cssselect('a') else None
		name = get_text(previous_cell)
		content = get_text(cell.cssselect('.aboutSubtitle'))
		return (name, name_url), content

	def parse_generic_row(row):
		name = get_text(row.cssselect('th'))
		content = get_text(row.cssselect('td'))
		return name, content

	response = browser.get(ABOUT_URL % graph_name)
	for element in lxml.html.fromstring(response.text).cssselect(".hidden_elem"): 
		comment = element.xpath("comment()")
		if not comment: continue
		
		element_from_comment = lxml.html.tostring(comment[0])[5:-4]
		doc = lxml.html.fromstring(element_from_comment)
		fbTimelineSection = doc.cssselect('.fbTimelineSection.fbTimelineCompactSection')
		fbTimelineFamilyGrid = doc.cssselect('.fbTimelineFamilyGrid')
		fbTimelineAboutMeHeader = doc.cssselect('.fbTimelineAboutMeHeader')

		# # this is for scraping a Page
		# if fbTimelineAboutMeHeader:
		# 	title = get_text(fbTimelineAboutMeHeader[0].cssselect('.uiHeaderTitle'))
		# 	print title

		# 	if "About" in title:
		# 		print doc.text_content() 
		# 	elif "Basic Info" in title:
		# 		print doc.text_content()

		if fbTimelineFamilyGrid:
			familyList = fbTimelineFamilyGrid[0].cssselect('.familyList')[0]
			for member in familyList:
				name, status = parse_generic_cell(member)
				ret['family'][status] = name

				# FacebookFamily(profile_id=, relationship=status, uid=, name=name)

		if fbTimelineSection:
			title = get_text(fbTimelineSection[0].cssselect('.uiHeaderTitle'))
			data = fbTimelineSection[0].cssselect('.profileInfoTable') if fbTimelineSection else None

			if not title or not data: continue
			
			# experiences
			if "Work and Education" in title:
				for row in get_rows(data[0]):
					if not row.cssselect('th'): continue
					header = row.cssselect('th')[0].text_content() 
					ret['experiences'][header] = {}
					for cell in row.cssselect('td'): 
						for experienceTitle, experienceBody in parse_experience(cell): 
							ret['experiences'][header][experienceTitle] = experienceBody

			# relationships
			elif "Relationship" in title:
				for cell in get_cells(data[0]): 
					name, status = parse_generic_cell(cell)
					ret['relationships'][status] = name

			# places
			elif "Places Lived" in title:
				for cell in get_cells(data[0]): 
					name, status = parse_generic_cell(cell)
					ret['places'][status] = name

			# contact
			elif "Contact Information" in title:
				for row in get_rows(data[0]): 
					name, status = parse_generic_row(row)
					ret['contact'][name] = status

			# basic
			elif "Basic Information" in title:
				for row in get_rows(data[0]): 
					name, status = parse_generic_row(row)
					ret['basic'][name] = status					

			# about
			elif "About" in title:
				data = fbTimelineSection[0].getchildren()[1]
				for quote in data.cssselect('.profileText'): 
					ret['about'].append(quote.text_content())

			# quotes
			elif "Favorite Quotations" in title:
				data = fbTimelineSection[0].getchildren()[1]
				for quote in data.cssselect('.profileText'):
					ret['quotes'].append(quote.text_content())
			# family
			elif "Family" in title: # empty
				pass # this will be empty Family information above in 'fbTimelineFamilyGrid'

			# events
			elif "Life Events" in title:
				# TODO: parse life events
				data = fbTimelineSection[0].getchildren()[1].text_content()
				pass
			else:
				raise ScrapingError("Unrecognized fbTimelineSection %s" % title)

	return ret
	