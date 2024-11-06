# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _default_disc_account(self):
        account_discount = self.env.ref("vox_task_template.account_discount_401200")
        return account_discount

    @api.depends('invoice_line_ids', 'invoice_line_ids.tax_ids', 'discount_distribution_type')
    def _compute_line_taxes(self):
        print("compute_line_taxes")
        dis_taxes = []
        for rec in self:
            for line in rec.invoice_line_ids:
                dis_taxes.append(line.tax_ids.ids[0]) if line.tax_ids else dis_taxes
            rec.line_taxes_ids = list(set(dis_taxes))


    discount_amount = fields.Float(string='Discount', readonly=True, states={'draft': [('readonly', False)]})

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')],
                                     string='Global Discount type', readonly=True, default='amount')
    disc_account_id = fields.Many2one('account.account', string='Discount Account',
                                      required=True, readonly=True, states={'draft': [('readonly', False)]},
                                      default=_default_disc_account)
    dis_amount = fields.Float(string="Dis")


    discount_distribution_type = fields.Selection([('against_item', 'Item Wise'), ('against_tax', 'Tax Wise')],
                                                  default='against_item', string="Discount Type")
    distribution_tax_ids = fields.Many2many('account.tax', string="Tax")
    line_taxes_ids = fields.Many2many('account.tax', string="Line Taxes", compute='_compute_line_taxes')

    @api.onchange('dis_amount', 'invoice_line_ids','distribution_tax_ids','discount_distribution_type')
    def _onchange_discount_amount(self):
        for order in self:
            total_vat_on_net_taxable = total_net_taxable = val = val1 = val3 = global_disc = 0.0
            sum_line_subtotal = sum(order.invoice_line_ids.mapped('price_subtotal'))

            qty_price_total = 0.0
            tax_wise_total = 0.0
            for tax_qty_price in order.invoice_line_ids:
                if tax_qty_price.tax_ids and tax_qty_price.tax_ids.ids[0] in order.distribution_tax_ids.ids:
                    tax_wise_total += (tax_qty_price.quantity * tax_qty_price.price_unit)
            for qty_price in order.invoice_line_ids:
                qty_price_total += (qty_price.quantity * qty_price.price_unit)

            if not 0.0 <= order.dis_amount <= qty_price_total:
                raise ValidationError(_('Enter proper discount'))
            for line in order.invoice_line_ids:
                if order.discount_distribution_type == 'against_item':
                    line.discount_distribution = (order.dis_amount / qty_price_total) * (
                            line.quantity * line.price_unit) if order.dis_amount else 0.0

                elif order.distribution_tax_ids and line.tax_ids and line.tax_ids.ids[0] in order.distribution_tax_ids.ids:
                    line.discount_distribution = (order.dis_amount / tax_wise_total) * (
                            line.quantity * line.price_unit) if tax_wise_total else 0.0
                else:
                    line.discount_distribution = 0.0
                # line.net_taxable = line.price_subtotal - line.discount_distribution
                # if line.tax_ids:
                #     for c in line.tax_ids.compute_all(line.net_taxable, order.currency_id, 1, False,
                #                                       line.move_id.partner_id)['taxes']:
                #         tax_on_net_taxable += c.get('amount', 0.0)
                #     line.l10n_ae_vat_amount = tax_on_net_taxable
                # line.price_subtotal_gross = line.net_taxable + line.l10n_ae_vat_amount
                line.discount = (line.discount_distribution / (
                        line.quantity * line.price_unit)) * 100.0 if line.discount_distribution else 0.0
                line._onchange_price_subtotal()
                # line.price_subtotal = (line.price_unit * line.quantity) - line.discount_distribution
                self._recompute_tax_lines(recompute_tax_base_amount=False, tax_rep_lines_to_recompute=None)
                # line._get_price_total_and_subtotal(price_unit=line.price_unit, quantity=line.quantity,
                #                                    discount=line.discount, currency=line.currency_id, product=None,
                #                                    partner=line.partner_id, taxes=line.tax_ids,
                #                                    move_type=line.move_id.move_type)
                # line._get_fields_onchange_subtotal_model(line.price_subtotal, line.move_id.move_type, line.currency_id,
                #                                          line.company_id, line.date)

                self._onchange_recompute_dynamic_lines()

    # @api.depends(
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.debit',
    #     'line_ids.credit',
    #     'line_ids.currency_id',
    #     'line_ids.amount_currency',
    #     'line_ids.amount_residual',
    #     'line_ids.amount_residual_currency',
    #     'line_ids.payment_id.state',
    #     'line_ids.full_reconcile_id',
    #     "dis_amount",
    #     "discount_type"
    # )
    # def _compute_amount(self):
    #     print("qqqqqqqqqqqqqqqqqqqqqqqqqqqqqq")
    #     # self._onchange_invoice_line_ids()
    #     super()._compute_amount()
    #     print("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz")
    #     for order in self:
    #         qty_price_total = 0.0
    #         for qty_price in order.invoice_line_ids:
    #             qty_price_total += (qty_price.quantity * qty_price.price_unit)
    #         # if not 0.0 <= order.dis_amount <= qty_price_total:
    #         #     print("dddddddddddddqqqqqqqqq")
    #         #     print(order.dis_amount,qty_price_total)
    #         #     raise ValidationError(_('Enter proper discount'))
    #
    #         for line in order.invoice_line_ids:
    #             line.discount_distribution = (order.dis_amount / qty_price_total) * (
    #                     line.quantity * line.price_unit) if order.dis_amount else 0.0
    #             line.discount = (line.discount_distribution / (
    #                     line.quantity * line.price_unit)) * 100.0 if line.discount_distribution else 0.0
    #             line._onchange_price_subtotal()
    #             self._recompute_tax_lines(recompute_tax_base_amount=False, tax_rep_lines_to_recompute=None)
    #             self._onchange_recompute_dynamic_lines()

    def set_discount_distribution(self):
        print("wwwwwwwwwwwwwwwwwwwwwwww")
        for order in self:
            total_vat_on_net_taxable = total_net_taxable = val = val1 = val3 = global_disc = 0.0
            sum_line_subtotal = sum(order.invoice_line_ids.mapped('price_subtotal'))
            if not 0.0 <= order.discount_amount <= sum_line_subtotal:
                raise ValidationError(_('Enter proper discount'))
            for line in order.invoice_line_ids:
                tax_on_net_taxable = tax = 0.0
                k = (order.discount_amount / sum_line_subtotal) * line.price_subtotal
                line.discount_distribution = round(k, 2)
                # line.net_taxable = line.price_subtotal - line.discount_distribution
                # if line.tax_ids:
                #     for c in line.tax_ids.compute_all(line.net_taxable, order.currency_id, 1, False,
                #                                       line.move_id.partner_id)['taxes']:
                #         tax_on_net_taxable += c.get('amount', 0.0)
                #     line.l10n_ae_vat_amount = tax_on_net_taxable
                # line.price_subtotal_gross = line.net_taxable + line.l10n_ae_vat_amount
                # line.discount = (line.discount_distribution / sum_line_subtotal) * 100.0
                line._onchange_price_subtotal()
                # line._get_price_total_and_subtotal(price_unit=line.price_unit, quantity=line.quantity,
                #                                    discount=line.discount, currency=line.currency_id, product=None,
                #                                    partner=line.partner_id, taxes=line.tax_ids,
                #                                    move_type=line.move_id.move_type)
                line._get_fields_onchange_subtotal_model(line.price_subtotal, line.move_id.move_type, line.currency_id,
                                                         line.company_id, line.date)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    global_discount_item = fields.Boolean()

    # @api.model
    # def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes,
    #                                         move_type):
    #     ''' This method is used to compute 'price_total' & 'price_subtotal'.
    #
    #     :param price_unit:  The current price unit.
    #     :param quantity:    The current quantity.
    #     :param discount:    The current discount.
    #     :param currency:    The line's currency.
    #     :param product:     The line's product.
    #     :param partner:     The line's partner.
    #     :param taxes:       The applied taxes.
    #     :param move_type:   The type of the move.
    #     :return:            A dictionary containing 'price_subtotal' & 'price_total'.
    #     '''
    #     res = {}
    #
    #     # Compute 'price_subtotal'.
    #     line_discount_price_unit = price_unit * (1 - (discount / 100.0))
    #     subtotal = quantity * line_discount_price_unit
    #
    #     # Compute 'price_total'.
    #     if taxes:
    #         taxes_res = taxes._origin.with_context(force_sign=1).compute_all((price_unit * quantity) - self.discount_distribution,
    #                                                                          quantity=1, currency=currency,
    #                                                                          product=product, partner=partner,
    #                                                                          is_refund=move_type in (
    #                                                                          'out_refund', 'in_refund'))
    #         res['price_subtotal'] = taxes_res['total_excluded']
    #         res['price_total'] = taxes_res['total_included']
    #     else:
    #         res['price_total'] = res['price_subtotal'] = subtotal
    #     # In case of multi currency, round before it's use for computing debit credit
    #     if currency:
    #         res = {k: currency.round(v) for k, v in res.items()}
    #
    #     # print("last---res",res)
    #     # print(self.discount_distribution)
    #     # print(round(self.discount_distribution,2))
    #     # res['price_subtotal'] = (price_unit * quantity) - self.discount_distribution
    #     # # res['price_total'] = res['price_subtotal'] + self.l10n_ae_vat_amount
    #     # print("price_total",res['price_total'])
    #     return res
