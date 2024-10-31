import time
import datetime
from datetime import date, datetime
from odoo import api, models, _
from odoo.exceptions import UserError

class ReportCPartnerLedger(models.AbstractModel):
    _name = 'report.statement_of_accounts.report_partner_ledger'
    _description = 'Partner Ledger'

    @api.model
    def _get_report_values(self, docids, data=None):
        report_for= data['report_for']
        partner_id = data['partner_id']
        start_date = data['start_date']
        end_date = data['end_date']


        receivable_payable=" account_type in('liability_payable','asset_receivable') "
        if report_for=='receivable':
            receivable_payable = " account_type ='asset_receivable' "
        elif report_for=='payable':
            receivable_payable = " account_type ='liability_payable' "

        addtionalfilter=""
        if partner_id:
            addtionalfilter= ' and partner_id='+ str(partner_id)

        self._cr.execute("""select  distinct partner_id from account_move_line where account_id in (select id from account_account where """ + receivable_payable + """) and partner_id>0 and move_id in(select id from account_move where state='posted')
""" + addtionalfilter)
        

        model = self.env.context.get('active_model')
        company = self.env.user

        ids = (x['partner_id'] for x in self._cr.dictfetchall())
        line_items = {}
        aml_items = {}
        objpartners = self.env['res.partner'].browse(ids)

        for row in objpartners:
            balfwd=0.00
            sqlbalfwd="""select coalesce(sum(balance),0.00) as balanceforward from account_move_line 
            where  account_id in (select id from account_account where  """ + receivable_payable + """)  
            and partner_id>0 and move_id in(select id from account_move where state='posted')  and date<'"""+ str(start_date)+ """' and partner_id=""" + str(row.id)
            # raise UserError(sqlbalfwd)
            self._cr.execute(sqlbalfwd)
            objbalf=self._cr.dictfetchall()
            for recbalfwd in objbalf:
                balfwd+=recbalfwd['balanceforward']

            sqltrans = """select id  from account_move_line 
                        where  account_id in (select id from account_account where  """ + receivable_payable + """)  
                        and partner_id>0 and move_id in(select id from account_move where state='posted')  and date>='""" + str(
                start_date) + """' and date<='""" + str(end_date) + """' and partner_id=""" + str(row.id)
            self._cr.execute(sqltrans)
            mvlids = (mvl['id'] for mvl in self._cr.dictfetchall())
            objaml = self.env['account.move.line'].browse(mvlids).sorted(key=lambda a: (a.date, a.id))

            balfinal =balfwd
            for recbal in objaml:
                so_number =''
                objso = self.env['account.move.line'].search([('move_id','=',recbal.move_id.id),('sale_line_ids.id','>',0)],limit=1)
                for rec1 in  objso:
                    so_number=rec1.sale_line_ids.order_id.name
                balfinal+=recbal.balance
                aml_items[recbal.id]=so_number


            sub_items ={}

            sub_items['balfwd']=balfwd
            sub_items['balfinal']=balfinal
            sub_items['aml'] = objaml
            sub_items['aml_so']=aml_items
            line_items[row.id] = sub_items
        return {
            'doc_model': model,
            'data': data,
            'line_items' : line_items,
            'start_date': start_date,
            'end_date':end_date,
            'docs': objpartners,
            'o': company,
            'currdate': datetime.now(),
        }
