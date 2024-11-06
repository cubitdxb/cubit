# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    amount_gross = fields.Float(store=True, readonly=True, string='Gross Amount',
                                help="The amount after discount without tax.", track_visibility='always')

    @api.depends('order_line.invoice_lines.move_id')
    def _compute_invoice(self):
        # for order in self:
        #     invoices = order.mapped('order_line.invoice_lines.move_id')
        #     order.invoice_ids = invoices
        #     order.invoice_count = len(invoices)

        for order in self:
            purchase_moves = self.env['account.move'].sudo().search(
                [('purchase_bill_id', '=', order.id)])
            default_invoices = order.mapped('order_line.invoice_lines.move_id')
            lt_purchase_invoice = [(4, lt_move_line.id) for lt_move_line in default_invoices]
            purchase_invoice = [(4, move_line.id) for move_line in purchase_moves]
            exist_moves = [(4, existing_orders.id) for existing_orders in order.invoice_ids]
            all_invoices = list(set(exist_moves + purchase_invoice + lt_purchase_invoice))
            order.invoice_ids = all_invoices
            order.invoice_count = len(order.invoice_ids)



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    is_downpayment = fields.Boolean(
            string="Is a down payment", help="Down payments are made when creating invoices from a sales order."
            " They are not copied when duplicating a sales order.")

    is_line_invoiced = fields.Boolean(string="Line Invoiced")
    done_qty_wizard = fields.Float(string="Done Qty Wizard")

    # untaxed_amount_to_invoice = fields.Monetary("Untaxed Amount To Invoice", compute='_compute_untaxed_amount_to_invoice', store=True)
    #
    # @api.depends('state', 'price_reduce', 'product_id', 'untaxed_amount_invoiced', 'qty_delivered', 'product_uom_qty')
    # def _compute_untaxed_amount_to_invoice(self):
    #     """ Total of remaining amount to invoice on the sale order line (taxes excl.) as
    #             total_sol - amount already invoiced
    #         where Total_sol depends on the invoice policy of the product.
    #
    #         Note: Draft invoice are ignored on purpose, the 'to invoice' amount should
    #         come only from the SO lines.
    #     """
    #     for line in self:
    #         amount_to_invoice = 0.0
    #         if line.state in ['purchase', 'done']:
    #             # Note: do not use price_subtotal field as it returns zero when the ordered quantity is
    #             # zero. It causes problem for expense line (e.i.: ordered qty = 0, deli qty = 4,
    #             # price_unit = 20 ; subtotal is zero), but when you can invoice the line, you see an
    #             # amount and not zero. Since we compute untaxed amount, we can use directly the price
    #             # reduce (to include discount) without using `compute_all()` method on taxes.
    #             price_subtotal = 0.0
    #             uom_qty_to_consider = line.qty_delivered if line.product_id.invoice_policy == 'delivery' else line.product_uom_qty
    #             price_reduce = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #             price_subtotal = price_reduce * uom_qty_to_consider
    #             if len(line.taxes_id.filtered(lambda tax: tax.price_include)) > 0:
    #                 # As included taxes are not excluded from the computed subtotal, `compute_all()` method
    #                 # has to be called to retrieve the subtotal without them.
    #                 # `price_reduce_taxexcl` cannot be used as it is computed from `price_subtotal` field. (see upper Note)
    #                 price_subtotal = line.taxes_id.compute_all(
    #                     price_reduce,
    #                     currency=line.order_id.currency_id,
    #                     quantity=uom_qty_to_consider,
    #                     product=line.product_id,
    #                     partner=line.order_id.partner_shipping_id)['total_excluded']
    #             inv_lines = line._get_invoice_lines()
    #             if any(inv_lines.mapped(lambda l: l.discount != line.discount)):
    #                 # In case of re-invoicing with different discount we try to calculate manually the
    #                 # remaining amount to invoice
    #                 amount = 0
    #                 for l in inv_lines:
    #                     if len(l.tax_ids.filtered(lambda tax: tax.price_include)) > 0:
    #                         amount += l.tax_ids.compute_all(
    #                             l.currency_id._convert(l.price_unit, line.currency_id, line.company_id,
    #                                                    l.date or fields.Date.today(), round=False) * l.quantity)[
    #                             'total_excluded']
    #                     else:
    #                         amount += l.currency_id._convert(l.price_unit, line.currency_id, line.company_id,
    #                                                          l.date or fields.Date.today(), round=False) * l.quantity
    #
    #                 amount_to_invoice = max(price_subtotal - amount, 0)
    #             else:
    #                 amount_to_invoice = price_subtotal - line.untaxed_amount_invoiced
    #
    #         line.untaxed_amount_to_invoice = amount_to_invoice



class AccountMove(models.Model):
    _inherit = "account.move"


    purchase_bill_id = fields.Many2one('purchase.order', string='Source Document')


    def action_post(self):
        #inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        res = super(AccountMove, self).action_post()
        line_ids = self.mapped('line_ids').filtered(lambda line: line.purchase_line_id.is_downpayment)
        for line in line_ids:
            try:
                line.purchase_line_id.taxes_id = line.tax_ids
                # if all(line.tax_ids.mapped('price_include')):
                #     line.purchase_line_id.price_unit = line.price_unit
                # else:
                #     #To keep positive amount on the sale order and to have the right price for the invoice
                #     #We need the - before our untaxed_amount_to_invoice
                #     line.purchase_line_id.price_unit = -line.purchase_line_id.untaxed_amount_to_invoice
            except UserError:
                # a UserError here means the SO was locked, which prevents changing the taxes
                # just ignore the error - this is a nice to have feature and should not be blocking
                pass
        return res
