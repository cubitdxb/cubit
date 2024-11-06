# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    type = fields.Selection(selection_add=[('existing_contact', 'Existing Contact')])
    existing_partner_id = fields.Many2one('res.partner', string='Existing Partner')

    @api.onchange('type')
    def _domain_existing_partners(self):
        print(222222222222222222222222222222222)
        res_partner_individuals = self.env['res.partner'].search([('company_type', '!=', 'company'), ('is_company', '=', False)]).ids
        return {'domain': {'existing_partner_id': [('id', 'in', res_partner_individuals)]}}

    @api.onchange('existing_partner_id')
    def onchange_existing_partner_id(self):
        for rec in self:
            rec.name = rec.existing_partner_id.name
            rec.email = rec.existing_partner_id.email if rec.existing_partner_id.email else False
            rec.function = rec.existing_partner_id.function if rec.existing_partner_id.function else False
            rec.mobile = rec.existing_partner_id.mobile if rec.existing_partner_id.mobile else False
            rec.phone = rec.existing_partner_id.phone if rec.existing_partner_id.phone else False
