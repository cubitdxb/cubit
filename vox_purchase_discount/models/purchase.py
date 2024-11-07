# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


# class PurchaseAdvancePaymentInv(models.TransientModel):
#     _inherit = "purchase.advance.payment.inv"
#
#     def _prepare_invoice_values(self, order, name, amount, so_line):
#         res = super()._prepare_invoice_values(order, name, amount, so_line)
#         if order.discount_amount:
#             res["discount_amount"] = order.discount_amount
#         return res

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('order_line', 'order_line.taxes_id', 'discount_distribution_type')
    def _compute_line_taxes(self):
        print("compute_line_taxes")
        dis_taxes = []
        for rec in self:
            for line in rec.order_line:
                dis_taxes.append(line.taxes_id.ids[0]) if line.taxes_id else dis_taxes
            rec.line_taxes_ids = list(set(dis_taxes))

    discount_distribution_type = fields.Selection([('against_item', 'Item Wise'), ('against_tax', 'Tax Wise')],
                                                  default='against_item', string="Discount Type")
    distribution_tax_ids = fields.Many2many('account.tax', string="Tax")
    line_taxes_ids = fields.Many2many('account.tax', string="Line Taxes", compute='_compute_line_taxes')

    # def _prepare_invoice(self):
    #     res = super()._prepare_invoice()
    #     if self.discount_amount:
    #         res["discount_amount"] = self.discount_amount
    #     return res

    @api.depends('order_line.price_total', 'discount_amount',
                 'order_line',
                 'order_line.price_unit',
                 'order_line.taxes_id',
                 'order_line.product_qty',
                 'distribution_tax_ids',
                 'discount_distribution_type'
                 )
    def _amount_all_wrapper(self):
        line_obj = self.env['purchase.order.line']
        if self:
            for order in self:
                total_vat_on_net_taxable = total_net_taxable = val = val1 = val3 = global_disc = 0.0
                qty_price_total = 0.0
                tax_wise_total = 0.0
                for tax_qty_price in order.order_line:
                    if tax_qty_price.taxes_id and tax_qty_price.taxes_id.ids[0] in order.distribution_tax_ids.ids:
                        tax_wise_total += (tax_qty_price.product_uom_qty * tax_qty_price.price_unit)
                for qty_price in order.order_line:
                    qty_price_total += (qty_price.product_qty * qty_price.price_unit)
                if not 0.0 <= order.discount_amount <= qty_price_total:
                    raise ValidationError(_('Enter proper discount'))
                for line in order.order_line:
                    tax_on_net_taxable = tax = 0.0
                    val1 += line.total_price
                    # val1 += line.price_subtotal
                    qty = line_obj._calc_line_quantity(line)
                    if line.taxes_id:
                        for c in line.taxes_id.compute_all(line.price_unit, order.currency_id, qty, False,
                                                           line.order_id.partner_id)['taxes']:
                            tax += c.get('amount', 0.0)
                    val += tax
                    # val3 += line.total_cost
                    # if order.discount_distribution_type == 'against_item':
                    #     line.discount_distribution = (order.discount_amount /
                    #                                   qty_price_total) * (line.product_qty * line.price_unit)
                    # elif order.distribution_tax_ids and line.taxes_id and line.taxes_id.ids[
                    #     0] in order.distribution_tax_ids.ids:
                    #     line.discount_distribution = (order.discount_amount /
                    #                                   tax_wise_total) * (line.product_qty * line.price_unit)
                    # else:
                    #     line.discount_distribution = 0.0

                    # To avoid division by zero
                    if order.discount_distribution_type == 'against_item':
                        if qty_price_total != 0:
                            line.discount_distribution = (order.discount_amount / qty_price_total) * (
                                        line.product_qty * line.price_unit)
                        else:
                            line.discount_distribution = 0.0
                    elif order.distribution_tax_ids and line.taxes_id and line.taxes_id.ids[
                        0] in order.distribution_tax_ids.ids:
                        if tax_wise_total != 0:
                            line.discount_distribution = (order.discount_amount / tax_wise_total) * (
                                        line.product_qty * line.price_unit)
                        else:
                            line.discount_distribution = 0.0
                    else:
                        line.discount_distribution = 0.0


                    line.discount = (line.discount_distribution / (
                            line.product_qty * line.price_unit) * 100.0) if line.discount_distribution else 0.0
                    line.net_taxable = (line.product_qty * line.price_unit) - line.discount_distribution
                    line.price_subtotal = (line.product_qty * line.price_unit) - line.discount_distribution
                    if line.taxes_id:
                        for c in line.taxes_id.compute_all(line.price_subtotal, order.currency_id, 1, False,
                                                           line.order_id.partner_id)['taxes']:
                            tax_on_net_taxable += c.get('amount', 0.0)
                        line.price_tax = tax_on_net_taxable
                    line.price_total = line.price_subtotal + line.price_tax
                    total_vat_on_net_taxable += line.price_tax
                    total_net_taxable += line.net_taxable
                    # total_net_taxable += line.price_subtotal
                # order_line = line_obj.search([
                #     ('order_id', '=', order.id),
                #     ('global_discount_line', '=', True),
                #     ('active', '=', False)
                # ])

                # for line in order_line:
                #     if line.global_discount_line:
                #         tax = 0.0
                #         val1 += line.price_subtotal
                #         qty = line_obj._calc_line_quantity(line)
                #         if line.taxes_id:
                #             for c in line.taxes_id.compute_all(line.price_unit, order.currency_id, qty, False,
                #                                              line.order_id.partner_id)['taxes']:
                #                 tax += c.get('amount', 0.0)
                #             # tax_amount = 5
                #         val += tax
                #         global_disc += line.price_subtotal

                val2 = (val1 + val)
                # amount_tax = round(val,6)
                # amount_tax = round((val1 * tax_amount / 100) if tax_amount else 0, 6)
                # amount_tax = round((tax_amount) if tax_amount else 0, 6)
                amount_gross = round(val1, 6)
                amount_untaxed = round((val1 - global_disc), 6)
                # amount_total = round(val2,6)
                # amount_total = round((val1 + amount_tax), 6)
                order.update({
                    'amount_untaxed': total_net_taxable,
                    'amount_gross': amount_gross,
                    'amount_total': total_net_taxable + total_vat_on_net_taxable,
                    'amount_tax': total_vat_on_net_taxable,
                })

        # for order in self:
        #     amount_untaxed = amount_tax = 0.0
        #     for line in order.order_line:
        #         line._compute_amount()
        #         amount_untaxed += line.price_subtotal
        #         amount_tax += line.price_tax
        #     currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id
        #     order.update({
        #         'amount_untaxed': currency.round(amount_untaxed),
        #         'amount_tax': currency.round(amount_tax),
        #         'discount_amount': order.discount_amount,
        #         'amount_total': amount_untaxed + amount_tax - order.discount_amount,
        #
        #     })

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')],
                                     string='Global Discount type', readonly=True, default='amount')
    amount_untaxed = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True,
                                  string='Untaxed Amount', help="The amount without tax.", track_visibility='always')
    amount_total = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True, string='Total',
                                help="The total amount.")
    amount_tax = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True, string='Taxes',
                              help="The tax amount.")
    amount_gross = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True, string='Gross Amount',
                                help="The amount after discount without tax.", track_visibility='always')

    # amount_untaxed = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True,
    #                               string='Untaxed Amount', help="The amount without tax.",
    #                               track_visibility='always')
    # amount_gross = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True, string='Gross Amount',
    #                             help="The amount after discount without tax.", track_visibility='always')
    # amount_total = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True, string='Total',
    #                             help="The total amount.")
    # amount_tax = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True, string='Taxes',
    #                           help="The tax amount.")

    # order_line = fields.One2many(domain=[('global_discount_line', '=', False)])
    #
    # discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')],
    #                                  string='Global Discount type', readonly=True, default='amount')
    # # discount_rate = fields.Float('Global Discount Rate', digits_compute=dp.get_precision('Account'),
    # #                             readonly=True, states={'draft': [('readonly', False)]})
    # amount_untaxed = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True,
    #                               digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
    #                               help="The amount without tax.", track_visibility='always')
    # amount_total = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True,
    #                             digits_compute=dp.get_precision('Account'), string='Total',
    #                             help="The total amount.")
    # amount_tax = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True,
    #                           digits_compute=dp.get_precision('Account'), string='Taxes', help="The tax amount.")

    # @api.model
    # def create(self, values):
    #     order = super(PurchaseOrder, self).create(values)
    #     order.generate_global_discount()
    #     return order
    #
    # def write(self, values):
    #     res = super(PurchaseOrder, self).write(values)
    #     self.generate_global_discount()
    #     self.onchange_add_tax()
    #     return res
    #
    # @api.model
    # def existing_global_discountline(self, values):
    #     order_line = self.env['purchase.order.line']
    #     # order_line = (order_line | self.order_line)
    #     exists = order_line.search(
    #         [
    #             ('order_id', '=', values.get('order_id')),
    #             ('product_id', '=', values.get('product_id')),
    #             ('name', '=', values.get('name')),
    #             ('global_discount_line', '=', True),
    #             '|',
    #             ('active', '=', True),
    #             ('active', '=', False)
    #         ]
    #     )
    #     equal = order_line.search(
    #         [
    #             ('order_id', '=', values.get('order_id')),
    #             ('product_id', '=', values.get('product_id')),
    #             ('name', '=', values.get('name')),
    #             ('price_unit', '=', values.get('price_unit')),
    #             ('product_qty', '=', values.get('product_qty')),
    #             ('global_discount_line', '=', True),
    #             '|',
    #             ('active', '=', True),
    #             ('active', '=', False)
    #         ]
    #     )
    #     return exists, equal, order_line
    #
    # def generate_global_discount(self):
    #     discount_calc = self.env.context.get('discount_calc', False)
    #     if not discount_calc and discount_calc != None:
    #         for order in self:
    #             amount_untaxed = order.amount_untaxed
    #             sequence = sum(line.sequence for line in order.order_line)
    #             sequence += 10
    #             global_discount_product = self.env.ref('vox_task_template.global_discount_product_0', False)
    #
    #             # global_discount_product = self.env.ref('cw_cubit_discount.global_discount_product_0', False)
    #             purchse_tax_5 = self.env.ref('vox_purchase_discount.purchse_tax_5', False)
    #             # taxes_id = [(5)]
    #             taxes_id = [(6, 0, [])]
    #             if purchse_tax_5 and order.amount_tax > 0.0:
    #                 taxes_id = [(6, 0, [purchse_tax_5.id])]
    #             discount_order_line_values = {
    #                 'order_id': order.id,
    #                 'sequence': sequence,
    #                 'global_discount_line': True,
    #                 'name': global_discount_product.name,
    #                 'product_id': global_discount_product.id,
    #                 # 'product_uom': global_discount_product.uom_id.id,
    #                 'product_qty': 1,
    #                 'taxes_id': taxes_id,
    #                 'active': False,
    #             }
    #             global_discount = 0.0
    #             # if order.discount_type and order.discount_rate and order.discount_rate != 0.0:
    #             if order.discount_type and order.discount_amount and order.discount_amount != 0.0:
    #                 if order.discount_type == 'percent':
    #                     # global_discount = (amount_untaxed * order.discount_rate)/100
    #                     global_discount = (amount_untaxed * order.discount_amount) / 100
    #                 elif order.discount_type == 'amount':
    #                     # global_discount = order.discount_rate
    #                     global_discount = order.discount_amount
    #                 price_unit = -global_discount
    #                 discount_order_line_values.update({'price_unit': price_unit})
    #             else:
    #                 price_unit = 0.0
    #                 discount_order_line_values.update({'price_unit': price_unit})
    #                 # order.with_context(ctx).write({'discount_amount': 0.0})
    #             # exists, equal = self.order_line.with_context(ctx).existing_global_discountline(discount_order_line_values)
    #             exists, equal, order_line = self.with_context(discount_calc=True).existing_global_discountline(
    #                 discount_order_line_values)
    #             if exists and not equal:
    #                 exists.with_context(discount_calc=True).write(discount_order_line_values)
    #             elif not exists and not equal:
    #                 # self.order_line.with_context(ctx).create(discount_order_line_values)
    #                 order_line.with_context(discount_calc=True).create(discount_order_line_values)
    #     return True


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_qty', 'price_unit')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = rec.price_unit * rec.product_qty

    global_discount_line = fields.Boolean(string="Line is a global discount line", default=False)
    active = fields.Boolean(string="Active", default=True)
    discount_distribution = fields.Float(string="Discount Distribution")
    net_taxable = fields.Float(string="Net Taxable")
    discount = fields.Float(string="Discount")
    total_price = fields.Float(string="Total Price", compute='_compute_total_price')

    def _calc_line_quantity(self, line):
        return line.product_qty
