# -*- coding: utf-8 -*-

from odoo import models, fields, api,_




class account_journal(models.Model):
    _inherit = "account.journal"


    show_expense = fields.Boolean(string='Expense')


class AccountMove(models.Model):
    _inherit = "account.move"

    expense_type = fields.Selection([
        ('expense', 'Expense'),
        ('all', 'ALL')
    ], ondelete={'expense': 'cascade'})

    @api.model
    def default_get(self, fields):
        result = super(AccountMove, self).default_get(fields)
        active_id = self._context.get('active_id')
        move_type = self._context.get('default_move_type', 'entry')
        expense_in_move = self._context.get('expense_in_move')
        expense_move_type = self._context.get('default_expense_type', 'expense')
        if expense_move_type == 'expense' and expense_in_move==1:
            journals = self.env['account.journal'].search([('show_expense', '=', True)])
            for journal in journals:
                if 'journal_id' in fields:
                    result['journal_id'] = journal.id
        return result

    # @api.model
    # def _get_default_journal(self):
    #     # res = super()._get_default_journal()
    #     move_type = self._context.get('default_move_type', 'entry')
    #     if move_type=='expense':
    #         journals = self.env['account.journal'].search([('show_expense','=',True)])
    #         for journal in journals:
    #             return self.env['account.journal'].browse(journal.id)
    #             # res = journal
    #             # res.write({'id':journal.id})
    #     return super()._get_default_journal()
    #     ''' Get the default journal.
    #     It could either be passed through the context using the 'default_journal_id' key containing its id,
    #     either be determined by the default type.
    #     '''
    #     move_type = self._context.get('default_move_type', 'entry')
    #     if move_type in self.get_sale_types(include_receipts=True):
    #         journal_types = ['sale']
    #     elif move_type in self.get_purchase_types(include_receipts=True):
    #         journal_types = ['purchase']
    #     else:
    #         journal_types = self._context.get('default_move_journal_types', ['general'])
    #
    #     if self._context.get('default_journal_id'):
    #         journal = self.env['account.journal'].browse(self._context['default_journal_id'])
    #
    #         if move_type != 'entry' and journal.type not in journal_types:
    #             raise UserError(_(
    #                 "Cannot create an invoice of type %(move_type)s with a journal having %(journal_type)s as type.",
    #                 move_type=move_type,
    #                 journal_type=journal.type,
    #             ))
    #     else:
    #         journal = self._search_default_journal(journal_types)
    #
    #     return journal

    def _get_move_display_name(self, show_ref=False):
        ''' Helper to get the display name of an invoice depending of its type.
        :param show_ref:    A flag indicating of the display name must include or not the journal entry reference.
        :return:            A string representing the invoice.
        '''
        self.ensure_one()
        name = ''
        if self.state == 'draft':
            name += {
                'out_invoice': _('Draft Invoice'),
                'out_refund': _('Draft Credit Note'),
                'in_invoice': _('Draft Bill'),
                'in_refund': _('Draft Vendor Credit Note'),
                'out_receipt': _('Draft Sales Receipt'),
                'in_receipt': _('Draft Purchase Receipt'),
                'entry': _('Draft Entry'),
                'expense': _('Draft Expense'),
            }[self.move_type]
            name += ' '
        if not self.name or self.name == '/':
            name += '(* %s)' % str(self.id)
        else:
            name += self.name
        return name + (show_ref and self.ref and ' (%s%s)' % (self.ref[:50], '...' if len(self.ref) > 50 else '') or '')

    # move_type = fields.Selection(selection=[
    #         ('entry', 'Journal Entry'),
    #         ('out_invoice', 'Customer Invoice'),
    #         ('out_refund', 'Customer Credit Note'),
    #         ('in_invoice', 'Vendor Bill'),
    #         ('in_refund', 'Vendor Credit Note'),
    #         ('out_receipt', 'Sales Receipt'),
    #         ('in_receipt', 'Purchase Receipt'),
    #     ], string='Type', required=True, store=True, index=True, readonly=True, tracking=True,
    #     default="entry", change_default=True)
