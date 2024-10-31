# -*- coding: utf-8 -*-
##############################################################################


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    cubit_move_id = fields.Integer(string="Cubit Move ID")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    adv_payment_id = fields.Many2one('account.payment.line', string='Multi Payment Id')


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.depends('amount', 'allocation_amount')
    def _compute_writeoff(self):
        for rec in self:
            if rec.is_multi_match:
                rec.write_off_amount = rec.amount - rec.allocation_amount
            else:
                rec.write_off_amount = 0.0
            if rec.amount - rec.allocation_amount == 0.0:
                rec.is_writeoff_details = True
            else:
                rec.is_writeoff_details = False

    @api.depends('payment_line_ids.writeoff_amount', )
    def _compute_line_writeoff_total(self):
        total_writeoff = 0.0
        for rec in self:
            for line in rec.payment_line_ids:
                total_writeoff += line.writeoff_amount

            rec.line_write_off_total = total_writeoff

    @api.onchange('is_multi_match')
    def onchange_payment_for(self):
        if self.is_multi_match:
            for line in self.payment_line_ids:
                line.unlink()

    @api.depends('payment_line_ids', 'payment_line_ids.allocation')
    def get_allocation_amount(self):
        for payment in self:
            amount = 0
            payment.allocation_amount = 0
            for line in payment.payment_line_ids:
                amount += line.allocation
            payment.allocation_amount = amount

    @api.onchange('partner_id', 'is_multi_match', 'payment_type')
    def _onchange_partner_id(self):
        line_vals = []
        account_moves = []
        for rec in self:
            rec.payment_line_ids = False
            if rec.payment_type == 'inbound':
                if rec.partner_id:
                    account_moves = self.env['account.move'].search(
                        [('partner_id', '=', rec.partner_id.id), ('move_type', '=', 'out_invoice'),
                         ('payment_state', 'in', ('not_paid', 'partial')), ('state', '=', 'posted')])
            else:
                if rec.partner_id:
                    account_moves = self.env['account.move'].search(
                        [('partner_id', '=', rec.partner_id.id), ('move_type', '=', 'in_invoice'),
                         ('payment_state', 'in', ('not_paid', 'partial')), ('state', '=', 'posted')])

            if rec.is_multi_match and account_moves:
                for mov in account_moves:
                    open_invoice_lines = {'invoice_id': mov.id,
                                          'account_id': mov.partner_id.property_account_receivable_id.id
                                          if rec.payment_type == 'inbound'
                                          else mov.partner_id.property_account_payable_id.id,
                                          'date': mov.date,
                                          'due_date': mov.invoice_date_due,
                                          'original_amount': mov.amount_total,
                                          'balance_amount': mov.amount_residual,
                                          'payment_id': rec.id,
                                          'currency_id': rec.currency_id.id}
                    line_vals.append((0, 0, open_invoice_lines))
            rec.payment_line_ids = line_vals

    payment_line_ids = fields.One2many('account.payment.line', 'payment_id')
    is_multi_match = fields.Boolean(string="Multi March?")
    allocation_amount = fields.Float('Total Amount',
                                     compute='get_allocation_amount',
                                     store=True, digits='Product Price')
    write_off_acc_id = fields.Many2one('account.account', string="Counterpart Account")
    write_off_comment = fields.Char(string="Counterpart Comment")
    is_writeoff_details = fields.Boolean(string="Writeoff Details", compute='_compute_writeoff', store=True)
    is_keep_open = fields.Boolean(string="Keep Open")
    write_off_amount = fields.Float(string="Difference Amount", compute='_compute_writeoff',
                                    store=True, digits='Product Price')
    line_write_off_total = fields.Float(string="Line write-off Total",
                                        compute='_compute_line_writeoff_total',
                                        store=True, digits='Product Price')

    def _synchronize_from_moves(self, changed_fields):
        for payment in self:
            if payment.is_multi_match:
                return True
        return super(AccountPayment, self)._synchronize_from_moves(changed_fields)

    def dev_reconcile(self):
        for line in self.payment_line_ids.filtered(lambda m: m.allocation > 0.0):
            invoice_id = line.invoice_id
            move_line = self.env['account.move.line'].search(
                [('move_id', '=', self.move_id.id), ('adv_payment_id', '=', line.id)])
            invoice_id.js_assign_outstanding_line(move_line.id)
        return True

    def loss_amount_payment_line(self, amount):
        for rec in self:
            currency_id = rec.currency_id.id
            # Compute a default label to set on the journal items.

            payment_display_name = {
                'outbound-customer': _("Customer Reimbursement"),
                'inbound-customer': _("Customer Payment"),
                'outbound-supplier': _("Vendor Payment"),
                'inbound-supplier': _("Vendor Reimbursement"),
            }

            default_line_name = self.env['account.move.line']._get_default_line_name(
                _("Internal Transfer") if rec.is_internal_transfer else payment_display_name[
                    '%s-%s' % (rec.payment_type, rec.partner_type)],
                amount,
                rec.currency_id,
                rec.date,
                partner=rec.partner_id,
            )
            new_lines = []

            if rec.is_keep_open and rec.write_off_amount < 0.0 and rec.payment_type == 'outbound':
                rec_dict = {
                    'name': rec.payment_reference or default_line_name,
                    'date_maturity': rec.date,
                    'currency_id': currency_id,
                    'debit': 0.0,
                    'credit': -rec.write_off_amount,
                    'partner_id': rec.partner_id.id,
                    'account_id': rec.destination_account_id.id,
                }
                new_lines.append(rec_dict)

            elif rec.is_keep_open and rec.write_off_amount < 0.0 and rec.payment_type == 'inbound':
                rec_dict = {
                    'name': rec.payment_reference or default_line_name,
                    'date_maturity': rec.date,
                    'currency_id': currency_id,
                    'debit': -rec.write_off_amount,
                    'credit': 0.0,
                    'partner_id': rec.partner_id.id,
                    'account_id': rec.destination_account_id.id,
                }

                new_lines.append(rec_dict)
            elif rec.is_keep_open and rec.write_off_amount > 0.0:
                raise ValidationError("Keep on option not work on positive amount")
            else:
                liq_dic = {}
                if rec.payment_type == 'outbound' and amount < 0.0:
                    liq_dic = {
                        'name': rec.write_off_comment,
                        'date_maturity': rec.date,
                        'amount_currency': -amount,
                        'currency_id': rec.currency_id.id,
                        'debit': 0.0,
                        'credit': -amount,
                        'partner_id': rec.partner_id.id,
                        'account_id': rec.write_off_acc_id.id,
                    }

                elif rec.payment_type == 'inbound' and amount < 0.0:
                    liq_dic = {
                        'name': rec.write_off_comment,
                        'date_maturity': rec.date,
                        'amount_currency': -amount,
                        'currency_id': rec.currency_id.id,
                        'debit': -amount,
                        'credit': 0.0,
                        'partner_id': rec.partner_id.id,
                        'account_id': rec.write_off_acc_id.id,
                    }

                new_lines.append(liq_dic)
            return new_lines

    def more_amount_payment_line(self, amount):
        for rec in self:
            currency_id = rec.currency_id.id
            # Compute a default label to set on the journal items.
            payment_display_name = {
                'outbound-customer': _("Customer Reimbursement"),
                'inbound-customer': _("Customer Payment"),
                'outbound-supplier': _("Vendor Payment"),
                'inbound-supplier': _("Vendor Reimbursement"),
            }

            default_line_name = self.env['account.move.line']._get_default_line_name(
                _("Internal Transfer") if rec.is_internal_transfer else payment_display_name[
                    '%s-%s' % (rec.payment_type, rec.partner_type)],
                amount,
                rec.currency_id,
                rec.date,
                partner=rec.partner_id,
            )
            new_lines = []

            if rec.is_keep_open and rec.write_off_amount > 0.0 and rec.payment_type == 'outbound':
                rec_dict = {
                    'name': rec.payment_reference or default_line_name,
                    'date_maturity': rec.date,
                    'currency_id': currency_id,
                    'debit': rec.write_off_amount,
                    'credit': 0.0,
                    'partner_id': rec.partner_id.id,
                    'account_id': rec.destination_account_id.id,
                }
                new_lines.append(rec_dict)

            elif rec.is_keep_open and rec.write_off_amount > 0.0 and rec.payment_type == 'inbound':
                rec_dict = {
                    'name': rec.payment_reference or default_line_name,
                    'date_maturity': rec.date,
                    'currency_id': currency_id,
                    'debit': 0.0,
                    'credit': rec.write_off_amount,
                    'partner_id': rec.partner_id.id,
                    'account_id': rec.destination_account_id.id,
                }

                new_lines.append(rec_dict)
            elif rec.is_keep_open and rec.write_off_amount < 0.0:
                raise ValidationError("Keep on option not work on negative amount")

            else:
                liq_dic = {}
                if rec.payment_type == 'inbound' and amount > 0.0:
                    liq_dic = {
                        'name': rec.write_off_comment,
                        'date_maturity': rec.date,
                        'amount_currency': -amount,
                        'currency_id': rec.currency_id.id,
                        'debit': 0.0,
                        'credit': amount,
                        'partner_id': rec.partner_id.id,
                        'account_id': rec.write_off_acc_id.id,
                    }

                elif rec.payment_type == 'outbound' and amount > 0.0:
                    liq_dic = {
                        'name': rec.write_off_comment,
                        'date_maturity': rec.date,
                        'amount_currency': -amount,
                        'currency_id': rec.currency_id.id,
                        'debit': amount,
                        'credit': 0.0,
                        'partner_id': rec.partner_id.id,
                        'account_id': rec.write_off_acc_id.id,
                    }

                new_lines.append(liq_dic)
            return new_lines

    def check_multi_payment(self):
        for rec in self:
            amt = "{:.2f}".format(rec.allocation_amount)
            amt = float(amt)
            if not amt:
                raise ValidationError("Add Allocation Amount in payment item")
            return True

    def dev_generate_moves(self):
        for rec in self:
            is_liq_line = False
            if rec.is_multi_match:
                rec.check_multi_payment()
                line_vals_list = []
                total_amount = rec.amount
                line_allocation_total = 0.0
                for line in rec.payment_line_ids.filtered(lambda m: m.allocation > 0.0):
                    line_allocation_total = line_allocation_total + line.allocation
                    if rec.payment_type == 'inbound':
                        counterpart_amount = -line.allocation
                        if line.invoice_id.move_type == 'out_refund':
                            counterpart_amount = line.allocation
                    elif rec.payment_type == 'outbound':
                        counterpart_amount = line.allocation
                        if line.invoice_id.move_type == 'in_refund':
                            counterpart_amount = -line.allocation
                    else:
                        counterpart_amount = 0.0

                    balance = rec.currency_id._convert(counterpart_amount,
                                                       rec.company_id.currency_id, rec.company_id, rec.date)
                    counterpart_amount_currency = counterpart_amount
                    currency_id = rec.currency_id.id

                    if rec.is_internal_transfer:
                        if rec.payment_type == 'inbound':
                            liquidity_line_name = _('Transfer to %s', rec.journal_id.name)
                        else:  # payment.payment_type == 'outbound':
                            liquidity_line_name = _('Transfer from %s', rec.journal_id.name)
                    else:
                        liquidity_line_name = rec.payment_reference

                    # Compute a default label to set on the journal items.

                    payment_display_name = {
                        'outbound-customer': _("Customer Reimbursement"),
                        'inbound-customer': _("Customer Payment"),
                        'outbound-supplier': _("Vendor Payment"),
                        'inbound-supplier': _("Vendor Reimbursement"),
                    }

                    default_line_name = self.env['account.move.line']._get_default_line_name(
                        _("Internal Transfer") if rec.is_internal_transfer else payment_display_name[
                            '%s-%s' % (rec.payment_type, rec.partner_type)],
                        line.allocation,
                        rec.currency_id,
                        rec.date,
                        partner=rec.partner_id,
                    )

                    # Liquidity line.
                    liq_dic = {}
                    if not is_liq_line:
                        if rec.payment_type == 'inbound':
                            liq_dic = {
                                'name': liquidity_line_name or default_line_name,
                                'date_maturity': rec.date,
                                'amount_currency': -counterpart_amount_currency,
                                'currency_id': currency_id,
                                'debit': balance < 0.0 and rec.amount or 0.0,
                                'credit': balance > 0.0 and balance or 0.0,
                                'partner_id': rec.partner_id.id,
                                'account_id': rec.journal_id.default_account_id.id if balance < 0.0
                                else rec.journal_id.default_account_id.id,
                            }
                        else:
                            liq_dic = {
                                'name': liquidity_line_name or default_line_name,
                                'date_maturity': rec.date,
                                'amount_currency': -counterpart_amount_currency,
                                'currency_id': currency_id,
                                'debit': balance < 0.0 and balance or 0.0,
                                'credit': balance > 0.0 and rec.amount or 0.0,
                                'partner_id': rec.partner_id.id,
                                'account_id': rec.journal_id.default_account_id.id if balance < 0.0
                                else rec.journal_id.default_account_id.id,
                            }

                    # Receivable / Payable.
                    rec_dict = {
                        'name': rec.payment_reference or default_line_name,
                        'date_maturity': rec.date,
                        'amount_currency': counterpart_amount_currency if currency_id else 0.0,
                        'currency_id': currency_id,
                        'debit': balance > 0.0 and balance or 0.0,
                        'credit': balance < 0.0 and -balance or 0.0,
                        'partner_id': rec.partner_id.id,
                        'account_id': rec.destination_account_id.id,
                        'adv_payment_id': line.id,
                    }
                    if not is_liq_line:
                        line_vals_list.append(liq_dic)
                    line_vals_list.append(rec_dict)
                    is_liq_line = True
                total_amount = total_amount - round(line_allocation_total, 2)
                total_amount = round(total_amount, 2)
                if total_amount > 0:
                    n_lines = rec.more_amount_payment_line(total_amount)
                    for n_l in n_lines:
                        line_vals_list.append(n_l)

                if total_amount < 0:
                    n_lines = rec.loss_amount_payment_line(total_amount)
                    for n_l in n_lines:
                        line_vals_list.append(n_l)
                rec.move_id.line_ids.unlink()
                rec.move_id.line_ids = [(0, 0, line_vals) for line_vals in line_vals_list]
                rec.move_id.action_post()
                for line in rec.payment_line_ids.filtered(lambda m: m.allocation > 0.0):
                    invoice_id = line.invoice_id
                    if invoice_id:
                        move_line = self.env['account.move.line'].search(
                            [('move_id', '=', rec.move_id.id), ('adv_payment_id', '=', line.id)])
                        if move_line:
                            invoice_id.js_assign_outstanding_line(move_line.id)
        return True


class AccountPaymentLine(models.Model):
    _name = 'account.payment.line'
    _description = 'Advance Payment Line'

    @api.depends('balance_amount', 'allocation')
    def get_diff_amount(self):
        for line in self:
            line.diff_amt = line.balance_amount - line.allocation

    @api.onchange('full_reconclle')
    def onchange_full_reconclle(self):
        if self.full_reconclle:
            self.allocation = self.balance_amount

    @api.onchange('allocation')
    def onchange_allocation(self):
        if self.allocation:
            if self.allocation >= self.balance_amount:
                self.full_reconclle = True
            else:
                self.full_reconclle = False

    invoice_id = fields.Many2one('account.move', string='Invoice')
    account_id = fields.Many2one('account.account', string="Account")
    date = fields.Date(string="Date")
    due_date = fields.Date(string="Due Date")
    original_amount = fields.Float(string="Original Amount", digits='Product Price')
    balance_amount = fields.Float(string="Balance Amount", digits='Product Price')
    full_reconclle = fields.Boolean(string="Full Reconclle")
    allocation = fields.Float(string="Allocation", digits='Product Price')
    payment_id = fields.Many2one('account.payment')
    diff_amt = fields.Float('Remaining Amount', compute='get_diff_amount', digits='Product Price')
    currency_id = fields.Many2one('res.currency', string='Currency')
    allow_rounding = fields.Char('round')
    cubit_id = fields.Integer(string="Cubit ID")
    writeoff_amount = fields.Float(string="Write-off Amount", digits='Product Price')
