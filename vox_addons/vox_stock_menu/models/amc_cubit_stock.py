from odoo import models, fields, api, _
import datetime


class AMCMSPCubitStock(models.Model):
    _name = 'amc.cubit.stock'
    _order = 'date desc, id desc'
    _description = 'AMC/MSP Cubit stock model'

    # name = fields.Char('DN Name', required=True, copy=False, default=lambda self: _('New'))
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
    # notes = fields.Text('Notes')
    # task_id = fields.Many2one('project.task', 'Task')

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code(
    #             'amc.cubit.stock') or _('New')
    #     res = super(AMCMSPCubitStock, self).create(vals)
    #     return res


# class AMCMSPCubitStockLine(models.Model):
#     _name = 'amc.cubit.stock.line'
#     _descriptions = 'AMC/MSP Cubit Stock lines'
#
#     part_number = fields.Char('Part Number')
#     name = fields.Char('Part Description')
#     qty = fields.Float('Qty')
#     serial_num = fields.Char(string="Serial Number")
#     hs_code = fields.Char(string='Hs Code')
#     country_of_origin = fields.Char(string='Country Of Origin')
#     th_weight = fields.Char(string='Weight')
#     service_suk = fields.Char(string="Service SUK")
#     # sl_number = fields.Char('Serial Number')
#     begin_date = fields.Char(string="Contract Begin Date")
#     end_date = fields.Char(string="Contract End Date")
#     stock_id = fields.Many2one('cubit.stock', 'Cubit Stock')
#
#     deliv_sale_line_id = fields.Many2one('sale.order.line', 'Sale Line')
#     product_id = fields.Many2one('product.product', 'Product')
#     cubit_id = fields.Integer('Cubit ID')
#     sale_id = fields.Many2one('sale.order',related='stock_id.deliv_sale_id',store=True)
#     partner_id = fields.Many2one('res.partner', related='stock_id.partner_id', store=True)
#     lpo_number = fields.Char(related='stock_id.deliv_sale_id.lpo_number', store=True)
#     project_reference = fields.Char(related='stock_id.deliv_sale_id.client_order_ref')




