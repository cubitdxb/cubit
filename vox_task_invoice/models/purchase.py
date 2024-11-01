# -*- coding: utf-8 -*-
from odoo import models, fields, api
class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    is_cancel_down_payment = fields.Boolean(string="Cancel Down Payment?")