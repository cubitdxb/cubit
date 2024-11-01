
# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID
from odoo.exceptions import ValidationError



class SaleOrderImport(models.Model):
    _inherit = "sale.order.import"


    def prepare_sale_requset(self,lines):
        res = super().prepare_sale_requset(lines)
        if res.get('res_model', False) == 'sale.order':
            sale_value = self.env['sale.order'].browse(res.get('res_id', False))
            for obj in sale_value:
                teams = [t.id for lead in obj.crm_lead_id for t in lead.team_ids if lead.team_ids]
                users = [t.id for lead in obj.crm_lead_id for t in lead.user_ids if lead.user_ids]
                # obj.user_ids = [(4, sale_ids.id) for sale_ids in obj.crm_lead_id],
                obj.team_ids = [(6, 0, teams)]
                obj.user_ids = [(6, 0, users)]
        return res
