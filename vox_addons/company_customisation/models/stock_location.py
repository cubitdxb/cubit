from odoo import models, fields, api, _


class StockLocation(models.Model):
    _inherit = 'stock.location'

    cubit_id = fields.Integer('Cubit Id')
