import requests as re
from bs4 import BeautifulSoup
from database import createData
from dateutil import parser
from datetime import datetime
import pytz

def fetchMatches():
    try:
        print("started")
        response = re.get("https://www.cricbuzz.com/cricket-schedule/upcoming-series/international")

        content = BeautifulSoup(response.content,
                                "html.parser")
        listofmatches = content.find_all("div", {"class": "cb-col-100 cb-col"})

        for item in listofmatches:

            datae = item.find("div", {"class": "cb-lv-grn-strip"})

            matches = item.find_all("div", {"class": "cb-col-100 cb-col"})
            for match in matches:
                title = match.find("a", title=True)
                venue = match.find("div", {"itemprop": "location"})
                time = match.find("div", {"class": "cb-col-50 cb-col cb-mtchs-dy-tm cb-adjst-lst"})
                time_details = time.text.split("/")[0].strip().split(' ')
                time_str = f"{time_details[0]} {time_details[1]}"
                parsed_time = datetime.strptime(time_str, "%I:%M %p")
                parsed_date = parser.parse(datae.text)

                event_datetime = datetime.combine(parsed_date.date(), parsed_time.time())
                event_datetime = pytz.timezone(time_details[2]).localize(event_datetime)

                event = {
                    "Team1": title.text.split(",")[0].split("vs")[0].strip(),
                    "Team2": title.text.split(",")[0].split("vs")[1].strip(),
                    "Venue": venue.text.strip(),
                    "ResultUrl": title["href"].strip(),
                    "Description": title.text.strip(),
                    "eventDate": event_datetime.isoformat(),
                    "updatedAt": datetime.now().isoformat()

                }

                createData(event)
    except Exception as e:
        print(e)



fetchMatches()


