from odoo import models, fields, api, _
import datetime
from odoo.exceptions import UserError


class TaskDelivery(models.Model):
    _name = 'task.delivery'
    _order = 'date desc, id desc'
    _description = 'task delivery model'

    name = fields.Char('Name', required=True, copy=False, default=lambda self: _('New'))
    date = fields.Date('Date', default=fields.Date.today())
    partner_id = fields.Many2one('res.partner', 'Customer')
    task_id = fields.Many2one('project.task', 'Task')
    notes = fields.Text('Notes')
    line_ids = fields.One2many('task.delivery.line', 'delivery_id', 'Lines')
    customer_ref = fields.Char('Reference/Description')
    sale_number = fields.Char('Sale Order Number')
    deliv_sale_id = fields.Many2one('sale.order', 'Sale Order')
    cubit_id = fields.Integer('Cubit ID')

    def write(self, vals):
        members = self.env['crm.team'].search([('team_code', '=', 'procurement')]).mapped('member_ids').ids
        if self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id or self.env.uid in members:
            res = super().write(vals)
            return res
        else:
            raise UserError(_("You can't Edit Delivery records, Please Contact Administrator"))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'task.delivery') or _('New')
        res = super(TaskDelivery, self).create(vals)
        return res


class TaskDeliveryLine(models.Model):
    _name = 'task.delivery.line'
    _descriptions = 'Task Delivery lines'

    deliv_sale_line_id = fields.Many2one('sale.order.line', 'Sale Line')
    product_id = fields.Many2one('product.product', 'Product')
    part_number = fields.Char('Part Number')
    sl_number = fields.Char('Serial Number')
    name = fields.Char('Name')
    qty = fields.Float('Qty')
    delivery_id = fields.Many2one('task.delivery', 'Delivery')
    cubit_id = fields.Integer('Cubit ID')
    sale_id = fields.Many2one('sale.order', related='delivery_id.deliv_sale_id', store=True)
    partner_id = fields.Many2one('res.partner', related='delivery_id.partner_id', store=True)
    lpo_number = fields.Char(related='delivery_id.deliv_sale_id.lpo_number', store=True)
    project_reference = fields.Char(related='delivery_id.deliv_sale_id.client_order_ref')

    hs_code = fields.Char(string='Hs Code')
    country_of_origin = fields.Char(string='Country Of Origin')
    th_weight = fields.Char(string='Weight')


class PurchaseTaskDeliveryLine(models.Model):
    _name = 'purchase.task.delivery.line'
    _descriptions = 'Purchase Delivery lines'

    # @api.onchange('sl_num', 'purchase_date', 'exp_date')
    # def onchange_deliv(self):
    #     values = {'received': False}
    #     for order in self:
    #         if order.sl_num or order.purchase_date or order.exp_date:
    #             values.update({'received': True})
    #     return {'value': values}

    def _get_line_numbers(self):
        number = 1
        for order in self:
            order.sequence = number
            number += 1

    sequence = fields.Integer(string='Sl No.', compute='_get_line_numbers')
    name = fields.Char('Product Description')
    sl_num = fields.Char(string='Serial No')
    part_number = fields.Char('Product Part Number')
    sale_layout_cat_id = fields.Many2one('sale_layout.category', string='Section')
    purchase_date = fields.Date('Purchase Date')
    exp_date = fields.Date('Expiry Date')
    received = fields.Boolean('Received')
    type = fields.Selection([('warranty', 'Warranty'), ('guaranty', 'Guaranty')], 'Type', default='warranty')
    price = fields.Float(string="Price")
    purchase_partner_id = fields.Many2one('res.partner', string='Supplier', readonly=True, store=True)
    task_id = fields.Many2one('project.task')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True, store=True)
    purchase_id = fields.Many2one('purchase.order', 'Line')

    exp_date_from = fields.Date(string="Expiry Date From")
    exp_date_to = fields.Date(string="Expiry Date To")
    purchase_date_from = fields.Date(string="Purchase Date From")
    purchase_date_to = fields.Date(string="Purchase Date To")
    sale_partner_id = fields.Many2one('res.partner', string='Customer', readonly=True, store=True)
    purchase_order_line_id = fields.Many2one('purchase.order.line', 'Purchase Order Line')
    comment = fields.Text('Note')
    cubit_id = fields.Integer(string="Cubit ID")

