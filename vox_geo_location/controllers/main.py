# -*- coding: utf-8 -*-
###############################################################################
#
#    Voxtron
#    Copyright (C) 2009-TODAY Voxtron solutions(<https://www.voxtronme.com/>).
#
###############################################################################

import logging
from odoo import models, fields, _,api
from odoo.exceptions import UserError,ValidationError
from datetime import datetime
from datetime import timedelta
import geocoder
import requests
from odoo import http
from odoo.http import request
from geopy.geocoders import Nominatim


class TraccarController(http.Controller):
    @http.route('/traccar/get_all_devices', type='http', auth='none', methods=['GET'])
    def get_all_devices(self):
        print(111111111111111111111111111111111111111111)
        # traccar_service = TraccarService(
        #     request.env['ir.config_parameter'].get_param(key_traccar_api_url),
        #     request.env['ir.config_parameter'].get_param(key_traccar_api_key)
        # )
        #
        # # Fetch all devices from Traccar
        # devices = traccar_service.get_all_devices()
        url = 'http://localhost:8082/api/devices'
        headers = {
            # "Authorization": "apikey %s" % keys,
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        print(response.json())

        # return devices

    # def get_all_devices(self):
    #     url = 'localhost:8082/api/devices'
    #     headers = {'Authorization': f'Bearer {self.api_key}'}
    #     response = requests.get(url, headers=headers)
    #
    #     if response.status_code == 200:
    #         return response.json()
    #     else:
    #         raise Exception(f'Error {response.status_code}: {response.text}')