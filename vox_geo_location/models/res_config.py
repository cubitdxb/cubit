# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ApiSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_url = fields.Char(string="API Url")
    api_key = fields.Char(string="API Key")

    @api.model
    def get_values(self):
        res = super(ApiSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        api_url = params.get_param('api_url', default=False)
        api_key = params.get_param('api_key', default=False)

        res.update(
            api_url=api_url,
            api_key=api_key,
        )
        return res

    def set_values(self):
        super(ApiSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("api_url",
                                                         self.api_url)
        self.env['ir.config_parameter'].sudo().set_param("api_key",
                                                         self.api_key)

