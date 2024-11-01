# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
class account_journal_period(models.Model):
    _name = "account.journal.period"
    _description = "Journal Period"
    _order = "period_id"

    name = fields.Char('Journal-Period Name', required=True)
    journal_id = fields.Many2one('account.journal', 'Journal', required=True, ondelete="cascade")
    period_id = fields.Many2one('account.period', 'Period', required=True, ondelete="cascade")
    active = fields.Boolean('Active', help="If the active field is set to False, it will allow you to hide the journal period without removing it.",default=True)
    state = fields.Selection([('draft','Draft'), ('printed','Printed'), ('done','Done')], 'Status', required=True, readonly=True,default='draft',
                              help='When journal period is created. The status is \'Draft\'. If a report is printed it comes to \'Printed\' status. When all transactions are done, it comes in \'Done\' status.')

    company_id = fields.Many2one('res.company', related='period_id.company_id', string='Company')
