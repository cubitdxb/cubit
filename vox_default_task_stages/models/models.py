# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = "project.project"

    def _get_default_type_common(self):
        ids = self.env["project.task.type"].search([("task_default", "=", True)])
        return ids

    type_ids = fields.Many2many(default=lambda self: self._get_default_type_common())

class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    task_default = fields.Boolean(string="Default for New Projects")