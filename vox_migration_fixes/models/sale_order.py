from odoo import models, fields


class SaleOrderUpdate(models.Model):
    _inherit = 'sale.order'

    def update_sale_team(self):
        cr = self.env.cr
        team_id = self.env['crm.team'].search([('name', '=', 'Sales')]).id
        for lead in self:
            if lead.id:
                if lead.user_id:
                    query = '''select id, user_id from sale_order where id=%s'''%(lead.id)
                    cr.execute(query)
                    a = cr.dictfetchall()
                    print(a)
                    lead.write({'team_id': team_id, 'user_ids': [(6, 0, [a[0]['user_id']])],
                            'team_ids': [(6, 0, lead.team_id.ids)]})
                    print('successssssssssssssssssssssssssssssssssssssssssssss')
            # print(lead.user_id.name, 9999999999999999999999999999999999999999999999999999999999)
            # presale_list = []
            # team_list = []
            # for presale in lead.presale_id:
            #     # if presale.presales_person:
            #     #     presale_list.append(presale.presales_person.id if presale.presales_person else 0)
            #     if presale.presales_team.id not in team_list:
            #         if presale.presales_team:
            #             team_list.append(presale.presales_team.id if presale.presales_team else 0)

            # print(self.user_ids, 'User idaaassssssssssssssssssssssssss')

