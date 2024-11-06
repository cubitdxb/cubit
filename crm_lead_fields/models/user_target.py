# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class MonthlyTargetDetails(models.Model):
    _name = 'monthly.target.det'
    _description = 'Monthly Target Details'

    years = fields.Selection([(str(num), str(num)) for num in range(2010, datetime.now().year + 2)], 'Year')
    month = fields.Selection([('january', 'January'),
                              ('february', 'February'),
                              ('march', 'March'),
                              ('april', 'April'),
                              ('may', 'May'),
                              ('june', 'June'),
                              ('july', 'July'),
                              ('august', 'August'),
                              ('september', 'September'),
                              ('october', 'October'),
                              ('november', 'November'),
                              ('december', 'December')], string="Month")
    target = fields.Float(string="Target")
    user_id = fields.Many2one('res.users', string="User")
    achieved_target = fields.Float(string="Target Achieved", compute='find_target_achieved',  store=True)
    target_deficit = fields.Float(string="Target Deficit", compute='get_target_deficit', store=True)
    target_start = fields.Date(string="Target Date", compute='get_target_deficit',  store=True)

    current_year = fields.Boolean(string="Current Year", compute='get_target_deficit', store=True)
    current_month = fields.Boolean(string="Current Month", compute='get_target_deficit', store=True)
    active = fields.Boolean('Active', default=True, tracking=True)
    lead_id = fields.Many2one('crm.lead',string="Lead/Oppurtunity")

    @api.constrains('years', 'month')
    def validate_monthly_target(self):
        for vals in self:
            if vals.month and vals.years:
                dat = self.search(
                    [('month', '=', vals.month), ('years', '=', vals.years), ('user_id', '=', vals.user_id._origin.id),
                     ('id', '!=', vals.id)])
                if dat:
                    raise ValidationError(
                        "Target for %s, %s for %s is already set." % (vals.month, vals.years, vals.user_id.name))

    @api.onchange('years', 'month')
    def onchange_find_target_date(self):
        for vals in self:
            if vals.month and vals.years:
                dat = self.search(
                    [('month', '=', vals.month), ('years', '=', vals.years), ('user_id', '=', vals.user_id._origin.id)])
                if dat:
                    raise UserError(
                        "Target for %s, %s for %s is already set." % (vals.month, vals.years, vals.user_id.name))

    @api.depends('user_id', 'years', 'month')
    def find_target_achieved(self):
        total_so_amount = 0

        for vals in self:
            sale_order = self.env['sale.order'].search([('user_id', '=', vals.user_id.id), ('state', '=', 'sale')])
            vals.target_start = False
            vals.current_year = False
            vals.current_month = False
            if vals.years and vals.month:
                for order in sale_order:
                    if order.date_order.strftime('%B').lower() == vals.month:
                        if order.date_order.strftime('%Y') == vals.years:
                            total_so_amount += order.amount_total
                vals.achieved_target = total_so_amount
                date_time_str = "01/%s/%s" % (vals.month.title(), vals.years)
                vals.target_start = datetime.strptime(date_time_str, '%d/%B/%Y')
                if vals.target_start.year == datetime.now().year:
                    vals.current_year = True
                if vals.target_start.month == datetime.now().month:
                    vals.current_month = True

    @api.depends('target', 'achieved_target')
    def get_target_deficit(self):
        for vals in self:
            if vals.target and vals.achieved_target:
                vals.target_deficit = vals.target - vals.achieved_target
            else:
                vals.target_deficit = 0


