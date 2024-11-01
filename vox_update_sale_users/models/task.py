from odoo import models, fields, api, _


class UpdateSaleuers(models.TransientModel):
    _name = 'update.sale.users'
    _description = 'Update sale users'

    start_date = fields.Date('Start Period', required=True)
    end_date = fields.Date('End Period', required=True)

    def update_sale_users(self):
        search_condition = [('date_order', '>=', self.start_date), ('date_order', '<=', self.end_date), ]
        sale_orders = self.env['sale.order'].search(search_condition)
        for sale in sale_orders:
            presale_list = []
            team_list = []
            if sale.crm_lead_id:
                for crm_lead in sale.crm_lead_id:
                    for presale in crm_lead.presale_id:
                        if presale.presales_person:
                            presale_list.append(presale.presales_person.id if presale.presales_person else 0)
                        if presale.presales_team.id not in team_list:
                            if presale.presales_team:
                                team_list.append(presale.presales_team.id if presale.presales_team else 0)

            sale.write({
                'user_ids': [(6, 0, sale.user_id.ids + presale_list + sale.user_id.sales_team_users.ids)],
                'team_ids': [(6, 0, sale.team_id.ids + team_list)]

            })

            # sale.user_ids = [(6, 0, sale.user_id.ids + presale_list + sale.user_id.sales_team_users.ids)]
            # sale.team_ids = [(6, 0, sale.team_id.ids + team_list)]

    def update_coordinator_renewal_users(self):
        search_condition = [('date_order', '>=', self.start_date), ('date_order', '<=', self.end_date), ]
        sale_orders = self.env['sale.order'].search(search_condition)
        for sale in sale_orders:
            team_list = []
            presale_list = []
            renewal_sales_team = self.env['crm.team'].search([('sale_team_code', '=', 'renewal')])
            lists = []
            for rec in renewal_sales_team:
                lists += rec.member_ids.ids
            if sale.user_id:
                if sale.user_id.sales_team_users:
                    sales_team = self.env['crm.team'].search(['|', ('sale_team_code', '=', 'renewal'),
                                                              ('team_code', 'in', ['sales_team', 'sales_coordinator'])])
                    team_list = team_list + sales_team.ids
                    for cor in sale.user_id.sales_team_users:
                        presale_list.append(cor.id)
                    presale_list = presale_list + lists

                else:
                    sales_team = self.env['crm.team'].search(
                        ['|', ('sale_team_code', '=', 'renewal'), ('team_code', 'in', ['sales_team'])])
                    team_list = team_list + sales_team.ids
                    for cor in sale.user_id.sales_team_users:
                        presale_list.append(cor.id)
                    presale_list = presale_list + lists

            if sale.crm_lead_id:
                for crm_lead in sale.crm_lead_id:
                    for presale in crm_lead.presale_id:
                        if presale.presales_person:
                            presale_list.append(presale.presales_person.id if presale.presales_person else 0)
                        if presale.presales_team.id not in team_list:
                            if presale.presales_team:
                                team_list.append(presale.presales_team.id if presale.presales_team else 0)

            sale.write({
                'user_ids': [(6, 0, sale.user_id.ids + presale_list + sale.user_id.sales_team_users.ids)],
                'team_ids': [(6, 0, sale.team_id.ids + team_list)]

            })

    def crm_update_sale_coordinator_renewal_users(self):
        leads = self.env['crm.lead'].search([])
        for sale in leads:
            team_list = []
            presale_list = []
            renewal_sales_team = self.env['crm.team'].search([('sale_team_code', '=', 'renewal')])
            lists = []
            for rec in renewal_sales_team:
                lists += rec.member_ids.ids
            if sale.user_id:
                if sale.user_id.sales_team_users:
                    sales_team = self.env['crm.team'].search(['|', ('sale_team_code', '=', 'renewal'),
                                                              ('team_code', 'in', ['sales_team', 'sales_coordinator'])])
                    team_list = team_list + sales_team.ids
                    for cor in sale.user_id.sales_team_users:
                        presale_list.append(cor.id)
                    presale_list = presale_list + lists

                else:
                    sales_team = self.env['crm.team'].search(
                        ['|', ('sale_team_code', '=', 'renewal'), ('team_code', 'in', ['sales_team'])])
                    team_list = team_list + sales_team.ids
                    for cor in sale.user_id.sales_team_users:
                        presale_list.append(cor.id)
                    presale_list = presale_list + lists

            for presale in sale.presale_id:
                if presale.presales_person:
                    presale_list.append(presale.presales_person.id if presale.presales_person else 0)
                if presale.presales_team.id not in team_list:
                    if presale.presales_team:
                        team_list.append(presale.presales_team.id if presale.presales_team else 0)

            sale.write({
                'user_ids': [(6, 0, sale.user_id.ids + presale_list + sale.user_id.sales_team_users.ids)],
                'team_ids': [(6, 0, sale.team_id.ids + team_list)]

            })
