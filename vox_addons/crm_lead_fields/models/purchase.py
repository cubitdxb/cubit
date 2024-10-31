# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class purchase_order_line(models.Model):
    _inherit = "purchase.order.line"

    sale_line_id = fields.Many2one('sale.order.line', 'Sale Line')
    cubit_purchase_id = fields.Integer(string="Cubit ID")

