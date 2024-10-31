# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
class SaleCancelRemark(models.TransientModel):
    _name = 'sale.cancel.remark'

    name = fields.Char(string="Remarks", store=True)

    sale_id = fields.Many2one(
        'sale.order', string='Sale Order', readonly=True)

    def _prepare_update_so(self):
        self.ensure_one()
        return {
            'quote_cancel_remark': self.name,
        }

    def confirm(self):
        self.ensure_one()
        vals = self._prepare_update_so()
        self.sale_id.write(vals)
        self.sale_id.action_cancel()
        return True


