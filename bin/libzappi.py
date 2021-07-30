#!/usr/bin/python3

import json
import configparser
import requests
from requests.auth import HTTPDigestAuth
import sys
import os

# import time
from pprint import pprint

# constants
HERE = os.path.realpath(__file__).split("/")
# runlist id :
MYID = HERE[-1]
# app_name :
MYAPP = HERE[-3]
MYROOT = "/".join(HERE[0:-3])
# host_name :
NODE = os.uname()[1]

# CONFIG_FILE = os.environ["HOME"] + "/.config/kamstrup/key.ini"
DIRECTOR_URL = "https://director.myenergi.net"
ZAPPI_DEFAULT = {
    "hr": 0,
    "dow": "Mon",
    "dom": 1,
    "mon": 1,
    "yr": 2021,
    "exp": 0,
    "gen": 0,
    "gep": 0,
    "imp": 0,
    "h1b": 0,
    "h1d": 0,
}


class Myenergi:
    def __init__(self, config_file, debug=False):
        global DEBUG
        global DIRECTOR_URL
        global ZAPPI_DEFAULT

        iniconf = configparser.ConfigParser()
        iniconf.read(config_file)
        self.hub_serial = iniconf.get("HUB", "serial")
        self.hub_password = iniconf.get("HUB", "password")
        self.zappi_serial = iniconf.get("ZAPPI", "serial")
        self.harvi_serial = iniconf.get("HARVI", "serial")
        self.zappi_data_default = ZAPPI_DEFAULT
        self.base_url = DIRECTOR_URL
        self.response = requests.get(
            self.base_url,
            auth=HTTPDigestAuth(self.hub_serial, self.hub_password),
        )
        self.DEBUG = debug
        if self.DEBUG:
            print("Response :")
            pprint(self.response)
            print("")
            for key in self.response.headers:
                print(key, "  :  ", self.response.headers[key])
            print("")
        # construct the URL to the ASN
        if "X_MYENERGI-asn" in self.response.headers:
            self.asn = self.response.headers["X_MYENERGI-asn"]
            self.base_url = "https://" + self.asn
            if self.DEBUG:
                print("ASN :")
                print(self.asn)
                print("baseURL :")
                print(self.base_url)
        else:
            print("MyEnergi ASN not found in MyEnergi header")

    def get_status(self, command):
        hdrs = {"User-Agent": "Wget/1.20 (linux-gnu)"}

        callURL = "/".join([self.base_url, command])
        if self.DEBUG:
            print(callURL)
        try:
            response = requests.get(
                callURL,
                headers=hdrs,
                auth=HTTPDigestAuth(self.hub_serial, self.hub_password),
                timeout=10,
            )
        except requests.exceptions.ReadTimeout:
            print("!!! TimeOut")
            sys.exit(0)

        result = json.loads(response.content)
        if self.DEBUG:
            print(response.status_code)
            for key in response.headers:
                print(key, "  ::  ", response.headers[key])
            print(f"### Payload {command}")
            pprint(result)
            print("***************")
        return result

    def trans_data_block(self, block, dst):
        """translate a block of data from the zappi

                    Args:
                        block (dict): example:
                        {
                            'hr': 18,
                            'dow': 'Tue',
                            'dom': 27,
                            'mon': 7,
                            'yr': 2021,
                            'imp': 893760,
                            'gep': 69900,
                            'gen': 3060
                            }


                    Returns:
                        list: values for each paramater in the template. 0 for missing values.
                                data_lbls: ['07-27 12h' '07-27 13h' '07-27 14h' '07-27 15h' '07-27 16h' '07-27 17h'
        '07-27 18h' '07-27 19h' '07-27 20h' '07-27 21h']
        """
        for key in self.zappi_data_default:
            if key not in block:
                # print(key, "!")
                block[key] = self.zappi_data_default[key]
                # print(key, block[key])
        exp = int(block["exp"] / 3600) / 1000
        imp = int(block["imp"] / 3600) / 1000
        gep = int(block["gep"] / 3600) / 1000
        gen = int(block["gen"] / 3600) / 1000
        h1b = int(block["h1b"] / 3600) / 1000
        h1d = int(block["h1d"] / 3600) / 1000
        # hack to display localtime in stead of UTC
        block_date = f"{str(block['mon']).zfill(2)}-{str(block['dom']).zfill(2)} {str(block['hr'] + 1 + dst).zfill(2)}h"
        #       block_date, imp, gep, gen, exp, h1d
        return [block_date, imp, gep, gen, exp, h1b, h1d]
