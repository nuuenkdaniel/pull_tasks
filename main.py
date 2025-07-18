import requests
import xml.etree.ElementTree as ET

import json
with open("config.json", 'r') as conf:
    config = json.load(conf)
    NEXTCLOUD_URL = config["NEXTCLOUD_URL"]
    USERNAME = config["USER"]
    PASSWORD = config["PASS"]
    CALDAV_PATH = f"{config['CALDAV_PATH']}{USERNAME}/{config['LIST']}"


REPORT_BODY = """<?xml version="1.0" encoding="UTF-8"?>
<c:calendar-query xmlns:c="urn:ietf:params:xml:ns:caldav" xmlns:d="DAV:">
  <d:prop>
    <d:getetag/>
    <c:calendar-data/>
  </d:prop>
  <c:filter>
    <c:comp-filter name="VCALENDAR">
      <c:comp-filter name="VTODO"/>
    </c:comp-filter>
  </c:filter>
</c:calendar-query>
"""

# ---------- Make the REPORT request ----------
url = NEXTCLOUD_URL + CALDAV_PATH
headers = {
    "Depth": "1",
    "Content-Type": "application/xml; charset=utf-8"
}

response = requests.request(
    method="REPORT",
    url=url,
    auth=(USERNAME, PASSWORD),
    headers=headers,
    data=REPORT_BODY
)

if response.status_code != 207:
    print("Error: received status", response.status_code, response.text)
    exit(1)

ns = {"d": "DAV:", "c": "urn:ietf:params:xml:ns:caldav"}
root = ET.fromstring(response.content)

tasks = []
for resp in root.findall("d:response", ns):
    href = resp.find("d:href", ns).text
    calendar_data = resp.find(".//c:calendar-data", ns).text.strip()
    task_lines = [l for l in calendar_data.splitlines()
        if l.startswith(("SUMMARY:", "UID:", "DUE:", "DESCRIPTION:"))]
    task = {}
    for line in task_lines:
        key, value = line.split(":", 1)
        task[key] = value
    task["href"] = href
    tasks.append(task)

for t in tasks:
    print("Task:", t.get("SUMMARY"))
    print("Due:", t.get("DUE"))
    print("UID:", t.get("UID"))
    print("Link path:", t.get("href"))
    print()
