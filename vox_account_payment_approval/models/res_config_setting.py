# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    payment_approval = fields.Boolean(string='Account Payment Approval ', help="Enable Account Payment Approval ")
    payment_approval_amount = fields.Float(string="Minimum Account")

    def set_values(self):
        res = super(ResConfigSetting, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('vox_account_payment_approval.payment_approval', self.payment_approval)
        self.env['ir.config_parameter'].sudo().set_param('vox_account_payment_approval.payment_approval_amount', self.payment_approval_amount)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSetting, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res['payment_approval'] = (get_param('vox_account_payment_approval.payment_approval'))
        res['payment_approval_amount'] = (get_param('vox_account_payment_approval.payment_approval_amount'))
        return res