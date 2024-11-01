import time
import datetime
from datetime import date, datetime
from odoo import api, models, _
from odoo.exceptions import UserError

class ReportCustomerSOA(models.AbstractModel):
    _name = 'report.statement_of_accounts.report_soa'
    _description = 'Statement Of Accounts'

    @api.model
    def _get_report_values(self, docids, data=None):
        partner_id = data['partner_id']
        # soa_date = date(data['soa_date'])
        soa_date=datetime.strptime(data['soa_date'], '%Y-%m-%d').date()

        addtionalfilter=""
        if partner_id:
            addtionalfilter= ' and partner_id='+ str(partner_id)

        self._cr.execute("""select  distinct partner_id from account_move where  amount_residual<>0.00 and move_type='out_invoice' """ + addtionalfilter + """ and state='posted'""")

        model = self.env.context.get('active_model')
        company = self.env.user

        ids = (x['partner_id'] for x in self._cr.dictfetchall())
        line_items = {}
        am_due = {}
        objpartners = self.env['res.partner'].browse(ids)
        for rec_partner in objpartners:
            objam = self.env['account.move'].search([('partner_id','=', rec_partner.id),('amount_residual','<>',0.00),('move_type','=','out_invoice'),('state','=','posted')],order='date')
            for recmv in objam:
                duedays = (soa_date-recmv.invoice_date_due).days
                if duedays>0:
                    am_due[recmv.id]=str(duedays) + ' Days'
                else:
                    am_due[recmv.id] = '0 Days'

            line_items[rec_partner.id] = objam


        return {
            'doc_model': model,
            'data': data,
            'line_items' : line_items,
            'am_due': am_due,
            'soa_date': soa_date,
            'docs': objpartners,
            'o': company,
            'currdate': datetime.now(),
        }
