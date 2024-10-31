# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class vox_user_groups(models.Model):
#     _name = 'vox_user_groups.vox_user_groups'
#     _description = 'vox_user_groups.vox_user_groups'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
