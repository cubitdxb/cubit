# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Stage(models.Model):
    _inherit = "crm.stage"

    is_lead = fields.Boolean('Is Lead Stage?')
    is_lost = fields.Boolean('Is Lost?')
    is_opportunity = fields.Boolean('Is Opportunity Stage?')
    is_import = fields.Boolean('Is Import?')
    is_sale_order = fields.Boolean('Is sale Order?')
    cubit_crm_stage_id = fields.Integer(string="Cubit ID")
    # stages_readonly = fields.Boolean(string="Conditional Stages",default=False)

#add cubit Id
class UtmSource(models.Model):
    _inherit = "utm.source"

    cubit_source_id = fields.Integer(string="Cubit ID")

class Tag(models.Model):
    _inherit = "crm.tag"

    cubit_tag_id = fields.Integer(string="Cubit ID")

# class CrmTeam(models.Model):
#     _inherit = "crm.team"
#
#     cubit_crm_team_id = fields.Integer(string="Cubit ID")


