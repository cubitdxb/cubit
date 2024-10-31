# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
class account_fiscalyear(models.Model):
    _name = "account.fiscalyear"
    _description = "Fiscal Year"
    _order = "date_start, id"

    name = fields.Char(string="Fiscal Year", required=True)
    code = fields.Char(string="Code", size=6, required=True)
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)
    state = fields.Selection([('draft', 'Open'), ('done', 'Closed')],string="Status", default='draft')
    date_start = fields.Date('Start Date', required=True)
    end_journal_period_id = fields.Many2one('account.journal.period', 'End of Year Entries Journal',readonly=True, copy=False)
    date_stop = fields.Date('Start Date', required=True)
    period_ids = fields.One2many('account.period', 'fiscalyear_id', 'Periods')
    cubit_id = fields.Integer('Cubit ID')

    def create_period3(self):
        return self.create_period(3)

    def create_period(self,interval=1):
        period_obj = self.env['account.period']
        for fy in self:
            ds = datetime.strptime(str(fy.date_start), '%Y-%m-%d')
            period_obj.create({
                    'name':  "%s %s" % (_('Opening Period'), ds.strftime('%Y')),
                    'code': ds.strftime('00/%Y'),
                    'date_start': ds,
                    'date_stop': ds,
                    'special': True,
                    'fiscalyear_id': fy.id,
                })
            while ds.strftime('%Y-%m-%d') < str(fy.date_stop):
                de = ds + relativedelta(months=interval, days=-1)

                if de.strftime('%Y-%m-%d') > str(fy.date_stop):
                    de = datetime.strptime(fy.date_stop, '%Y-%m-%d')

                period_obj.create({
                    'name': ds.strftime('%m/%Y'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'fiscalyear_id': fy.id,
                })
                ds = ds + relativedelta(months=interval)
        return True
