from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    team_code = fields.Selection([
        ('sales_team', 'Sales Team'),
        ('sales_coordinator', 'Sales Coordinator'),
        ('pre_sales', 'Pre sales'),
        ('post_sales', 'Post sales'),
        ('finance', 'Finance'),
        ('procurement', 'Procurement'),
        ('msp', 'MSP'),
        ('hr', 'HR'),
        ('marketing', 'Marketing'),
        ('project', 'Project'),

    ],
        string='code')
    sale_team_code = fields.Selection([
        ('amc', 'AMC'),
        ('msp', 'MSP'),
        ('renewal', 'Renewal'),
        ('cisco', 'Cisco'),
    ],string='Sale code')

    leader_ids = fields.Many2many('res.users', 'crm_team_user_rel', 'sale_team_id', 'team_lead_id', string="Team Lead",
                                  domain=lambda self: [
                                      ('groups_id', 'in', self.env.ref('vox_user_groups.group_sale_salesman_level_2_user').id),
                                      ('groups_id', 'in', self.env.ref('vox_user_groups.group_sale_salesman_level_1_user').id)
                                  ])
                        # domain=lambda self: [
                        #               ('groups_id', 'in', self.env.ref('sales_team.group_sale_salesman_all_leads').id),
                        #               ('groups_id', 'not in', self.env.ref('sales_team.group_sale_manager').id)
                        #           ])



    # @api.depends('is_membership_multi', 'member_ids')
    # def _compute_member_warning(self):
    #     for team in self:
    #         if team.member_ids:
    #             members = team.member_ids._origin
    #             for member in team.member_ids._origin:
    #                 if member.is_level_5 or member.is_level_4 or member.is_level_3:
    #                     if self.team_check_level_3_4_5(member)[0]:
    #                         if member.is_level_5 or member.is_level_4:
    #                             if member.report_mgr_id:
    #                                 if member.report_mgr_id not in members:
    #                                     raise ValidationError(
    #                                         "Reporting Head %s of user %s is not a member in this team." % (
    #                                             member.report_mgr_id.name, member.name))
    #
    #                             # if member.report_mgr_level_4:
    #                             #     if member.report_mgr_level_4 not in members:
    #                             #         raise ValidationError(
    #                             #             "Reporting Head %s of user %s is not a member in this team." % (
    #                             #             member.report_mgr_level_4.name, member.name))
    #                         # if member.is_level_4:
    #                         #     if member.report_mgr_level_3:
    #                         #         if member.report_mgr_level_3 not in members:
    #                         #             raise ValidationError(
    #                         #                 "Reporting Head %s of user %s is not a member in this team." % (
    #                         #                 member.report_mgr_level_3.name, member.name))
    #                     else:
    #                         raise ValidationError("The user %s is a member of team %s." % (
    #                             member.name, self.team_check_level_3_4_5(member)[1][0].crm_team_id.name))
    #     super(CrmTeam, self)._compute_member_warning()

    def team_check_level_3_4_5(self, member):
        other_memberships = self.env['crm.team.member'].search([
            ('crm_team_id', '!=', self._origin.id if self._origin.id else False),  # handle NewID
            ('user_id', '=', member.id)
        ])
        if other_memberships:
            return [False, other_memberships]
            # return False
        else:
            return [True, other_memberships]
            # return True

    def check_user_sale_access_level(self, member):
        if member.is_level_5:
            return "Level-5"
        elif member.is_level_4:
            return "Level-4"
        else:
            return "Level-3"

    def _get_default_team_id_new(self, user_id=None, domain=None):
        if user_id is None:
            user = self.env.user
        else:
            user = self.env['res.users'].sudo().browse(user_id)
        valid_cids = [False] + user.company_ids.ids
        team = self.env['crm.team']
        teams = self.env['crm.team'].search([
            ('company_id', 'in', valid_cids),
            '|', ('leader_ids', '=', user.id), ('member_ids', 'in', [user.id]),
        ])
        if teams and domain:
            team = teams.filtered_domain(domain)[:1]
        if not team:
            team = teams[:1]
        return team
