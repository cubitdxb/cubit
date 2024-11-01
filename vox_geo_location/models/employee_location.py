# -*- coding: utf-8 -*-
###############################################################################
#
#    Voxtron
#    Copyright (C) 2009-TODAY Voxtron solutions(<https://www.voxtronme.com/>).
#
###############################################################################

import logging
from odoo import models, fields, _,api
import requests
from odoo.http import request
from geopy.geocoders import Nominatim
import json
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class EmployeeLocation(models.Model):
    _name = 'employee.location'
    _description = 'Employee Location Details'
    _order = 'create_date desc'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    latitude = fields.Char(string='Latitude')
    longitude = fields.Char(string='Longitude')
    altitude = fields.Char(string='Altitude')
    total_distance = fields.Char(string='Total Distance')
    address = fields.Char(string='Address')
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    google_maps_link = fields.Html(
        string='Google Maps Link',
        compute='_compute_google_maps_link',
        store=False  # Set to True if you want to store the link in the database
    )
    device_status = fields.Char('Device Status')

    def _compute_google_maps_link(self):
        for record in self:
            if record.latitude and record.longitude:
                google_maps_url = f'https://maps.google.com/?q={record.latitude},{record.longitude}'
                record.google_maps_link = f'<a href="{google_maps_url}" target="_blank">Open in Google Maps</a>'
            else:
                record.google_maps_link = '<p>No location data available</p>'


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    unique_id = fields.Char('Unique ID')

    # @api.model
    # def create(self, vals):
    #     res = super(HrEmployee, self).create(vals)
    #     traccar_api_url = self.env['ir.config_parameter'].sudo().get_param('api_url')
    #     keys = self.env['ir.config_parameter'].sudo().get_param('api_key')
    #     headers = {'Authorization': 'Basic %s' % keys}
    #     data = {
    #         "name": vals['name'],
    #         "email": vals['work_email'] if vals['work_email'] else '',
    #         "phone": vals['work_phone'] if vals['work_phone'] else '',
    #         "readonly": True,
    #         "administrator": False,
    #         "expirationTime": "2019-08-24T14:15:22Z",
    #         "deviceLimit": 0,
    #         "userLimit": 0,
    #     }
    #     response = requests.post(traccar_api_url, headers=headers, data=json.dumps(data))
    #
    #     device_data = {
    #               "name": vals['name']+ ' Phone',
    #               "uniqueId": vals['name'],
    #               "positionId": 0,
    #               "groupId": 0,
    #               "phone": "string",
    #               "model": "string",
    #               "contact": "string",
    #               "category": "string",
    #               "attributes": {}
    #             }
    #
    #     return res

    def get_device_info(self):
        traccar_api_url = self.env['ir.config_parameter'].sudo().get_param('api_url')
        keys = self.env['ir.config_parameter'].sudo().get_param('api_key')
        # traccar_api_url = 'http://127.0.0.1:8082/api'
        headers = {'Authorization': 'Basic %s' %keys}

        response_device = requests.get(f'{traccar_api_url}/devices', headers=headers)
        try:
            if response_device.status_code == 200:
                device_info = response_device.json()
                return  device_info
            else:
                # Handle error response
                return None
        except Exception as e:
            print(f"JSON decoding error: {e}")

    def get_position_info(self):
        traccar_api_url = self.env['ir.config_parameter'].sudo().get_param('api_url')
        keys = self.env['ir.config_parameter'].sudo().get_param('api_key')
        # traccar_api_url = 'http://127.0.0.1:8082/api'
        headers = {'Authorization': 'Basic %s' % keys}
        response_positions = requests.get(f'{traccar_api_url}/positions', headers=headers)
        try:
            if response_positions.status_code == 200:
                device_positions = response_positions.json()
                print(device_positions, 222222222222222222222)
                return device_positions
            else:
                # Handle error response
                return None
        except Exception as e:
            print(f"JSON decoding error: {e}")

    @api.model
    def get_employee_location_details(self):
        position_informations = self.get_position_info()
        device_informations = self.get_device_info()
        print(position_informations, 'position infor')
        print(device_informations, 'device info')
        geolocator = Nominatim(user_agent="coordinateconverter")
        for rec in device_informations:
            employee_details = self.env['hr.employee'].search([('unique_id', '=', rec['uniqueId'])])
            print(employee_details, 22222222222222222222222)
            for position in position_informations:
                if position['deviceId'] == rec['id']:
                    address = "%s, %s" %(position['latitude'], position['longitude'])
                    location = geolocator.reverse(address)
                    if employee_details:
                        location_data = {
                            'latitude': position['latitude'],
                            'longitude': position['longitude'],
                            'altitude': position['altitude'],
                            'employee_id': employee_details.id if employee_details else None,
                            'address': location,
                            'device_status': rec['status']
                        }
                        self.env['employee.location'].create(location_data)



