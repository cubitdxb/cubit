# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



class ResUsers(models.Model):
    _inherit = 'res.users'


    report_mgr_id = fields.Many2one('res.users', string="Reporting Lead")
    # is_level_4 = fields.Boolean(string="User Level-4")
    # is_level_3 = fields.Boolean(string="User Level-3")
    # is_level_5 = fields.Boolean(string="User Level-5")

    is_level_4 = fields.Boolean(string="Is a Level-4 user", compute='compute_level_4_5', store=True)
    is_level_5 = fields.Boolean(string="Is Level-5 user", compute='compute_level_4_5', store=True)
    is_level_3 = fields.Boolean(string="Is Level-3 user", compute='compute_level_4_5', store=True)

    def _team_domain(self):
        team_list = []
        sales_team = self.env['crm.team'].search([('team_code','=','sales_coordinator')])
        for teams in sales_team:
            team_list+=teams.member_ids.ids
        return [('id', 'in', team_list)]

    sales_team_users = fields.Many2many('res.users','sales_coordinator_rel', 'user_id', 'id', string='Sales Coordinator',
                                        domain=_team_domain)


    @api.depends('groups_id')
    def compute_level_4_5(self):
        for user in self:
            user = user.sudo()
            user.is_level_5 = False
            user.is_level_4 = False
            user.is_level_3 = False
            # test = self.env.ref('sales_team.group_sale_salesman_all_leads')
            test = self.env.ref('vox_user_groups.group_sale_salesman_level_2_user')
            # if not self.env.ref('sales_team.group_sale_manager') in user.groups_id and not self.env.ref(
            #         'sales_team.group_sale_salesman_all_leads') in user.groups_id:
            if not self.env.ref('vox_user_groups.group_sale_salesman_level_1_user') in user.groups_id and not self.env.ref(
                    'vox_user_groups.group_sale_salesman_level_2_user') in user.groups_id:
                if not self.env.ref('vox_user_groups.group_sale_salesman_level_3_user') in user.groups_id:
                    if not self.env.ref('vox_user_groups.group_sale_salesman_level_4_user') in user.groups_id:
                        # if self.env.ref('sales_team.group_sale_salesman') in user.groups_id:
                        if self.env.ref('vox_user_groups.group_sale_salesman_level_5_user') in user.groups_id:
                            user.is_level_5 = True
                    else:
                        user.is_level_4 = True
                else:
                    user.is_level_3 = True

    # @api.onchange('report_mgr_id')
    # def onchange_report_manager_4(self):
    #     if self.report_mgr_id:
    #         other_memberships = self.env['crm.team.member'].search(
    #             [('user_id', '=', self.id), ('crm_team_id', '!=', False)])
    #         if other_memberships:
    #             raise ValidationError(
    #                 _("%s is a member of team %s. Please remove the user from the team and change the report lead" % self.name,
    #                   other_memberships[0].crm_team_id.name))



    # @api.depends('crm_team_member_ids.active')
    def _compute_crm_team_ids(self):
        super(ResUsers, self)._compute_crm_team_ids()
        for user in self:
            # lead_group = self.env.ref('sales_team.group_sale_salesman_all_leads')
            # ad_group = self.env.ref('sales_team.group_sale_manager')
            lead_group = self.env.ref('vox_user_groups.group_sale_salesman_level_2_user')
            ad_group = self.env.ref('vox_user_groups.group_sale_salesman_level_1_user')
            if lead_group in user.groups_id and ad_group not in user.groups_id:
                teams = self.env['crm.team'].search([('leader_ids', '=', user.id)])
                user.crm_team_ids = user.crm_team_member_ids.crm_team_id + teams


