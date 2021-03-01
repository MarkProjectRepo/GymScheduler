from selenium import webdriver
from datetime import datetime, timedelta
from time import sleep
import re, sys, json
from selenium.webdriver import FirefoxOptions



SCHEDULED_FILE = "C:/Users/MTisME/Documents/Python Scripts/GymScheduler/scheduled_tasks.txt"

import sys
sys.stdout = open("C:/Users/MTisME/Documents/Python Scripts/GymScheduler/scheduling_log.txt", 'a+')
sys.stderr = open("C:/Users/MTisME/Documents/Python Scripts/GymScheduler/scheduling_log.txt", 'a+')
def reserve_timeslots(browser=None):
	if not browser:
		opts = FirefoxOptions()
		opts.add_argument("--headless")
		browser = webdriver.Firefox(options=opts)
	
	browser.get("https://lafitness.com")

	creds = json.loads(open("credentials.json","r").read())

	# For a minor speed up (every second counts here) use username/password hashes
	# and load them directly into cookies, avoiding needing to go to the login screen all the way
	browser.add_cookie({"name": "LAFitness.Password", "value": creds["password"]})
	browser.add_cookie({"name": "LAFitness.Username", "value": creds["username"]})

	browser.find_element_by_id("ctl00_GlobalHeader_lnkLogin").click()

	browser.get("https://www.lafitness.com/Pages/ClubReservation.aspx?clubID=482")

	# If we're not at the bottom of the hour, wait the remaining seconds
	if datetime.now().second > 0 or datetime.now().minute != 0:
		print(f"Waiting to refresh, time is currently {datetime.now()}\n")
		now = datetime.now()

		wait_seconds = 60 - now.second
		print(f"Waiting {wait_seconds} seconds")
		sleep(wait_seconds)
		browser.refresh()
		print(f"Refreshed browser after waiting {wait_seconds} seconds\n")

	# The way the gym scheduling works is such that you book two days in advance
	# and weekend hours are different from weekday	
	if 2 < datetime.today().weekday() < 5:
		time_to_book = ["12","01","02","03","04","05"]
	else:
		time_to_book = ["05","12"]

	# Look for time slots in our current range
	print(f"Checking booking times for {time_to_book}... \n")
	booked = ""
	for timeslot in time_to_book:
		x = list(filter(lambda a: a.text.startswith(timeslot) and not bool(re.search("\d{1,2}\/\d{1,2}\/\d{4}",a.text)) and "pm" in a.text.lower(), browser.find_elements_by_tag_name("tr")))
		if x:
			booked = timeslot
			x = x[0]

			print(f"\n{x} ")
			output = []
			print(f"Found a time slot...\n")

			try:
				x.find_element_by_tag_name("a").click()
			except:
				print("No <a>, oh well")
				continue

			OK_button = list(filter(lambda a:a.text == "OK", browser.find_elements_by_tag_name("button")))[-1]
			OK_button.click()
			output.append(f"\nScheduled a task {str(datetime.now())}\n at {booked}")
			browser.save_screenshot(f"screenshots/{datetime.now()}.png")
			# When we've scheduled something, write it to our successful schedule file
			with open(SCHEDULED_FILE, "a+") as f:
				for elem in output:
					f.write(elem)
			break

	browser.close()

if __name__ == "__main__":
	reserve_timeslots()