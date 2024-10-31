# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError

#
#
#     def reconcile(self):
#         for line in self:
#             line.move_id.state = 'posted'
#         res = super().reconcile()
#         return res

class AccountMove(models.Model):
    _inherit = "account.move"

    state = fields.Selection(
        selection_add=[('waiting_approval', 'Waiting For Approval'),
                       ('approved', 'Approved'),
                       ('rejected', 'Rejected')],
        ondelete={'waiting_approval': 'set default', 'approved': 'set default', 'rejected': 'set default'})



class AccountPayment(models.Model):
    _inherit = "account.payment"

    reference = fields.Char(string="Payment Ref", copy=False, tracking=True)
    is_approver = fields.Boolean()

    # def action_post(self):
    #     """Overwrites the _post() to validate the payment in the 'approved' stage too.
    #     Currently Odoo allows payment posting only in draft stage.
    #     """
    #     validation = self._check_payment_approval()
    #     if validation:
    #         if self.state == ('posted', 'cancel', 'waiting_approval', 'rejected'):
    #             raise UserError(_("Only a draft or approved payment can be posted."))
    #         if any(inv.state != 'posted' for inv in self.reconciled_invoice_ids):
    #             raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
    #         self.move_id._post(soft=False)

    def dev_generate_moves(self):
        validation = self._check_payment_approval()
        if validation and self.state:
            if self.state == ('posted', 'cancel', 'waiting_approval', 'rejected'):
                raise UserError(_("Only a draft or approved payment can be posted."))
            if any(inv.state != 'posted' for inv in self.reconciled_invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
            res = super(AccountPayment, self).dev_generate_moves()
            return res

    def action_post(self):

        validation = self._check_payment_approval()
        if validation and self.state:
            if self.state == ('posted', 'cancel', 'waiting_approval', 'rejected'):
                raise UserError(_("Only a draft or approved payment can be posted."))
            if any(inv.state != 'posted' for inv in self.reconciled_invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
            # res = super(AccountPayment, self).action_post()
            if self.state not in ('draft', 'approved'):
                raise UserError(_("Only a draft or approved payment can be posted."))

            payments_need_tx = self.filtered(
                lambda p: p.payment_token_id and not p.payment_transaction_id
            )
            # creating the transaction require to access data on payment acquirers, not always accessible to users
            # able to create payments
            transactions = payments_need_tx.sudo()._create_payment_transaction()

            res = super(AccountPayment, self - payments_need_tx).action_post()

            for tx in transactions:  # Process the transactions with a payment by token
                tx._send_payment_request()

            # Post payments for issued transactions
            transactions._finalize_post_processing()
            payments_tx_done = payments_need_tx.filtered(
                lambda p: p.payment_transaction_id.state == 'done'
            )
            super(AccountPayment, payments_tx_done).action_post()
            payments_tx_not_done = payments_need_tx.filtered(
                lambda p: p.payment_transaction_id.state != 'done'
            )
            payments_tx_not_done.action_cancel()

            return res

    def _check_payment_approval(self):
        if self.state == "draft":
            first_approval = self.env['ir.config_parameter'].sudo().get_param(
                'vox_account_payment_approval.payment_approval')
            if first_approval:
                amount = float(self.env['ir.config_parameter'].sudo().get_param(
                    'vox_account_payment_approval.payment_approval_amount'))
                register_payment_amount = self.amount
                if self.allocation_amount:
                    total_amount = self.allocation_amount
                    payment_amount = total_amount - register_payment_amount
                    # if payment_amount<0:
                    #     payment_amount = -1* payment_amount
                else:
                    total_amount = self.amount_total_in_currency_signed
                    payment_amount = total_amount - register_payment_amount
                # write_off_amount = self.write_off_amount
                if payment_amount > amount and self.is_keep_open == False:
                # if payment_amount > amount:
                    self.write({
                        'state': 'waiting_approval'
                    })
                    self.move_id.write({
                        'state': 'waiting_approval'
                    })
                    self.is_approver = True
                    return False
        return True

    def approve_transfer(self):
        if self.is_approver:
            self.write({
                'state': 'approved'
            })

    def reject_transfer(self):
        if self.is_approver:
            self.write({
                'state': 'rejected'
            })



class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    reference = fields.Char(string="Payment Ref", copy=False, tracking=True)

    def _create_payment_vals_from_wizard(self):
        # OVERRIDE
        payment_vals = super()._create_payment_vals_from_wizard()
        payment_vals['is_keep_open'] = False if self.payment_difference_handling == 'reconcile' else True
        payment_vals['write_off_amount'] = self.payment_difference
        payment_vals['reference'] = self.reference
        return payment_vals