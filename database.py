from supabase import create_client, Client
from datetime import datetime
import requests as re
from bs4 import BeautifulSoup
import schedule
import time

# Replace these with your actual Supabase URL and API Key
supabase_url = "https://xjgfurxtzkfpcfyiedcu.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhqZ2Z1cnh0emtmcGNmeWllZGN1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA3MjQzNjMsImV4cCI6MjA0NjMwMDM2M30.oLWk6OAqcSC59OzIpf-ZyZX2l3ToRDTTk6e2fNwP3q0"

# Initialize the Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# Get the current date and time in GMT
current_date = datetime.utcnow()


current_date_str = current_date.isoformat() + 'Z'


def createData(data):
    try:
        insert_data = supabase.table("Event").insert(data).execute()
        print(insert_data)
    except Exception as e:
        print(e)


def updateData():
    # Now you can interact with your Supabase database
    try:
        response = supabase.table("Event").select("*, Vote(*, User(*))") \
            .lt("eventDate", current_date_str) \
            .eq("Status", "Ongoing") \
            .execute()
        print(response.data)
        #
        for item in response.data:
            scrapeddata = re.get(f"https://www.cricbuzz.com/{item['ResultUrl']}")
            parsedData = BeautifulSoup(scrapeddata.content, "html.parser")
            div_element = parsedData.find("div", {"class": "cb-col cb-col-100 cb-min-stts cb-text-complete"})
            if div_element is None:
                inningsbreak = parsedData.find("div", {"class": "cb-text-inningsbreak"})
                inprogress = parsedData.find("div", {"class": "cb-text-inprogress"})
                if inprogress is not None:
                    supabase.table("Event").update({"Description": inprogress.text}).eq("id", item["id"]).execute()
                if inningsbreak is not None:
                    supabase.table("Event").update({"Description": inningsbreak.text}).eq("id", item["id"]).execute()
            else:
                winner_team = div_element.text.split(" ")[0].strip()

                teams_key = {
                    "ONE": item["Team1"],
                    "TWO": item["Team2"]
                }

                supabase.table("Event").update({"Status": "Completed", "Description": div_element.text}).eq("id", item[
                    "id"]).execute()
                for vote in item["Vote"]:
                    if teams_key[vote["predicted"]] == winner_team:
                        updated_amount = vote["User"]["balance"]

                        if vote["predicted"] == "ONE":
                            updated_amount += vote["amount"] * 1.5
                        else:
                            updated_amount += vote["amount"] * 2.5
                        print(updated_amount)

                        supabase.table("User").update({"balance": int(updated_amount)}).eq("id",
                                                                                           vote["User"]["id"]).execute()
                        supabase.table("Vote").update({"status": "WON"}).eq("id", vote["id"]).execute()

                    else:
                        supabase.table("Vote").update({"status": "LOST"}).eq("id", vote["id"]).execute()

                        print("wrong")
    except Exception as e:
        print(e)



updateData()

