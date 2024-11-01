from odoo import models, fields, api,_


class statement_Report(models.TransientModel):
    _name = "statement.account.report.wizard"
    _description = " statement Of Account Report"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)

    partner_id = fields.Many2one(
        'res.partner', string='Partner', readonly=True)

    display_name = fields.Char(string="Display Name")

    @api.model
    def _prepare_default_get(self, order):
        default = {
            'partner_id': order.id,
            'date_start': order.date_start,
            'date_end': order.date_end,
            'display_name': order.display_name,
        }
        return default

    @api.model
    def default_get(self, fields):
        res = super(statement_Report, self).default_get(fields)
        assert self._context.get('active_model') == 'res.partner', \
            'active_model should be res.partner'
        order = self.env['res.partner'].browse(self._context.get('active_id'))
        default = self._prepare_default_get(order)
        res.update(default)
        return res

    def _prepare_update_so(self):
        self.ensure_one()
        return {
            'date_start': self.date_start,
            'date_end': self.date_end,
        }

    def print_statment_report(self):
        self.ensure_one()
        vals = self._prepare_update_so()
        self.partner_id.write(vals)
        # self.partner_id.open_action_followup()

        return {
            'name': _("Overdue Payments for %s", self.display_name),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [[self.env.ref('account_followup.customer_statements_form_view').id, 'form']],
            'res_model': 'res.partner',
            'res_id': self.partner_id.id,
        }

    # def print_report(self):
    #     # res_ids = records['ids'] if 'ids' in records else records.ids  # records come from either JS or server.action
    #     action = self.env.ref('account_followup.action_report_followup').report_action(res_ids)
    #     if action.get('type') == 'ir.actions.report':
    #         for partner in self.env['res.partner'].browse(res_ids):
    #             partner.message_post(body=_('Follow-up letter printed'))
    #     return action

    # def open_action_followup(self):
    #     self.ensure_one()

