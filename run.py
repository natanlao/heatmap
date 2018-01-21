# -*- coding: utf-8 -*-
import datetime
import email.utils
import time
import os.path

from bs4 import BeautifulSoup
import requests

from heatmap.model import db, Listing, Subnet

if not os.path.exists("heatmap.db"):
    db.create_tables([Subnet, Listing])

def get_data():
    # TODO: Error checking
    r = requests.get("https://www2.ucsc.edu/its/dhcpstats/")
    return parse_data(r.content)


def parse_data(html):
    s = BeautifulSoup(html, "html.parser")

    newtime = email.utils.parsedate_to_datetime(s.b.text.strip())
    try:
        oldtime = Listing.select().order_by(Listing.asof.desc()).get().asof
        if not (newtime > oldtime):
            return
    except Listing.DoesNotExist:
        # Then this is the first run, continue.
        pass

    # Skip header row and isolate table
    rows = s.find_all("tr")
    for row in rows[1:]:
        data = dict(zip([i.text.strip() for i in rows[0].findChildren("th")], \
                        [i.text.strip() for i in row.children]))
        snet = Subnet.get_or_create(
                comment=data['Comment'],
                network=data['Network'],
                subnet=data['Subnet'],
                gateway=data['Gateway']
        )
        Listing.create(
                subnet=snet,
                fixed=int(data['Fixed']),
                pool=int(data['Pool']),
                assigned=int(data['Assigned']), asof="2018-01-01 01:01:01"
                #asof=str(newtime.strftime("%Y-%m-%d %H:%M:%S"))
        )

if __name__ == "__main__":
    get_data()
    exit()
    while True:
        get_data()
        time.sleep(60)

