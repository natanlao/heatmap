# -*- coding: utf-8 -*-
import datetime
import email.utils
import time
import os.path

from bs4 import BeautifulSoup, SoupStrainer
import pytz
import requests

from heatmap.models import db, Listing, Subnet

if not os.path.exists("heatmap.db"):
    db.create_tables([Subnet, Listing])

def get_data():
    # TODO: Error checking
    r = requests.get("https://www2.ucsc.edu/its/dhcpstats/")
    return parse_data(r.content)


def parse_data(html):
    s = BeautifulSoup(html, "lxml", parse_only=SoupStrainer(["b", "table"]))

    newtime = email.utils.parsedate_to_datetime(s.b.text.strip())
    try:
        oldtime = Listing.select().order_by(Listing.asof.desc()).get().asof
        oldtime = datetime.datetime.strptime(oldtime, "%Y-%m-%d %H:%M:%S-08:00").replace(tzinfo=pytz.timezone("US/Pacific"))
        if not (newtime > oldtime):
            return
    except Listing.DoesNotExist:
        # Then this is the first run, continue.
        pass

    # Skip header row and isolate table
    rows = s.find_all("tr")
    listings = []
    for row in rows[1:]:
        data = dict(zip([i.text.strip() for i in rows[0].findChildren("th")], \
                        [i.text.strip() for i in row.children]))
        snet, _ = Subnet.get_or_create(
                comment=data['Comment'],
                network=data['Network'],
                subnet=data['Subnet'],
                gateway=data['Gateway']
        )
        listings.append({
            'subnet': snet.id,
            'fixed': data['Fixed'],
            'pool': data['Pool'],
            'assigned': data['Assigned'],
            'asof': newtime
        })

    with db.atomic():
        print("Inserting %d records" % len(listings))
        Listing.insert_many(listings).execute()

if __name__ == "__main__":
    get_data()
    exit()
    import os.path
    for f in sorted(os.listdir("data"), key=lambda x: os.path.getmtime("data/"+x)):
        print(f)
        with open(os.path.join("data", f), "r") as html:
            parse_data(html)
    exit()
    while True:
        get_data()
        time.sleep(60)

