from odoo import fields, models, api, _


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    level_one_employee_ids = fields.Many2many('res.users', 'level_one_rel', 'team_id', 'user_id', string='Level One Users')
    level_two_employee_ids = fields.Many2many('res.users', 'level_two_rel', 'team_id', 'user_id', string='Level Two Users')
    level_three_employee_ids = fields.Many2many('res.users', 'level_three_rel', 'team_id', 'user_id', string='Level Three Users')
    level_four_employee_ids = fields.Many2many('res.users', 'level_four_rel', 'team_id', 'user_id', string='Level four Users')
    level_five_employee_ids = fields.Many2many('res.users', 'level_five_rel', 'team_id', 'user_id', string='Level five Users')

    cubit_crm_team_id = fields.Integer(string="Cubit ID")
