# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from datetime import datetime


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    @api.onchange('show_end_customer')
    def onchange_end_customer(self):
        for order in self:
            if order.show_end_customer == True:
                order.end_partner_id = order.sale_id.partner_id.id
