# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
class ResPartner(models.Model):
    _inherit = "res.partner"

    sales_team_users = fields.Many2many('res.users','partner_sales_coordinator_rel', 'id', 'user_id', string='Sales Coordinator')
    renewal_team_users = fields.Many2many('res.users','partner_renewal_rel', 'id', 'user_id', string='Renewal Users')
    amc_team_users = fields.Many2many('res.users','partner_amc_rel', 'id', 'user_id', string='AMC Users')
    msp_team_users = fields.Many2many('res.users','partner_msp_rel', 'id', 'user_id', string='MSP Users')
    cisco_team_users = fields.Many2many('res.users','partner_cisco_rel', 'id', 'user_id', string='Cisco Users')


    @api.onchange('user_id')
    def _onchange_user_id(self):
        for partner in self:
            if partner.user_id:
                partner.sales_team_users = partner.user_id.sales_team_users.ids





