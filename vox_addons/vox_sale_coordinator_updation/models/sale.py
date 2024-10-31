from odoo import models, fields, api, _


class UpdatePartneruers(models.TransientModel):
    _name = 'update.partner.users'
    _description = 'Update Coordinator'


    # start_date = fields.Date('Start Period', required=True)
    # end_date = fields.Date('End Period', required=True)


    def update_partner_coordinator(self):
        # search_condition = [('date_order', '>=', self.start_date),('date_order', '<=', self.end_date),]
        partners = self.env['res.partner'].search([])
        for partner in partners:
            if partner.user_id:
                partner.sales_team_users = partner.user_id.sales_team_users.ids
                # partner.write({
                #     'sales_team_users': [(6, 0, partner.user_id.sales_team_users.ids)]
                #
                # })


    def update_renewal_team(self):
        uid = self.env.user
        sales_team = self.env['crm.team'].search([('sale_team_code', '=', 'renewal')])
        lists = []
        for rec in sales_team:
            lists += rec.member_ids.ids
        partners = self.env['res.partner'].search([])
        for partner in partners:
            partner.renewal_team_users = [(6, 0, lists)]


