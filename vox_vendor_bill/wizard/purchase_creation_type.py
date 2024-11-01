# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseAdvancePaymentInv(models.TransientModel):
    _name = "purchase.advance.payment.inv"
    _description = "Purchase Advance Payment Invoice"

    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))

    @api.model
    def _default_product_id(self):
        product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
        return self.env['product.product'].browse(int(product_id)).exists()

    @api.model
    def _default_deposit_account_id(self):
        return self._default_product_id()._get_product_accounts()['income']

    @api.model
    def _default_deposit_taxes_id(self):
        return self._default_product_id().taxes_id

    @api.model
    def _default_has_down_payment(self):
        if self._context.get('active_model') == 'purchase.order' and self._context.get('active_id', False):
            purchase_order = self.env['purchase.order'].browse(self._context.get('active_id'))
            return purchase_order.order_line.filtered(
                lambda purchase_order_line: purchase_order_line.is_downpayment
            )

        return False



    @api.model
    def _default_currency_id(self):
        if self._context.get('active_model') == 'purchase.order' and self._context.get('active_id', False):
            purchase_order = self.env['purchase.order'].browse(self._context.get('active_id'))
            return purchase_order.currency_id

    advance_payment_method = fields.Selection([
        ('delivered', 'Regular Bill'),
        ('percentage', 'Down payment (percentage)'),
        ('fixed', 'Down payment (fixed amount)'),
        ('some_order_lines', 'Some Order Lines')
        ], string='Create Invoice', default='delivered', required=True,
        help="A standard invoice is issued with all the order lines ready for invoicing, \
        according to their invoicing policy (based on ordered or delivered quantity).")
    deduct_down_payments = fields.Boolean('Deduct down payments', default=True)
    has_down_payments = fields.Boolean('Has down payments', default=_default_has_down_payment, readonly=True)
    product_id = fields.Many2one('product.product', string='Down Payment Product', domain=[('type', '=', 'service')],
        default=_default_product_id)
    count = fields.Integer(default=_count, string='Order Count')
    amount = fields.Float('Down Payment Amount', digits='Account', help="The percentage of amount to be invoiced in advance, taxes excluded.")
    currency_id = fields.Many2one('res.currency', string='Currency', default=_default_currency_id)
    fixed_amount = fields.Monetary('Down Payment Amount (Fixed)', help="The fixed amount to be invoiced in advance, taxes excluded.")
    deposit_account_id = fields.Many2one("account.account", string="Income Account", domain=[('deprecated', '=', False)],
        help="Account used for deposits", default=_default_deposit_account_id)
    deposit_taxes_id = fields.Many2many("account.tax", string="Customer Taxes", help="Taxes used for deposits", default=_default_deposit_taxes_id)

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        if self.advance_payment_method == 'percentage':
            amount = self.default_get(['amount']).get('amount')
            return {'value': {'amount': amount}}
        return {}

    def _prepare_invoice_values(self, order, name, amount, so_line):
        # partner_invoice_id = order.partner_id.address_get(['invoice'])['invoice']
        partner_bank_id = order.partner_id.commercial_partner_id.bank_ids.filtered_domain(
            ['|', ('company_id', '=', False), ('company_id', '=', order.company_id.id)])[:1]
        invoice_tax = self.env['account.tax'].sudo().search([('invoice_tax', '=', True), ('type_tax_use', '=', 'purchase')],
                                                            limit=1)
        invoice_vals = {
            'project_id': order.project_id.id,
            'task_id': order.task_id.id,
            'ref': order.partner_ref,
            'move_type': 'in_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.notes,
            'partner_id': order.partner_id.id,
            'purchase_id':order.id,
            'purchase_bill_id': order.id,
            # 'partner_id': partner_invoice_id,
            'fiscal_position_id': (order.fiscal_position_id or order.fiscal_position_id.get_fiscal_position(order.partner_id.id)).id,
            # 'currency_id': order.currency_id.id,
            'payment_reference': order.partner_ref,
            'invoice_payment_term_id': order.payment_term_id.id,
            'payment_term': order.payment_term,
            # 'partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
            'partner_bank_id': partner_bank_id,
            # 'discount_amount': order.discount_amount,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,
                'tax_ids': [(6, 0, so_line.taxes_id.ids)],
                # 'tax_ids': [(6, 0, invoice_tax.ids)],
                # 'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'sale_layout_cat_id': so_line.sale_layout_cat_id.id,
                'part_number': so_line.part_number,
                'purchase_line_id': so_line.id,
                'discount_distribution': self.discount_distribution,
                'discount': self.discount,
                'net_taxable': self.net_taxable,
            })],
        }

        return invoice_vals

    def _get_advance_details(self, order):
        context = {'lang': order.partner_id.lang}
        if self.advance_payment_method == 'percentage':
            if all(self.product_id.taxes_id.mapped('price_include')):
                # for down payment percentage option select Total taxable amount instead of Total amount (Including VAT)
                amount = order.amount_gross * self.amount / 100

            else:
                amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount)
        # if self.advance_payment_method == 'percentage':
        #     #For percentage type always takes untaxed amount. Taxes can add separately in draft bill .
        #     # amount = (order.amount_untaxed - order.discount_amount)* self.amount / 100
        #     # amount = order.amount_total- order.discount_amount) * self.amount / 100
        #     amount = order.amount_untaxed * self.amount / 100
        #     name = _("Down payment of %s%%") % (self.amount)
        else:
            amount = self.fixed_amount
            name = _('Down Payment')
        del context

        return amount, name


    def _create_invoice(self, order, so_line, amount):
        total_inv = 0
        for invoices in self.env['account.move'].search(
                [('purchase_bill_id', '=', order.id), ('state', '!=', 'cancel'),('move_type', 'in', ('in_invoice', 'in_refund'))]):
            invoices.amount_total = round(invoices.amount_total, 2)
            total_inv += invoices.amount_total
            #2
        amount = round(amount, 2)
        total_inv += amount
        if total_inv > (order.amount_total+1):
            raise UserError(_('You are trying to invoice more than total price'))
        if (self.advance_payment_method == 'percentage' and self.amount <= 0.00) or (self.advance_payment_method == 'fixed' and self.fixed_amount <= 0.00):
            raise UserError(_('The value of the down payment amount must be positive.'))

        amount, name = self._get_advance_details(order)

        invoice_vals = self._prepare_invoice_values(order, name, amount, so_line)

        if order.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id

        invoice = self.env['account.move'].with_company(order.company_id)\
            .sudo().create(invoice_vals).with_user(self.env.uid)
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice

    def _prepare_so_line(self, order, analytic_tag_ids, tax_ids, amount):
        context = {'lang': order.partner_id.lang}
        so_values = {
            'name': _('Down Payment: %s') % (time.strftime('%m %Y'),),
            'price_unit': amount,
            'product_qty': 0.0,
            'order_id': order.id,
            # 'discount': 0.0,
            'product_uom': self.product_id.uom_id.id,
            'product_id': self.product_id.id,
            'analytic_tag_ids': analytic_tag_ids,
            'taxes_id': [(6, 0, tax_ids)],
            'is_downpayment': True,
            'sequence': order.order_line and order.order_line[-1].sequence + 1 or 10,
        }
        del context
        return so_values

    def _create_invoices_vals(self):
        purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids', []))
        vat = purchase_orders.amount_tax
        invoice_lines = []
        total_price = 0.0
        for line in purchase_orders.order_line.filtered(lambda x: not x.is_line_invoiced):
            if line.is_downpayment:
                total_price = total_price + line.price_unit * -1
            else:
                total_price = total_price + line.price_unit * line.product_qty

        total_price = total_price + vat
        if total_price < 0:
            for line in purchase_orders.order_line.filtered(lambda x: not x.is_line_invoiced and not x.is_cancel_down_payment):
                if line.is_downpayment:
                    vals = {
                        'name': line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom.id,
                        'tax_ids': [(6, 0, line.taxes_id.ids)],
                        'sale_layout_cat_id': line.sale_layout_cat_id.id,
                        'part_number': line.part_number,
                        'purchase_line_id': line.id,
                    }

                else:

                    vals = {
                        'name': line.name,
                        'price_unit': line.price_unit,
                        'quantity': -(line.product_uom_qty-line.done_qty_wizard),
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom.id,
                        'tax_ids': [(6, 0, line.taxes_id.ids)],
                        'sale_layout_cat_id': line.sale_layout_cat_id.id,
                        'part_number': line.part_number,
                        'purchase_line_id': line.id,
                        'discount_distribution': line.discount_distribution,
                        'discount': line.discount,
                        'net_taxable': line.net_taxable,

                    }
                invoice_lines.append((0, 0, vals))



            for order in purchase_orders:
                create_moves = self.env['account.move'].create({
                    # 'ref': self.client_order_ref,
                    'project_id': order.project_id.id,
                    'task_id': order.task_id.id,
                    # 'discount_amount': order.discount_amount,
                    # 'project_id': task.project_id.id,
                    # 'task_id': self.env.context.get('active_id'),
                    'move_type': 'in_invoice',
                    'invoice_origin': order.name,
                    'invoice_user_id': order.user_id.id,
                    'partner_id': order.partner_id.id,
                    # 'currency_id': order.currency_id.id,
                    'invoice_line_ids': invoice_lines,
                    'invoice_payment_term_id': order.payment_term_id.id,
                    'payment_term': order.payment_term,
                    'narration':order.notes,
                    'purchase_id': order.id,
                    'purchase_bill_id': order.id,
                    'dis_amount': order.discount_amount,
                })

                if create_moves:
                    amount = create_moves.amount_total
                    total_inv = 0
                    for invoices in self.env['account.move'].search(
                            [('purchase_bill_id', '=', order.id), ('state', '!=', 'cancel'),('move_type', 'in', ('in_invoice','in_refund')),('id','!=',create_moves.id)]):
                        total_inv += invoices.amount_total
                    total_inv += amount
                    # if total_inv > order.amount_total:
                    #     create_moves.unlink()
                    #     raise UserError(_('You are trying to invoice more than total price'))


        else:

            for line in purchase_orders.order_line.filtered(lambda x: not x.is_line_invoiced and not x.is_cancel_down_payment):
                invoice_tax = self.env['account.tax'].sudo().search(
                    [('invoice_tax', '=', True), ('type_tax_use', '=', 'purchase')],
                    limit=1)
                if line.is_downpayment:
                    vals = {
                        'name': line.name,
                        'price_unit': line.price_unit,
                        'quantity': -1,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom.id,
                        'tax_ids': [(6, 0, line.taxes_id.ids)],
                        # 'tax_ids': [(6, 0, invoice_tax.ids)],
                        'sale_layout_cat_id': line.sale_layout_cat_id.id,
                        'part_number': line.part_number,
                        'purchase_line_id': line.id,
                    }

                else:

                    vals = {
                        'name': line.name,
                        'price_unit': line.price_unit,
                        'quantity': line.product_uom_qty - line.done_qty_wizard,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom.id,
                        'tax_ids': [(6, 0, line.taxes_id.ids)],
                        'sale_layout_cat_id': line.sale_layout_cat_id.id,
                        'part_number': line.part_number,
                        'purchase_line_id': line.id,
                        'discount_distribution': line.discount_distribution,
                        'net_taxable': line.net_taxable,
                        'discount': line.discount

                    }
                invoice_lines.append((0, 0, vals))
            for order in purchase_orders:
                create_moves = self.env['account.move'].create({
                    'project_id': order.project_id.id,
                    'task_id': order.task_id.id,
                    'discount_amount': order.discount_amount,
                    # 'project_id': task.project_id.id,
                    # 'task_id': self.env.context.get('active_id'),
                    'move_type': 'in_invoice',
                    'invoice_origin': order.name,
                    'invoice_user_id': order.user_id.id,
                    'partner_id': order.partner_id.id,
                    # 'currency_id': order.currency_id.id,
                    'invoice_line_ids': invoice_lines,
                    'invoice_payment_term_id': order.payment_term_id.id,
                    'payment_term': order.payment_term,
                    # 'add_information': order.add_information,
                    'narration':order.notes,
                    'purchase_id':order.id,
                    'purchase_bill_id':order.id,
                    'dis_amount':order.discount_amount
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
                    if total_inv > order.amount_total:
                        create_moves.unlink()
                        raise UserError(_('You are trying to invoice more than total price'))
        return

    def create_invoices(self):
        # task = self.env['project.task'].browse(self._context.get('active_ids', []))
        purchase = self.env['purchase.order'].browse(self._context.get('active_ids', []))


        if self.advance_payment_method == 'delivered':
            # purchase.action_create_invoice()
            self._create_invoices_vals()
            # purchase.is_regular_invoice = True
            # task.sale_id.task_invoice_ids = task.invoice_ids
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

            purchase_line_obj = self.env['purchase.order.line']
            for order in purchase:
                amount, name = self._get_advance_details(order)

                if self.product_id.invoice_policy != 'order':
                    raise UserError(
                        _('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(
                        _("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                taxes = self.product_id.taxes_id.filtered(
                    lambda r: not order.company_id or r.company_id == order.company_id)
                tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                analytic_tag_ids = []
                for line in order.order_line:
                    analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

                so_line_values = self._prepare_so_line(order, analytic_tag_ids, tax_ids, amount)
                so_line = purchase_line_obj.create(so_line_values)
                # so_line.unit_price = so_line.price_unit
                self._create_invoice(order, so_line, amount)
            if self._context.get('open_invoices', False):
                return purchase.action_view_invoice()
            return {'type': 'ir.actions.act_window_close'}

    # def create_invoices(self):
    #     purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids', []))
    #
    #     if self.advance_payment_method == 'delivered':
    #         purchase_orders._create_invoices(final=self.deduct_down_payments)
    #     else:
    #         # Create deposit product if necessary
    #         if not self.product_id:
    #             vals = self._prepare_deposit_product()
    #             self.product_id = self.env['product.product'].create(vals)
    #             self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)
    #
    #         sale_line_obj = self.env['sale.order.line']
    #         for order in purchase_orders:
    #             amount, name = self._get_advance_details(order)
    #
    #             if self.product_id.invoice_policy != 'order':
    #                 raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
    #             if self.product_id.type != 'service':
    #                 raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
    #             taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
    #             tax_ids = order.fiscal_position_id.map_tax(taxes).ids
    #             analytic_tag_ids = []
    #             for line in order.order_line:
    #                 analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
    #
    #             so_line_values = self._prepare_so_line(order, analytic_tag_ids, tax_ids, amount)
    #             so_line = sale_line_obj.create(so_line_values)
    #             self._create_invoice(order, so_line, amount)
    #     if self._context.get('open_invoices', False):
    #         return purchase_orders.action_view_invoice()
    #     return {'type': 'ir.actions.act_window_close'}

    def _prepare_deposit_product(self):
        return {
            'name': _('Down payment'),
            'type': 'service',
            'invoice_policy': 'order',
            'property_account_income_id': self.deposit_account_id.id,
            'taxes_id': [(6, 0, self.deposit_taxes_id.ids)],
            'company_id': False,
        }


    def show_so_lines(self):
        purchase = self.env['purchase.order'].browse(self._context.get('active_ids', []))
        wiz = self.env['wiz.purchase_order_line_edit'].create({'name':'Select Purchase Order Lines', 'purchase_id':purchase.id})
        for line in purchase.order_line.filtered(lambda x: not x.is_downpayment and not x.is_line_invoiced):
            invoice_tax = self.env['account.tax'].sudo().search(
                [('invoice_tax', '=', True), ('type_tax_use', '=', 'purchase')],
                limit=1)
            self.env['wiz.purchase_order_line_edit.lines'].create({
                'wizard_id': wiz.id,
                'line_id': line.id,
                'name': line.name,
                'part_number': line.part_number,
                # 'sl_no': line.sl_no,
                'unit_price': line.price_unit,
                'product_uom_qty': line.product_qty - line.done_qty_wizard,
                # 'price_included': line.price_included,
                # 'tax_total': line.tax_total,
                # 'price_total_val': line.price_total_val,
                # 'tax_id': [(6, 0, line.taxes_id.ids)],
                'tax_id': [(6, 0, invoice_tax.ids)],
                'sale_layout_cat_id': line.sale_layout_cat_id.id,
                'product_uom': line.product_uom.id,
                'discount_distribution': line.discount_distribution,
                'net_taxable': line.net_taxable,
                'discount': line.discount,

            })
        view = self.env.ref('vox_vendor_bill.wizard_form_purchase_order_line_edit')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wiz.purchase_order_line_edit',
            'res_id': wiz.id,
            'view_id': view.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new'}


