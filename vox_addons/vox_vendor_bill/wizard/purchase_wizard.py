# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError


class PurchaseOrderLineEdit(models.TransientModel):
    _name = 'wiz.purchase_order_line_edit'
    _description = 'Purchase order lines edit'

    name = fields.Char()
    line_ids = fields.One2many(
        comodel_name='wiz.purchase_order_line_edit.lines',
        inverse_name='wizard_id',
        string='Lines')
    purchase_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase')

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
                'purchase_line_id': line.line_id.id,
                'discount_distribution': line.discount_distribution,
                'net_taxable': line.net_taxable,
                'discount': line.discount,
            }
            invoice_lines.append((0, 0, vals))
            if line.product_uom_qty > line.line_id.product_uom_qty - line.line_id.done_qty_wizard:
                raise ValidationError("you cannot create invoice with quantity greater than ordered quantity")
            line.line_id.done_qty_wizard = line.line_id.done_qty_wizard + line.product_uom_qty
            if line.line_id.product_uom_qty == line.line_id.done_qty_wizard:
                line.line_id.is_line_invoiced = True

        invoiced_purchase_line = self.purchase_id.order_line.filtered(lambda x: x.is_line_invoiced).mapped('is_line_invoiced')
        total_purchase_line = self.purchase_id.order_line.filtered(lambda x: not x.is_downpayment).mapped('id')
        # if len(invoiced_purchase_line) == len(total_purchase_line):
        #     self.purchase_id.is_regular_invoice = True
        if invoice_lines:
            for order in self.purchase_id:
                create_moves = self.env['account.move'].create({
                    'project_id': order.project_id.id,
                    'task_id': order.task_id.id,
                    'purchase_id': order.id,
                    'move_type': 'in_invoice',
                    'invoice_origin': order.name,
                    'invoice_user_id': order.user_id.id,
                    'partner_id': order.partner_id.id,
                    # 'currency_id': order.pricelist_id.currency_id.id,
                    'invoice_line_ids': invoice_lines,
                    'invoice_payment_term_id': order.payment_term_id.id,
                    # 'add_information': order.add_information,
                    'narration': order.notes,
                    'purchase_bill_id': order.id,
                    'payment_term': order.payment_term,
                    'dis_amount': sum_dis_distrubution,
                    'discount_distribution_type': order.discount_distribution_type,
                    'line_taxes_ids': order.line_taxes_ids.ids,
                    'distribution_tax_ids': order.distribution_tax_ids.ids,
                })

                if create_moves:
                    amount = create_moves.amount_total
                    total_inv = 0
                    for invoices in self.env['account.move'].search(
                            [('purchase_bill_id', '=', order.id), ('state', '!=', 'cancel'),('move_type', 'in', ('in_invoice','in_refund')),('id','!=',create_moves.id)]):
                        invoices.amount_total = round(invoices.amount_total, 2)
                        total_inv += invoices.amount_total
                    amount = round(amount, 2)
                    total_inv += amount
                    if total_inv > (order.amount_total+1):
                        create_moves.unlink()
                        raise UserError(_('You are trying to invoice more than total price'))



        return

    def create_invoices(self):
        self._create_invoices_vals()
        # for order in self.purchase_id.sudo():
        #     amount = order.amount_total
        #     total_inv = 0
        #     for invoices in self.env['account.move'].search([('purchase_bill_id', '=', order.id),('state','!=','cancel')]):
        #         total_inv += invoices.amount_total
        #     # total_inv += amount
        #     if total_inv > order.amount_total:
        #         raise UserError(_('You are trying to invoice more than total price'))
        return {'type': 'ir.actions.act_window_close'}

class SaleOrderLineEditLines(models.TransientModel):
    _name = 'wiz.purchase_order_line_edit.lines'
    _description = 'Lines of Purchase order lines edit'

    wizard_id = fields.Many2one(
        comodel_name='wiz.purchase_order_line_edit',
        string='Wizard')
    line_id = fields.Many2one(
        comodel_name='purchase.order.line',
        string='Purchase order line')
    name = fields.Text(string='Description')
    sale_layout_cat_id = fields.Many2one('sale_layout.category', string='Section')
    product_uom_qty = fields.Float(string="Quantity")
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure')
    unit_price = fields.Monetary(string="Unit Price",)
    part_number = fields.Char(string="Part Number")
    tax_id = fields.Many2many('account.tax',string="Tax")
    # sl_no = fields.Integer(string="Sl#")
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id)
    # price_included = fields.Monetary(string="Subtotal", currency_field='currency_id',)
    # tax_total = fields.Monetary(string="Tax", currency_field='currency_id',)
    # price_total_val = fields.Monetary(string="Total", currency_field='currency_id',)
    is_check = fields.Boolean(string="Check")
    is_line_invoiced = fields.Boolean(string="Line Invoiced")
    discount_distribution = fields.Float(string="Discount Distribution")
    net_taxable = fields.Float(string="Net Taxable")
    discount = fields.Float(string="Discount")

