from odoo import models, fields, api, _
from datetime import timedelta
from datetime import date
from dateutil.relativedelta import relativedelta


class SaleOrderEmailNotification(models.Model):
    _inherit = 'sale.order'

    @api.model
    def run_amc_msp_renewal_email_reminder(self):
        today = fields.Date.context_today(self)
        template = self.env.ref('vox_task_template.mail_template_to_amc_msp_renewal')
        orders = self.env['sale.order'].search([])
        l1_users = self.env.ref('vox_user_groups.group_sale_salesman_level_1_user').users.partner_id.ids
        l2_users = self.env.ref('vox_user_groups.group_sale_salesman_level_2_user').users.partner_id.ids
        l3_users = self.env.ref('vox_user_groups.group_sale_salesman_level_3_user').users.partner_id.ids
        l4_users = self.env.ref('vox_user_groups.group_sale_salesman_level_4_user').users.partner_id.ids
        if l3_users and l4_users:
            users = l3_users + l4_users
        elif l3_users and not l4_users:
            users = l3_users
        elif l4_users and not l3_users:
            users = l4_users
        else:
            users = []
        sales_team_users = self.env['crm.team'].search([('team_code', '=', 'sales_team'), ('sale_team_code', '=', False)]).mapped('member_ids').partner_id.ids
        # print(list(set((users))), 'usersssssssssssssssssssssss')
        # print(sales_team_users, 'sales team users')
        total_users = list((set(users).intersection(set(sales_team_users))).difference(set(l1_users).union(set(l2_users))))
        # print(total_users, 'total users')
        for rec in orders:
            for line in rec.order_line:
                if line.end_date:
                    first_month_prior = line.end_date - relativedelta(months=1)
                    second_month_prior = line.end_date - relativedelta(months=2)
                    third_month_prior = line.end_date - relativedelta(months=3)
                    if today in [first_month_prior, second_month_prior,
                                 third_month_prior] and line.line_category_id.name in ['AMC', 'MSP', 'Renewal']:
                        email_values = {'email_to': line.salesman_id.email, 'recipient_ids': total_users}
                        if template:
                            template.send_mail(rec.id, force_send=True, email_values=email_values)
                if rec.commitment_date:
                    renewal_end_date = rec.commitment_date + relativedelta(months=int(float(line.service_duration)) if line.service_duration else 0)
                    # print(renewal_end_date, 'renewal_end_date')
                    if renewal_end_date:
                        renewal_first_month_prior = renewal_end_date - relativedelta(months=1)
                        renewal_second_month_prior = renewal_end_date - relativedelta(months=2)
                        renewal_third_month_prior = renewal_end_date - relativedelta(months=3)
                        if today in [renewal_first_month_prior, renewal_second_month_prior,
                                     renewal_third_month_prior] and line.line_category_id.name in ['Smartnet', 'Software', 'License']:
                            email_values = {'email_to': line.salesman_id.email, 'recipient_ids': total_users}
                            if template:
                                template.send_mail(rec.id, force_send=True, email_values=email_values)
