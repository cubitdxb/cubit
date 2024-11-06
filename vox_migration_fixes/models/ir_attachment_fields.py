# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class IrAttachmentInherit(models.Model):
    _inherit = 'ir.attachment'

    cubit_id = fields.Integer('Cubit ID')
    cubit_res_id = fields.Integer('Cubit Res ID')
