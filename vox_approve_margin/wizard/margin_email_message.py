# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
class confirm_wizard(models.TransientModel):
    _name = 'approval.message'


    email_margin_text= fields.Char(default='You cannot confirm SO without E-mail Approval and margin is less than 5%')
    margin_text= fields.Char(default='It is not allowed to confirm an order when the margin is less than 5%')
    email_text= fields.Char(default='You cannot confirm SO without E-mail Approval')
    sale_order_id = fields.Many2one('sale.order', 'Sale ID')


    @api.model
    def _prepare_default_get(self, order):
        default = {
            'sale_order_id':order.id if self._context.get('active_model') == 'sale.order' else False
        }
        return default

    @api.model
    def default_get(self, fields):
        res = super(confirm_wizard, self).default_get(fields)
        if self._context.get('active_model') == 'sale.order':
            order = self.env['sale.order'].browse(self._context.get('active_id'))
            default = self._prepare_default_get(order)
            res.update(default)
        return res

    def margin_approve(self):
        for order in self.sale_order_id:
            order.write({'state': 'send_for_margin_approval'})
        return

    def email_approve(self):
        # current_id = self.env.context.get('current_id', False)
        # picking = self.env['sale.order'].browse(current_id)
        for order in self.sale_order_id:
            order.write({'state': 'send_for_email_approval'})
        return

    def email_margin_approve(self):
        for order in self.sale_order_id:
            order.write({'state': 'send_for_lpo_email_margin_approval'})
            # self.state = 'send_for_lpo_email_margin_approval'
        return
