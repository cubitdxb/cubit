from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api,_
from odoo.exceptions import UserError


class AgedTrialBalanceBillwise(models.TransientModel):
    _name = 'account.aged.trial.balance.xls'
    _description = 'Account Aged Trial balance Report Bill-wise'

    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    target_move = fields.Selection([('all', 'All'), ('posted', 'Posted')])
    period_length = fields.Integer(string='Period Length (days)', required=True, default=30)
    result_selection = fields.Selection([('customer', 'Receivable Accounts'),
                                         ('supplier', 'Payable Accounts'),
                                         # ('customer_supplier', 'Receivable and Payable Accounts')
                                         ], string="Partner's", required=True, default='customer')

    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['from_date', 'to_date', 'result_selection', 'target_move','period_length'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        return self._print_report(data)

    def _build_contexts(self, data):
        result = {}
        result['from_date'] = data['form']['from_date'] or False
        result['to_date'] = data['form']['to_date'] or False
        result['target_move'] = data['form']['target_move'] or False
        result['period_length'] = data['form']['period_length'] or False
        result['result_selection'] = data['form']['result_selection'] or False
        ctx = dict(self.env.context)
        self.env.context = ctx
        return result



    def _print_report(self, data):
        res = {}
        data['form'].update(self.read(['result_selection'])[0])
        data['form'].update(self.read(['period_length'])[0])
        period_length = data['form']['period_length']
        if period_length <= 0:
            raise UserError(_('You must set a period length greater than 0.'))
        if not data['form']['from_date']:
            raise UserError(_('You must set a start date.'))

        start = datetime.strptime(str(data['form']['from_date']), "%Y-%m-%d")

        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length - 1)
            res[str(i)] = {
                'name': (i != 0 and (str((5 - (i + 1)) * period_length) + '-' + str((5 - i) * period_length)) or (
                '+' + str(4 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
        data['form'].update(res)
        return self.env.ref('vox_ageing_invoice_number.financial_report_xlsx').with_context(landscape=True).report_action(self, data=data)