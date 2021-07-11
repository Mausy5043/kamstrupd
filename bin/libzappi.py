#!/usr/bin/python3

import requests
from requests.auth import HTTPDigestAuth
import sys
import time
from pprint import pprint

BASEURL = "https://director.myenergi.net"


class Zappi:
    """Support for Zappi v2 from myEnergi API."""

    def __init__(self, password, serial):
        global BASEURL
        self.hub_password = password
        self.hub_serial = serial
        self.myenergi_base_url = BASEURL

    def get_server_url(self):
        """update server URL by requesting the ASN"""
        myenergi_response = requests.get(
            self.myenergi_base_url,
            auth=HTTPDigestAuth(self.hub_serial, self.hub_password),
        )
        if "X_MYENERGI-asn" in myenergi_response.headers:
            self.myenergi_base_url = (
                "https://" + myenergi_response.headers["X_MYENERGI-asn"]
            )
        else:
            print("MyEnergi ASN not found in Myenergi header")

    def get_status(self):
        hdrs = {"User-Agent": "Wget/1.14 (linux-gnu)"}

        success = False

        for i in range(3):
            try:
                theURL = self.myenergi_base_url + "/cgi-jstatus-*"
                response = requests.get(
                    theURL,
                    headers=hdrs,
                    auth=HTTPDigestAuth(self.hub_serial, self.hub_password),
                    timeout=10,
                )
            except:
                print("Myenergi server request problem")
            else:
                # self.checkMyEnergiServerURL(response.headers)
                if response.status_code == 200:
                    print("response.json()")
                    pprint(response.json())
                    success = True
                else:
                    print(
                        "Myenergi server call unsuccessful, returned code: "
                        + str(response.status_code)
                    )

            if success == True:
                break
            else:
                time.sleep(1)


# temporary code for testing:

HUB_SERIAL = "8888888"
HUB_PWD = "password"

# zresponse = requests.get(BASEURL, auth=HTTPDigestAuth(HUB_SERIAL, HUB_PWD))
# pprint(zresponse.status_code)
# print("*****")
# pprint(zresponse.__dict__)
# print("*****")
# pprint(zresponse.headers['X_MYENERGI-asn'])
# print("**********")
# abort here
# sys.exit(0)
zappi = Zappi(HUB_PWD, HUB_SERIAL)
print("*****")
zappi.get_server_url()
pprint(zappi.myenergi_base_url)
print("*****")
zappi.get_status()
