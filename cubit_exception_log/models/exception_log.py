# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ExceptionLog(models.Model):
    _name = 'exception.log'
    _description = 'While Migrating any exception is comes, that exception stored here'
    _rec_name = 'related_exception'

    cubit_eight_id = fields.Integer('Cubit ID')
    error = fields.Char('Error')
    related_exception = fields.Char('Related Exception')
