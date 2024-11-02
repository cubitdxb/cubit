# -*- coding: utf-8 -*-
import lib2to3.pgen2.grammar

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        member_ids = []
        member_ids += self.env['crm.team'].search([('team_code', '=', 'finance')]).mapped('member_ids').ids
        member_ids += self.env['crm.team'].search([('team_code', '=', 'finance')]).mapped('leader_ids').ids
        _logger.info('members %s', member_ids)
        print(member_ids, 11111111111222222222222222222222)
        if self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id or self.env.uid in member_ids:
            res = super().write(vals)
            return res
        else:
            raise ValidationError("You can't edit, Please contact Administrator")
        return super().write(vals)

    @api.depends('invoice_line_ids.price_subtotal', 'amount_residual')
    def _compute_amount_paid(self):
        for record in self:
            record.amount_paid = 0.0
            amount_total = residual = amount_paid = 0.0
            if record.state not in ['draft', 'proforma', 'proforma2', 'cancel']:
                amount_total = record.amount_total
                residual = record.amount_residual
                amount_paid = amount_total - residual
                record.amount_paid = amount_paid

        # self.amount_paid = 0.0
        # if self.state not in ['draft', 'proforma', 'proforma2', 'cancel']:
        #     amount_total = self.amount_total
        #     residual = self.amount_residual
        #     amount_paid = amount_total - residual
        #     self.amount_paid = amount_paid

    task_id = fields.Many2one('project.task', string='Task')
    project_id = fields.Many2one('project.project', string='Project')
    place_of_supply = fields.Many2one('res.country.state',string="Place of Supply")
    place_of_delivery = fields.Many2one('res.country.state',string="Place of Delivery")
    # exclude_tax = fields.Boolean(string="Exclude Tax")
    exclude_tax = fields.Selection([('', '-select-'), ('include_tax', 'Include Tax'), ('exclude_tax', 'Exclude Tax')],default='include_tax', string="Include/Exclude Tax")

    def _default_tax_value(self):
        if self.env.context.get('default_move_type'):
            if self.env.context.get('default_move_type') in ('out_invoice', 'out_refund'):
                return self.env['account.tax'].sudo().search([('invoice_tax', '=', True), ('type_tax_use', '=', 'sale')], limit=1).id
            else:
                return self.env['account.tax'].sudo().search(
                    [('invoice_tax', '=', True), ('type_tax_use', '=', 'purchase')], limit=1).id


    include_tax_val = fields.Many2one('account.tax',string="Tax",default=_default_tax_value)
    custom_invoice_date_due=fields.Date(related='invoice_date_due', string='Due Date')

    cubit_id = fields.Integer(string="Cubit ID")

    # residual = fields.Float(string='Balance',compute='_compute_residual', store=True)
    amount_paid = fields.Float(string='Amount Paid',compute='_compute_amount_paid')
    sale_task_id = fields.Many2one('sale.order')
    add_information = fields.Html(string="Additional Information")

    add_tax = fields.Boolean('Add Tax',
                             help='By checking this boolean will add TAX automatically in all the line items')

    lpo_number = fields.Char(string="LPO Number")
    

    @api.onchange('add_tax')
    def onchange_add_tax(self):
        tax = self.env['account.tax'].sudo().search([('sale_add_tax', '=', True), ('type_tax_use', '=', 'sale')])
        purchase_tax = self.env['account.tax'].sudo().search([('sale_add_tax', '=', True), ('type_tax_use', '=', 'purchase')])
        for order in self:
            if order.move_type in ('out_invoice','out_refund'):
                if order.add_tax == True:
                    for line in order.invoice_line_ids:
                        line.write({'tax_ids': [(4, t.id) for t in tax if t]})
                else:
                    for line in order.invoice_line_ids:
                        line.write({'tax_ids': False})
            if order.move_type in ('in_invoice', 'in_refund'):
                if order.add_tax == True:
                    for line in order.invoice_line_ids:
                        line.write({'tax_ids': [(4, t.id) for t in purchase_tax if t]})
                else:
                    for line in order.invoice_line_ids:
                        line.write({'tax_ids': False})

    def move_confirm_wizard_button(self):
        for move in self:
            self.onchange_exclude_tax()
            if move.move_type in ('out_invoice', 'out_refund'):
                action = self.env["ir.actions.actions"]._for_xml_id('vox_task_invoice.update_recipient_bank_action')
                action['context'] = {'default_move_id': self.id}
                return action
            else:
                return move.action_post()
                # return super(AccountMove, self).action_post()

    @api.onchange('exclude_tax','include_tax_val')
    def onchange_exclude_tax(self):
        tax = self.env['account.tax'].sudo().search([('exclude_tax', '=', True)])
        for taxes in self:
            if taxes.exclude_tax == 'exclude_tax':
                if taxes.invoice_line_ids:
                    # taxes.invoice_line_ids = False
                    for line in taxes.invoice_line_ids:
                        # line.write({'tax_ids': [(4, t.id) for t in tax if t]})
                        # line.write({'tax_ids': False})
                        # line.tax_ids = False
                        line.tax_ids = False
                        # line.tax_ids = [t.id for t in tax if t]
                        line.l10n_ae_vat_amount = False

                    taxes.tax_totals_json = False
                    taxes.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True)
            elif taxes.exclude_tax == 'include_tax':
                if taxes.include_tax_val:
                    if taxes.invoice_line_ids:
                        for line in taxes.invoice_line_ids:
                            # line.tax_ids = [t.id for t in tax if t]

                            line.tax_ids = taxes.include_tax_val.ids
                            line._onchange_price_subtotal()
                        taxes.with_context(check_move_validity=False)._recompute_dynamic_lines(
                                recompute_all_taxes=True)
                            # line.l10n_ae_vat_amount = False
                            # line.write({'tax_ids': [(4, taxes.include_tax_val.id)]})
                            # line.write({'tax_ids': [(4, taxes.include_tax_val.id)]})
                else:
                    for line in taxes.invoice_line_ids:
                        line.tax_ids = False
                        line.l10n_ae_vat_amount = False
                        # line.write({'tax_ids': False})
                # taxes.tax_totals_json = False
                taxes.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True)

            else:
                if taxes.invoice_line_ids:
                    for line in taxes.invoice_line_ids:
                        line.tax_ids = False
                        line.l10n_ae_vat_amount = False

                    taxes.tax_totals_json = False
                    taxes.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True)


                    # line._onchange_mark_recompute_taxes()
                    # line._onchange_price_subtotal()
                    # taxes.update(taxes._get_price_total_and_subtotal())
                    # taxes.update(taxes._get_fields_onchange_subtotal())
            # else:
            #     if taxes.invoice_line_ids:
            #         for line in taxes.invoice_line_ids:
            #             line.tax_ids = False
            #             line.tax_ids = line.product_id.taxes_id.ids + line.tax_ids.ids

    def button_cancel(self):
        res = super().button_cancel()
        down_payment_line = self.invoice_line_ids.filtered(lambda l: l.name.startswith('Down payment') or l.name.startswith('Down Payment') if l.name else False)
        if down_payment_line and down_payment_line.sale_line_ids:
            down_payment_line.sale_line_ids.is_cancel_down_payment = True
        elif down_payment_line and down_payment_line.purchase_line_id:
            down_payment_line.purchase_line_id.is_cancel_down_payment = True
        return res

    def button_draft(self):
        res = super().button_draft()
        down_payment_line = self.invoice_line_ids.filtered(lambda l: l.name.startswith('Down payment') or l.name.startswith('Down Payment') if l.name else False)
        if down_payment_line and down_payment_line.sale_line_ids:
            down_payment_line.sale_line_ids.is_cancel_down_payment = False
        elif down_payment_line and down_payment_line.purchase_line_id:
            down_payment_line.purchase_line_id.is_cancel_down_payment = False
        return res


    payment_term = fields.Char(string="Payment Terms")


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends('price_unit', 'discount', 'tax_ids', 'quantity',
                 'product_id', 'move_id.partner_id',
                 'move_id.currency_id')
    def _compute_price_gross(self):
        for invoice in self:
            price = invoice.price_unit * (1 - (invoice.discount or 0.0) / 100.0)
            if invoice.tax_ids:
                taxes = invoice.tax_ids.compute_all(price,invoice.move_id.currency_id, invoice.quantity, product=invoice.product_id,partner=invoice.move_id.partner_id)
                invoice.price_subtotal_gross = taxes['total_included']
            if not invoice.tax_ids:
                invoice.price_subtotal_gross = invoice.price_subtotal

    @api.depends('discount_distribution')
    def _compute_discount_distribution2(self):
        for rec in self:
            rec.discount_distribution2 = (rec.price_unit * rec.quantity)*rec.discount/100.0

    @api.depends('price_unit', 'quantity')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = rec.price_unit * rec.quantity

    cubit_id = fields.Integer(string="Cubit ID")
    price_subtotal_gross = fields.Float(string='Total Amount',compute='_compute_price_gross', readonly=True,store=True)
    # tax_amount = fields.Float(string='Tax',compute='_compute_tax', readonly=True)
    sale_layout_cat_id = fields.Many2one('sale_layout.category', string='Section')
    # categ_sequence = fields.Integer(related='sale_layout_cat_id.sequence',string='Layout Sequence', store=True)

    # @api.depends('price_unit', 'discount', 'tax_ids', 'quantity',
    #              'product_id', 'move_id.partner_id', 'move_id.currency_id')
    # def _compute_price(self):
    #     price = self.price_unit
    #     taxes = self.tax_ids.compute_all(price, self.move_id.currency_id,self.quantity, product=self.product_id,
    #                                                  partner=self.invoice_id.partner_id)
    #     self.price_subtotal = taxes['total'] - self.discount
    #     if self.invoice_id:
    #         self.price_subtotal = self.move_id.currency_id.round(self.price_subtotal)
    #
    # price_subtotal = fields.Float(string='Amount',store=True, readonly=True, compute='_compute_price')
    part_number = fields.Char(string='Part Number')
    service_suk = fields.Char(string="Service SUK")
    serial_num = fields.Char(string="Serial Number")
    begin_date = fields.Char(string="Begin Date")
    end_date = fields.Char(string="End Date")
    discount_distribution = fields.Float(string="Discount Distribution")
    net_taxable = fields.Float(string="Net Taxable")
    discount_distribution2 = fields.Float(string="Discount Distribution2", compute='_compute_discount_distribution2')
    total_price = fields.Float(string="Total Price", compute='_compute_total_price')

    @api.onchange('product_id')
    def onchange_invoice_lines(self):
        for rec in self:
            if not rec.move_id.exclude_tax:
                raise ValidationError('Please choose Include/Exclude Tax')




    # @api.depends('price_unit', 'discount', 'tax_ids', 'quantity',
    #              'product_id', 'move_id.partner_id',
    #              'move_id.currency_id')
    # def _compute_tax(self):
    #     for invoice in self:
    #         price = invoice.price_unit * (1 - (invoice.discount or 0.0) / 100.0)
    #         val = 0.0
    #         for c in invoice.tax_ids.compute_all(price, invoice.move_id.currency_id,self.quantity, product=invoice.product_id,
    #                             partner=invoice.move_id.partner_id)['taxes']:
    #             val += c.get('amount', 0.0)
    #         if invoice.move_id:
    #             invoice.tax_amount = val



    _sql_constraints = [
        ('accountable_required_fields',
         'check(1=1)',
         "Missing required fields on accountable sale order line."),

    ]


class AccountTaxInherit(models.Model):
    _inherit = "account.tax"

    exclude_tax = fields.Boolean("Exclude Tax")
    invoice_tax = fields.Boolean("Invoice Tax")


