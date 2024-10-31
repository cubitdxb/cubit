# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    period_id = fields.Many2one('account.period', string="Period")

