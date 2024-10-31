
from odoo import fields, models

class AccountWzSOA(models.TransientModel):
    _name = "wizard.soa"
    _description = "Statement Of Accounts"

    soa_date = fields.Date(string='Date', default=lambda self: fields.Date.context_today(self).replace(day=1), required="1")

    partner_id = fields.Many2one('res.partner', string="Partner")


    def print_report(self):
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data = self.pre_print_report(data)
        return self.env.ref(
            'statement_of_accounts.action_report_soa').report_action(
            self, data=data)

    def pre_print_report(self, data):
        data['soa_date'] = self.soa_date
        data['partner_id']=self.partner_id.id
        return data