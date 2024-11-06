from odoo import models, fields, api, _
import datetime


class CubitStock(models.Model):
    _name = 'cubit.stock'
    _order = 'date desc, id desc'
    _description = 'Cubit stock model'

    date = fields.Date('Date', default=fields.Date.today())
    part_number = fields.Char('Part Number')
    name = fields.Char('Part Description')
    qty = fields.Float('Qty')
    serial_num = fields.Char(string="Serial Number")
    hs_code = fields.Char(string='Hs Code')
    country_of_origin = fields.Char(string='Country Of Origin')
    th_weight = fields.Char(string='Weight')
    service_suk = fields.Char(string="Service SUK")
    cubit_id = fields.Integer('Cubit ID')

    # name = fields.Char('DN Name', required=True, copy=False, default=lambda self: _('New'))
    # date = fields.Date('Date', default=fields.Date.today())
    # partner_id = fields.Many2one('res.partner', 'Customer')
    # lpo_reference = fields.Char('LPO Reference')
    # sale_number = fields.Char('Sale Order Number')
    # line_ids = fields.One2many('cubit.stock.line', 'stock_id', 'Lines')
    # customer_ref = fields.Char('Reference/Description')
    # deliv_sale_id = fields.Many2one('sale.order', 'Sale Order')
    # cubit_id = fields.Integer('Cubit ID')
    # notes = fields.Text('Notes')
    # task_id = fields.Many2one('project.task', 'Task')
    #
    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code(
    #             'cubit.stock') or _('New')
    #     res = super(CubitStock, self).create(vals)
    #     return res

