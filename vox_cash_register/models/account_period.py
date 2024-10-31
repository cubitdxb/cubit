# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class account_period(models.Model):
    _name = "account.period"
    _description = "Account period"
    _order = "date_start, special desc"

    cubit_id = fields.Integer('Cubit ID')
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Fiscal Year', required=True,
                                    states={'done': [('readonly', True)]})
    name = fields.Char('Period Name', required=True)
    code = fields.Char('Code', size=12)
    special = fields.Boolean('Opening/Closing Period', help="These periods can overlap.")
    date_start = fields.Date('Start of Period', required=True, states={'done': [('readonly', True)]})
    date_stop = fields.Date('End of Period', required=True, states={'done': [('readonly', True)]})
    state = fields.Selection([('draft', 'Open'), ('done', 'Closed')], 'Status', readonly=True, copy=False,
                             help='When monthly periods are created. The status is \'Draft\'. At the end of monthly period it is in \'Done\' status.',
                             default='draft')
    company_id = fields.Many2one('res.company',related='fiscalyear_id.company_id', string="Company", store=True)

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)', 'The name of the period must be unique per company!'),
    ]
