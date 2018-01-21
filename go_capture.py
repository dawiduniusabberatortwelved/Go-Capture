import argparse
import csv
import os
import sys
import time

try:
	from bs4 import BeautifulSoup
except ImportError:
	print("[-] Install bs4 (Beautiful Soup) to use this script")
	sys.exit(1)

try:
	from selenium import webdriver
	from selenium.webdriver.common.keys import Keys
except ImportError:
    print("[-] Install selenium and the Google Chrome Driver to use this script")
    sys.exit(2)
	
try:
	from tqdm import tqdm
except ImportError:
    print("[-] Install tqdm to use this script")
    sys.exit(3)
	

"""
    Google Activity Capture - Automatically capture Google's My Activity page.
    Copyright (C) 2018  Preston Miller
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


def main(user, pwd, cnt, output, seconds):
	login_url = "https://accounts.google.com/ServiceLogin?continue=https://myactivity.google.com/myactivity&amp;hl=en"
	driver = webdriver.Chrome()
	print("[+] Navigating to Google Login followed by the 'My Activity' page")
	driver.get(login_url)
	
	driver.find_element_by_id("identifierId").send_keys(user)
	driver.find_element_by_id("identifierNext").click()
	time.sleep(1.5)
	driver.find_element_by_name("password").send_keys(pwd)
	driver.find_element_by_id("passwordNext").click()
	
	input("[+] Manually handle any two-factor requirements. Press Enter when ready to continue...")
	scroll_activity(driver, cnt, output, seconds)

	
def scroll_activity(driver, cnt, output, seconds):
	driver.get("https://myactivity.google.com/item")
	driver.find_element_by_tag_name('body').click()
	
	print("[*] Pressing the END key {} times to scroll through the page".format(cnt))
	for i in tqdm(range(cnt)):
		driver.find_element_by_tag_name('body').send_keys(Keys.END)
		time.sleep(seconds)
		
	print("[+] Reading page source, this may take awhile...")
	html_source = driver.page_source
	soup = BeautifulSoup(html_source, 'html.parser')
	parse_data(soup, output)
			
			
def parse_data(html_soup, output):
	num_days = 0
	num_events = 0
	parsed_data = {}
	cards = html_soup.select("#main-content > div > div > hist-date-block")
	for day in cards:
		num_days += 1
		date = day.select("div")[0].text.split("\n\n\n\n\n")[1].strip()
		parsed_data[date] = []
	
		for card in day.select("div > div > div > md-card > hist-display-item > md-card-content"):
			num_events += 1
			tmp_dict = {}
			
			temp = [x.replace("\n", "").strip() for x in card.text.split('\n\n\n\n')]
			raw_string = " - ".join([" ".join(x.split()) for x in temp if x.strip() != "" and x.strip() != "Delete" and x.strip() != "Details"])
			service = card.find('div', attrs={'class': ['fp-display-item-title']}).text.replace("\n", "").strip()
			action = " ".join(card.find("h4", attrs={"class": ["fp-display-block-title t08"]}).text.replace("\n", "").strip().split())
			title = " ".join(card.find("div", attrs={'class': ['layout-column']}).find("span").text.replace("\n", "").strip().split())
			sub_title_elements = card.find_all("div", attrs={"ng-repeat": "subTitle in ::item.getSubTitleList()"})
			sub_title = " ".join([x.text.replace("\n", "").strip() for x in sub_title_elements])
			dt_time = card.find("div", attrs={"ng-if": "::!detailsItem", "class": ["fp-display-block-details"]}).text.replace("\n", "").split(u"\u2022")[0].strip()
			
			tmp_dict["Raw String"] = raw_string
			tmp_dict["Date"] = date
			
			if service != "":
				tmp_dict["Service"] = service
			if action.strip() != "":
				tmp_dict["Action"] = action
			if title.strip() != "":
				tmp_dict["Card Title"] = title
			if sub_title.strip() != "":
				tmp_dict["Card Subtitle"] = sub_title
			if dt_time.strip() != "":
				tmp_dict["Time"] = dt_time
			
			parsed_data[date].append(tmp_dict)
			
	print("[+] Processed {} days' worth of events from Google's MyActivity".format(num_days))
	print("[+] Processed {} events from Google's MyActivity".format(num_events))
			
			
	write_csv(parsed_data, output)

	
def write_csv(data, output):
	fieldnames = ["Date", "Time", "Service", "Action", "Card Title", "Card Subtitle", "Raw String"]
	print("[+] Writing processed data to {} CSV".format(output))
	with open(output, "w", newline="", encoding='utf-8') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
		writer.writeheader()
		for day in data:
			for event in data[day]:
				writer.writerow(event)

		
if __name__ == '__main__':
	# Command-line Argument Parser
	parser = argparse.ArgumentParser(description="Capture Google My Activity..")
	parser.add_argument("-u", "--username", type=str, help="Google account user: username@gmail.com", required=True)
	parser.add_argument("-p", "--password", type=str, help="Google account password", required=True)
	parser.add_argument("-c", "--count", type=int, help="Number of times to scroll to the end of the page" ,required=True)
	parser.add_argument("-o", "--output", help="Output CSV", required=True)
	parser.add_argument("-s", "--seconds", type=float, default=1, help="Number of seconds to wait before pressing END (default 1 second)")
	args = parser.parse_args()
	
	if not os.path.exists(os.path.dirname(args.output)) and os.path.dirname(args.output) != "":
		os.makedirs(os.path.dirname(args.output))
	
	if not args.username.endswith("@gmail.com"):
		print("[-] Poorly formatted username. Make sure you supply an appropriately formatted username. For example, username@gmail.com")
		sys.exit(3)
	
	if not sys.version_info >= (3,0):
		print("[-] Must use Python 3.X, this script was developed with Python 3.6.4")
		sys.exit(4)

	main(args.username, args.password, args.count, args.output, args.seconds)
