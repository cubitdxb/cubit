# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Sale_line_brand(models.Model):
    _inherit = "sale.line.category"

    category_selection = fields.Selection([('msp', 'MSP'), ('amc', 'AMC')], string='Category')


class Sale_line_brand(models.Model):
    _inherit = "sale.line.brand"

    cisco_brand = fields.Boolean(string='Cisco')


class PresaleInformation(models.Model):
    _inherit = "presale.information"

    presales_team = fields.Many2one('crm.team', string="Presales Team", required="1",
                                    domain=[('team_code', '=', 'pre_sales')])
    presale_boolean = fields.Boolean(string='Presale Visibility',compute='presale_information',default='presale_information')
    sales_boolean = fields.Boolean(string='Sale Visibility',default='presale_information')

    @api.model
    def default_get(self, fields_list):
        # only 'code' state is supported for cron job so set it as default
        self.presale_information()
        return super(PresaleInformation, self).default_get(fields_list)

    @api.depends_context('uid','presale_information')
    @api.depends('presales_team', 'presale_department_id', 'sale_order_id', 'crm_lead_id', 'presales_person',
                 'crm_lead_id.user_id','sale_order_id.user_id','crm_lead_id.presales_required','crm_lead_id.user_ids',
                 'crm_lead_id.team_ids','crm_lead_id.team_id','crm_lead_id.presale_id','sale_order_id.presale_id')
    def presale_information(self):
        uid = self.env.user
        sales_team = self.env['crm.team'].search([('team_code', '=', 'sales_team')])
        lists = []
        for rec in sales_team:
            lists+=rec.leader_ids.ids
            lists+=rec.member_ids.ids
            # lists.append(rec.member_ids.ids)
        for sale in self:
            # if self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id:
            if self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id:
                sale.presale_boolean = False
                sale.sales_boolean = False
            elif self.env.user.has_group('vox_user_groups.group_presale_users') and not uid.id in lists :
                sale.presale_boolean = True
                sale.sales_boolean = False
            # if uid in lists:
            #     sale.sales_boolean = True
            elif self.env.user.has_group('vox_user_groups.group_presale_users') and uid.id in lists:
                sale.presale_boolean = False
                sale.sales_boolean = False
            else:
                if uid.id in lists:
                    sale.sales_boolean = True
                    sale.presale_boolean = False
                else:
                    sale.sales_boolean = True
                    sale.presale_boolean = True
                    # raise ValidationError("Invalid Sales Team")
                    # sale.presale_boolean = True
                # sale.sales_boolean = False

    def write(self, vals):
        activity_type_approval_id = self.env.ref('sales_team.team_sales_department').id
        if self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id:
            res = super().write(vals)
            return res
        if self.env.user.has_group('vox_user_groups.group_presale_users'):
            if vals.get('available_date', False) or vals.get('done', False) or vals.get('presale_status_id', False) \
                    or vals.get('comments', False):
                return super().write(vals)
            # else:
            #     raise ValidationError("Invalid Sales Team")
        return super().write(vals)

    @api.onchange('presale_department_id')
    def change_product(self):
        self.presale_information()
        lst = []
        for i in self:
            if i.presale_department_id:
                i.presales_person = False
                pre_sales_department = self.env['presale.department'].search([('id', '=', i.presale_department_id.id)])
                for presale in pre_sales_department:
                    lst += presale.sales_team_users.ids

        # pre_sales_team = self.env['crm.team'].search([('team_code', '=', 'pre_sales')])
        # for rec in pre_sales_team:
        #     lst1 = rec.leader_ids.ids
        #     lst2 = rec.member_ids.ids
        #     lst = lst1 + lst2
        return {'domain': {'presales_person': [('id', 'in', lst)]}}

    # def _onchange_presales_person(self):
    #     # domain = [('id', '=', -1)]
    #     domain = []
    #     lists = []
    #     pre_sales_team = self.env['crm.team'].search([('team_code', '=', 'pre_sales')])
    #     for rec in pre_sales_team:
    #         list1 = rec.leader_ids.ids
    #         list2 = rec.member_ids.ids
    #         lists = list1+list2
    #     if lists:
    #         domain = [('id', 'in', lists)]
    #         return domain
    #     return domain
    #
    # presales_person = fields.Many2one('res.users', string="Presales Person", required="1",domain=_onchange_presales_person)

# class PresaleInformation(models.Model):
#     _inherit = "presale.information"
#
#     def _get_employee(self):
#         domain = [('id', '=', -1)]
#         lists = []
#         pre_sales_team = self.env['crm.team'].search([('team_code', '=', 'pre_sales')])
#         for each in pre_sales_team:
#             lists.append(each.employee_id.id)
#         if lists:
#             domain = [('id', 'in', lists)]
#             return domain
#         return domain
#
# def _onchange_presales_person(self):
#     pre_sales_team = self.env['crm.team'].search([('team_code', '=', 'pre_sales')])
#     lists = []
#     for rec in pre_sales_team:
#         lists.append(rec.leader_ids.ids)
#         lists.append(rec.member_ids.ids)
#     return [('id', 'in', lists)]
#
#     presales_person = fields.Many2one('res.users', string="Presales Person", required="1",domain=_onchange_presales_person)
