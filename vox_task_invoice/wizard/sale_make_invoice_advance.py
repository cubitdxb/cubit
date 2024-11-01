# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"


    @api.model
    def default_get(self, fields):
        # # res = super(SaleAdvancePaymentInv, self).default_get(fields)
        # project_team_users = self.env['crm.team'].search([('team_code', '=', 'project')]).mapped('member_ids').ids
        # procurement_team_users = self.env['crm.team'].search([('team_code', '=', 'procurement')]).mapped(
        #     'member_ids').ids
        finance_team_users = self.env['crm.team'].search([('team_code', '=', 'finance')]).mapped('member_ids').ids
        # procurement_finance = procurement_team_users + finance_team_users
        current_user = self.env.uid

        if not (self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id):
            if current_user not in finance_team_users:
                raise ValidationError(_('You are not able to create Invoice'))

        if self.env.context.get('active_model') == 'project.task':
            task = self.env['project.task'].browse(self.env.context.get('active_id'))
            self.env.context = dict(self.env.context)
            self.env.context.update({
                'active_id': task.sale_id.id,
                'active_ids': task.sale_id.ids,
                'active_model':'sale.order',
                'task_id':self.env.context.get('active_id'),
                'task_model':'project.task'
            })
        return super(SaleAdvancePaymentInv, self).default_get(fields)

    @api.model
    def _default_has_down_payment(self):
        # if self._context.get('active_model') == 'project.task' and self._context.get('active_id', False):
        if self._context.get('task_model') == 'project.task' and self._context.get('task_id', False):
            task = self.env['project.task'].browse(self._context.get('task_id'))
            task = self.env['project.task'].browse(self._context.get('task_id'))
            return task.sale_id.order_line.filtered(
                lambda sale_order_line: sale_order_line.is_downpayment
            )

        return False

    has_down_payments = fields.Boolean('Has down payments', default=_default_has_down_payment, readonly=True)
    advance_payment_method = fields.Selection(selection_add=[('some_order_lines', 'Some Order Lines')],ondelete={'some_order_lines': 'cascade'})




    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        if self.advance_payment_method == 'percentage':
            amount = self.default_get(['amount']).get('amount')
            return {'value': {'amount': amount}}
        return {}

    def _prepare_invoice_values(self, order, name, amount, so_line):
        # task = self.env['project.task'].browse(self.env.context.get('active_id'))
        # task = self.env['project.task'].browse(self._context.get('active_ids', []))
        invoice_tax = self.env['account.tax'].sudo().search([('invoice_tax', '=', True), ('type_tax_use', '=', 'sale')],
                                                            limit=1)
        invoice_vals = {
            # 'task_id': self.env.context.get('active_id'),
            'project_id':order.project_id.id,
            'lpo_number': order.lpo_number,
            'ref': order.client_order_ref,
            'move_type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': (order.fiscal_position_id or order.fiscal_position_id.get_fiscal_position(
                order.partner_id.id)).id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_reference': order.reference,
            'invoice_payment_term_id': order.payment_term_id.id,
            'payment_term': order.payment_term,
            'partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'add_information': order.add_information,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,
                'tax_ids': [(6, 0, so_line.tax_id.ids)],
                # 'tax_ids': [(6, 0, invoice_tax.ids)],
                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id if not so_line.display_type and order.analytic_account_id.id else False,
                'discount_distribution': so_line.discount_distribution,
                'net_taxable': so_line.net_taxable,
                'price_subtotal': so_line.price_included,
                'discount': so_line.discount,
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
        else:
            amount = self.fixed_amount
            name = _('Down Payment')
        del context

        return amount, name


    def _create_invoice(self, order, so_line, amount):
        total_inv = 0
        for invoices in self.env['account.move'].search([('task_id.sale_id', '=', order.id),('state','!=','cancel'),('move_type', 'in', ('out_invoice','out_refund'))]):
            invoices.amount_total = round(invoices.amount_total, 2)
            total_inv += invoices.amount_total
        amount = round(amount, 2)
        total_inv += amount
        if total_inv > (order.amount_total+1):
            raise UserError(_('You are trying to invoice more than total price'))
        if (self.advance_payment_method == 'percentage' and self.amount <= 0.00) or (
                self.advance_payment_method == 'fixed' and self.fixed_amount <= 0.00):
            raise UserError(_('The value of the down payment amount must be positive.'))

        amount, name = self._get_advance_details(order)

        invoice_vals = self._prepare_invoice_values(order, name, amount, so_line)

        if order.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id

        # invoice = self.env['account.move'].with_company(order.company_id) \
        #     .sudo().create(invoice_vals).with_user(self.env.uid)
        # invoice.message_post_with_view('mail.message_origin_link',
        #                                values={'self': invoice, 'origin': order},
        #                                subtype_id=self.env.ref('mail.mt_note').id)

        task = self.env['project.task'].browse(self._context.get('active_ids', []))
        task.write({'invoice_ids': [(0, 0, invoice_vals)]})
        task.sale_id.sudo().task_invoice_ids = task.invoice_ids
        task.sale_id.sudo().task_invoice_ids.message_post_with_view('mail.message_origin_link',
                                       values={'self': task.sale_id.sudo().task_invoice_ids, 'origin': order},
                                       subtype_id=self.env.ref('mail.mt_note').id)
        return
        # return invoice

    def _prepare_so_line(self, order, analytic_tag_ids, tax_ids, amount):
        context = {'lang': order.partner_id.lang}
        so_values = {
            'name': _('Down Payment: %s') % (time.strftime('%m %Y'),),
            'price_unit': amount,
            'unit_price': amount,
            'product_uom_qty': 0.0,
            'order_id': order.id,
            'discount': 0.0,
            'product_uom': self.product_id.uom_id.id,
            'product_id': self.product_id.id,
            'analytic_tag_ids': analytic_tag_ids,
            'tax_id': [(6, 0, tax_ids)],
            'is_downpayment': True,
            'sequence': order.order_line and order.order_line[-1].sequence + 1 or 10,
        }
        del context
        return so_values

    def _create_invoices_vals(self):
        task = self.env['project.task'].browse(self._context.get('active_ids', []))
        vat = task.sale_id.amount_tax
        product_discount = task.sale_id.discount_amount
        service_discount = task.sale_id.service_discount_amount
        invoice_lines = []
        total_price = 0.0
        for line in task.sale_id.order_line.filtered(lambda x: not x.is_line_invoiced and not x.is_cancel_down_payment):
            if line.is_downpayment:
                total_price = total_price + line.unit_price * -1
            else:
                total_price = total_price + line.unit_price * line.product_uom_qty

        total_price = total_price - product_discount - service_discount + vat
        if total_price < 0:
            for line in task.sale_id.order_line.filtered(lambda x: not x.is_line_invoiced and not x.is_cancel_down_payment):
                if line.is_downpayment:
                    vals = {
                        'name': line.name,
                        'price_unit': line.unit_price,
                        'quantity': 1,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom.id,
                        'tax_ids': [(6, 0, line.tax_id.ids)],
                        'sale_layout_cat_id': line.sale_layout_cat_id.id,
                        'part_number': line.part_number,
                    }
                    line.update({'qty_invoiced': 1})

                else:

                    vals = {
                        'name': line.name,
                        'price_unit': line.unit_price,
                        'quantity': -(line.product_uom_qty-line.done_qty_wizard),
                        'product_id': line.product_id.id,
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
                        'price_subtotal': line.price_included,
                        'discount':line.discount,
                    }
                    line.update({'qty_invoiced': -(line.product_uom_qty-line.done_qty_wizard)})
                invoice_lines.append((0, 0, vals))



            for order in task.sale_id:
                create_moves = self.env['account.move'].create({
                    # 'ref': self.client_order_ref,
                    'project_id': task.project_id.id,
                    'task_id': self.env.context.get('active_id'),
                    'move_type': 'out_refund',
                    'invoice_origin': order.name,
                    'invoice_user_id': order.user_id.id,
                    'partner_id': order.partner_invoice_id.id,
                    'currency_id': order.pricelist_id.currency_id.id,
                    'invoice_line_ids': invoice_lines,
                    'invoice_payment_term_id': order.payment_term_id.id,
                    'payment_term': order.payment_term,
                    'add_information': order.add_information,
                    'narration':order.note,
                })
                if create_moves:
                    amount = create_moves.amount_total
                    total_inv = 0
                    for invoices in self.env['account.move'].search(
                            [('task_id.sale_id', '=', order.id), ('state', '!=', 'cancel'),('move_type', 'in', ('out_invoice','out_refund')),('id','!=',create_moves.id)]):
                        invoices.amount_total = round(invoices.amount_total, 2)
                        total_inv += invoices.amount_total
                    amount = round(amount, 2)
                    total_inv += amount
                    if total_inv > order.amount_total:
                        create_moves.unlink()
                        raise UserError(_('You are trying to invoice more than total price'))



        else:

            for line in task.sale_id.order_line.filtered(lambda x: not x.is_line_invoiced and not x.is_cancel_down_payment):
                invoice_tax = self.env['account.tax'].sudo().search([('invoice_tax', '=', True), ('type_tax_use', '=', 'sale')],
                                                      limit=1)

                if line.is_downpayment:
                    vals = {
                        'name': line.name,
                        'price_unit': line.unit_price,
                        'quantity': -1,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom.id,
                        'tax_ids': [(6, 0, line.tax_id.ids)],
                        # 'tax_ids': [(6, 0, invoice_tax.ids)],
                        'sale_layout_cat_id': line.sale_layout_cat_id.id,
                        'part_number': line.part_number,
                    }
                    line.update({'qty_invoiced': -1})
                else:

                    vals = {
                        'name': line.name,
                        'price_unit': line.unit_price,
                        'quantity': line.product_uom_qty - line.done_qty_wizard,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom.id,
                        'tax_ids': [(6, 0, line.tax_id.ids)],
                        # 'tax_ids': [(6, 0, invoice_tax.ids)],
                        'sale_layout_cat_id': line.sale_layout_cat_id.id,
                        'part_number': line.part_number,
                        'service_suk': line.service_suk,
                        'serial_num': line.serial_num,
                        'begin_date': line.begin_date,
                        'end_date': line.end_date,
                        'discount_distribution': line.discount_distribution,
                        'net_taxable': line.net_taxable,
                        'discount':line.discount
                    }
                    line.update({'qty_invoiced': line.product_uom_qty - line.done_qty_wizard})
                invoice_lines.append((0, 0, vals))

            for order in task.sale_id:
                create_moves = self.env['account.move'].create({
                    'project_id': task.project_id.id,
                    'task_id': self.env.context.get('active_id'),
                    'move_type': 'out_invoice',
                    'invoice_origin': order.name,
                    'invoice_user_id': order.user_id.id,
                    'partner_id': order.partner_invoice_id.id,
                    'currency_id': order.pricelist_id.currency_id.id,
                    'invoice_line_ids': invoice_lines,
                    'invoice_payment_term_id': order.payment_term_id.id,
                    'payment_term': order.payment_term,
                    'add_information': order.add_information,
                    'narration':order.note,
                    'lpo_number':order.lpo_number,
                    'dis_amount': order.discount_amount + order.service_discount_amount,
                    'discount_distribution_type': order.discount_distribution_type,
                    'line_taxes_ids': order.line_taxes_ids.ids,
                    'distribution_tax_ids':order.distribution_tax_ids.ids,

                })
                if create_moves:
                    amount = create_moves.amount_total
                    total_inv = 0
                    for invoices in self.env['account.move'].search(
                            [('task_id.sale_id', '=', order.id), ('state', '!=', 'cancel'),('move_type', 'in', ('out_invoice','out_refund')),('id','!=',create_moves.id)]):
                        invoices.amount_total = round(invoices.amount_total, 2)
                        total_inv += invoices.amount_total
                    amount = round(amount, 2)
                    total_inv += amount
                    if total_inv > order.amount_total:
                        create_moves.unlink()
                        raise UserError(_('You are trying to invoice more than total price'))

        return

    def create_invoices(self):
        finance_team_users = self.env['crm.team'].search([('team_code', '=', 'finance')]).mapped('member_ids').ids
        current_user = self.env.uid
        if not (self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id):
            if current_user not in finance_team_users:
                raise ValidationError(_('You are not able to create Invoice'))
        task = self.env['project.task'].browse(self._context.get('active_ids', []))
        if self.advance_payment_method == 'delivered':
            self._create_invoices_vals()
            task.is_regular_invoice = True
            task.sale_id.sudo().task_invoice_ids = task.invoice_ids
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

            sale_line_obj = self.env['sale.order.line']
            for order in task.sudo().sale_id:
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
                so_line = sale_line_obj.sudo().create(so_line_values)
                so_line.unit_price = so_line.price_unit
                self._create_invoice(order, so_line, amount)
            if self._context.get('open_invoices', False):
                return task.sale_id.action_view_invoice()
            return {'type': 'ir.actions.act_window_close'}

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
        finance_team_users = self.env['crm.team'].search([('team_code', '=', 'finance')]).mapped('member_ids').ids
        current_user = self.env.uid
        if not (self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id):
            if current_user not in finance_team_users:
                raise ValidationError(_('You are not able to create Invoice'))
        task = self.env['project.task'].browse(self._context.get('active_ids', []))
        sale_order = task.sale_id
        wiz = self.env['wiz.sale_order_line_edit'].create({'name':'Select Sale Order Lines', 'task_id':task.id})
        for line in sale_order.order_line.filtered(lambda x: not x.is_downpayment and not x.is_line_invoiced):
            invoice_tax = self.env['account.tax'].sudo().search(
                [('invoice_tax', '=', True), ('type_tax_use', '=', 'sale')],
                limit=1)
            self.env['wiz.sale_order_line_edit.lines'].create({
                'wizard_id': wiz.id,
                'line_id': line.id,
                'name': line.name,
                'part_number': line.part_number,
                'sl_no': line.sl_no,
                'unit_price': line.unit_price,
                'product_uom_qty': line.product_uom_qty - line.done_qty_wizard,
                'price_included': line.price_included,
                'tax_total': line.tax_total,
                'price_total_val': line.price_total_val,
                # 'tax_id': [(6, 0, line.tax_id.ids)],
                'tax_id': [(6, 0, invoice_tax.ids)],
                'sale_layout_cat_id': line.sale_layout_cat_id.id,
                'product_uom': line.product_uom.id,
                'service_suk': line.service_suk,
                'serial_num': line.serial_num,
                'begin_date': line.begin_date,
                'end_date': line.end_date,
                'discount_distribution': line.discount_distribution,
                'net_taxable': line.net_taxable,
                'discount':line.discount,
            })
        view = self.env.ref(
            'vox_task_invoice.wiz_sale_order_line_edit')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wiz.sale_order_line_edit',
            'res_id': wiz.id,
            'view_id': view.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new'}
