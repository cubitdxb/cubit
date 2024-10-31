# -*- coding: utf-8 -*-
from odoo import models, fields


class EndUserRequiredConditions(models.TransientModel):
    _name = 'end.user.req.conditions'
    _description = 'End User Required Conditions'

    required_msg = fields.Text(string='Required Message',
                               default='Is the Customer and End User the Same?')
    warning_msg = fields.Text(string="Warning Message", default='* If NO, kindly complete end-user details')

    def confirm(self):
        end_user_email = end_user_mobile = end_user_name = ''
        sale_rec = self.env['sale.order'].browse(self.env.context.get('active_id'))
        if sale_rec.partner_contact:
            end_user_email = sale_rec.partner_contact.email
            end_user_mobile = sale_rec.partner_contact.mobile
            end_user_name = sale_rec.partner_contact.name

        sale_rec.write({
            'end_user_req_condition': 'yes',
            'end_user_name': end_user_name,
            'end_user_mobile': end_user_mobile,
            'end_user_mail': end_user_email,
            'end_user_website': sale_rec.partner_id.website,
            'end_user_fax': sale_rec.partner_id.fax,
            'end_user_company_value': sale_rec.partner_id.name,
            'end_user_vat': sale_rec.partner_id.vat,
            'end_user_address': sale_rec.partner_id.street + " " + sale_rec.partner_id.street2
            if sale_rec.partner_id.street2 and sale_rec.partner_id.street else sale_rec.partner_id.street
        })
        sale_rec.action_confirm()

    def not_confirm(self):
        sale_rec = self.env['sale.order'].browse(self.env.context.get('active_id'))
        sale_rec.write({
            'end_user_req_condition': 'no',
        })
        return {'type': 'ir.actions.act_window_close'}
