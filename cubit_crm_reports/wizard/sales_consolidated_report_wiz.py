# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError


class SalesConsolidatedWizard(models.TransientModel):
    _name='sales.consolidated.wizard'
    _description='Sales Consolidated Report'
    
    @api.constrains('date_from','date_to')
    @api.onchange('date_from','date_to')
    def date_validation(self):
        for self in self:
            date_from = self.date_from
            date_to = self.date_to

            if date_to and date_from and date_to<date_from:
                warning = { 'title': ("Warning"), 'message': ('From Date should be before than the End date'), }
                raise UserError(_('From Date should be before than the End date!!'))
    
    
    date_from = fields.Date(string="Create Date From")
    date_to = fields.Date(string="Create Date To")
    
    
    def action_print_xls(self):
        self.ensure_one()
        data = self.read()
        data = {
        'form' : data,
        }
        return self.env.ref('cubit_crm_reports.action_sales_consolidated_report_xls').sudo().report_action(self,data=data)
    
    
    
