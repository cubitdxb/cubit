
from odoo import fields, models

class WizardPartnerLedger(models.TransientModel):
    _name = "wizard.partner.ledger"
    _description = "Partner Ledger"

    start_date = fields.Date(string='Start Date', default=lambda self: fields.Date.context_today(self).replace(day=1), required="1")
    end_date = fields.Date(string="End Date", default=lambda self: fields.Date.context_today(self), required="1")
    report_for = fields.Selection([('receivable','Receivable'),('payable','Payable'),('receivable_payable','Receivable and Payable')], default="receivable", string="Type")
    partner_id = fields.Many2one('res.partner', string="Partner")


    def print_report(self):
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data = self.pre_print_report(data)
        return self.env.ref(
            'statement_of_accounts.action_report_partner_ledger').report_action(
            self, data=data)

    def pre_print_report(self, data):
        data['report_for'] = self.report_for
        data['start_date'] = self.start_date
        data['end_date'] = self.end_date
        data['partner_id']=self.partner_id.id
        return data
