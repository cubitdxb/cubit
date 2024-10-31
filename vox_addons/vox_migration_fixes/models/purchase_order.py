from odoo import models, fields


class PurchaseOrderUpdate(models.Model):
    _inherit = 'project.task'

    def update_purchase_team(self):
        team_id = self.env['crm.team'].search([('name', '=', 'Procurement')])
        for lead in self:
            if lead.name in ['Purchase Order', 'PO to supplier']:
                lead.write({'team_id': team_id})
