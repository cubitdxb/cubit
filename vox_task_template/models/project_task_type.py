from odoo import fields, api, models, _


class ProjectTaskStages(models.Model):
    _inherit = 'project.task.type'

    cubit_id = fields.Integer(string='Cubit_id')
