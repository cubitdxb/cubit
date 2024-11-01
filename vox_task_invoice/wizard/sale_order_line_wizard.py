# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError


class SaleOrderLineEdit(models.TransientModel):
    _name = 'wiz.sale_order_line_edit'
    _description = 'Sale order lines edit'

    name = fields.Char()
    line_ids = fields.One2many(
        comodel_name='wiz.sale_order_line_edit.lines',
        inverse_name='wizard_id',
        string='Lines')
    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Task')
    select_all = fields.Boolean('Line Select All')

    @api.onchange('select_all')
    def _onchange_select_all(self):
        for lines in self:
            if lines.select_all == True:
                for line in lines.line_ids:
                    line.write({'is_check': True})
            else:
                for line in lines.line_ids:
                    line.write({'is_check': False})

    def _create_invoices_vals(self):
        invoice_lines = []
        sum_dis_distrubution = 0.0
        for line in self.line_ids.filtered(lambda x: x.is_check):
            sum_dis_distrubution += line.discount_distribution
            vals = {
                'name': line.name,
                'price_unit': line.unit_price,
                'quantity': line.product_uom_qty,
                'product_uom_id': line.product_uom.id,
                'tax_ids': [(6, 0, line.tax_id.ids)],
                'sale_layout_cat_id': line.sale_layout_cat_id.id,
                'part_number': line.part_number,
                'service_suk': line.service_suk,
                'serial_num': line.serial_num,
                'begin_date': line.begin_date,
                'end_date': line.end_date,
                'discount_distribution': line.discount_distribution,
                'net_taxable': line.net_taxable,
                'discount':line.discount,
            }
            invoice_lines.append((0, 0, vals))
            if line.product_uom_qty > line.line_id.product_uom_qty - line.line_id.done_qty_wizard:
                raise ValidationError("you cannot create invoice with quantity greater than ordered quantity")
            line.line_id.done_qty_wizard = line.line_id.done_qty_wizard + line.product_uom_qty
            if line.line_id.product_uom_qty == line.line_id.done_qty_wizard:
                line.line_id.is_line_invoiced = True

        invoiced_sale_line = self.task_id.sale_id.order_line.filtered(lambda x: x.is_line_invoiced).mapped('is_line_invoiced')
        total_sale_line = self.task_id.sale_id.order_line.filtered(lambda x: not x.is_downpayment).mapped('id')
        if len(invoiced_sale_line) == len(total_sale_line):
            self.task_id.is_regular_invoice = True
        if invoice_lines:
            for order in self.task_id.sale_id:
                create_moves = self.env['account.move'].create({
                    'project_id': self.task_id.project_id.id,
                    'task_id': self.task_id.id,
                    'move_type': 'out_invoice',
                    'invoice_origin': order.name,
                    'invoice_user_id': order.user_id.id,
                    'partner_id': order.partner_invoice_id.id,
                    'currency_id': order.pricelist_id.currency_id.id,
                    'invoice_line_ids': invoice_lines,
                    'invoice_payment_term_id': order.payment_term_id.id,
                    'add_information': order.add_information,
                    'narration': order.note,
                    'lpo_number': order.lpo_number,
                    'payment_term': order.payment_term,
                    'dis_amount': sum_dis_distrubution,
                })
                if create_moves:
                    amount = create_moves.amount_total
                    total_inv = 0
                    for invoices in self.env['account.move'].search(
                            [('task_id.sale_id', '=', order.id), ('state', '!=', 'cancel'),('move_type', 'in', ('out_invoice','out_refund')),('id','!=',create_moves.id)]):
                        invoices.amount_total = round(invoices.amount_total,2)
                        total_inv += invoices.amount_total
                    amount = round(amount, 2)
                    total_inv += amount
                    if total_inv > (order.amount_total + 1):
                        create_moves.unlink()
                        raise UserError(_('You are trying to invoice more than total price'))

        return

    def create_invoices(self):
        self._create_invoices_vals()

        self.task_id.sale_id.sudo().task_invoice_ids = self.task_id.invoice_ids

        return {'type': 'ir.actions.act_window_close'}

class SaleOrderLineEditLines(models.TransientModel):
    _name = 'wiz.sale_order_line_edit.lines'
    _description = 'Lines of sale order lines edit'

    wizard_id = fields.Many2one(
        comodel_name='wiz.sale_order_line_edit',
        string='Wizard')
    line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale order line')
    name = fields.Text(string='Description')
    part_number = fields.Char(string="Part Number")
    sl_no = fields.Integer(string="Sl#")
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id)
    unit_price = fields.Monetary(string="Unit Price", currency_field='currency_id',)
    product_uom_qty = fields.Float(string="Quantity")
    price_included = fields.Monetary(string="Subtotal", currency_field='currency_id',)
    tax_total = fields.Monetary(string="Tax", currency_field='currency_id',)
    price_total_val = fields.Monetary(string="Total", currency_field='currency_id',)
    is_check = fields.Boolean(string="Check")
    tax_id = fields.Many2many('account.tax',string="Tax")
    sale_layout_cat_id = fields.Many2one('sale_layout.category', string='Section')
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure')
    is_line_invoiced = fields.Boolean(string="Line Invoiced")
    service_suk = fields.Char(string="Service SUK")
    serial_num = fields.Char(string="Serial Number")
    begin_date = fields.Char(string="Begin Date")
    end_date = fields.Char(string="End Date")
    discount_distribution = fields.Float(string="Discount Distribution")
    net_taxable = fields.Float(string="Net Taxable")
    discount = fields.Float(string="Discount")

