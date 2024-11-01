# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class AssignUserManager(models.TransientModel):
    _name = 'assign.users.manager'
    _description = 'Assign Report Managers'

    @api.model
    def default_get(self, fields):
        res = super(AssignUserManager, self).default_get(fields)
        if self.env.context.get('active_model') == 'res.users' and self.env.context.get('active_id'):
            user = self.env['res.users'].browse(self.env.context.get('active_id'))
            if user:
                groups = [self.env.ref('vox_user_groups.group_sale_salesman_level_3_user').id,
                          self.env.ref('vox_user_groups.group_sale_salesman_level_1_user').id,
                          self.env.ref('vox_user_groups.group_sale_salesman_level_2_user').id]
                for group in groups:
                    if group in user.groups_id.ids:
                        raise ValidationError("Reporting Lead is not required for %s" % user.name)

        return res

    def _get_user_doamin(self):
        if self.env.context.get('active_model') == 'res.users' and self.env.context.get('active_id'):
            user = self.env['res.users'].browse(self.env.context.get('active_id'))
            if user:
                if user.is_level_4:
                    users = self.env['res.users'].search([('is_level_3', '=', True)])
                    return str([('id', 'in', users.ids)])
                if user.is_level_5:
                    users = self.env['res.users'].search([('is_level_4', '=', True)])
                    return str([('id', 'in', users.ids)])
                else:
                    return False
            else:
                return False
        else:
            return False

    user_id = fields.Many2one('res.users', string="Reporting Lead", domain=_get_user_doamin)

    def add_report_manager(self):
        if self.env.context.get('active_model') == 'res.users' and self.env.context.get('active_id'):
            user = self.env['res.users'].browse(self.env.context.get('active_id'))
            # if self.report_mgr_id:
            other_memberships = self.env['crm.team.member'].search(
                [('user_id', '=', user.id), ('crm_team_id', '!=', False)])
            if other_memberships:
                if other_memberships[0].crm_team_id:
                    if self.user_id:
                        if self.user_id not in other_memberships.crm_team_id.member_ids:
                            raise ValidationError(
                                "Reporting Lead - %s is not a member of team %s. Please add new reporting lead to the team" % (
                                self.user_id.name, other_memberships[0].crm_team_id.name))

            if user:
                user.report_mgr_id = self.user_id.id
            else:
                user.report_mgr_id = False
