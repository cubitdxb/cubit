##############################################################################
from odoo import models,fields,api,_


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'


    def button_confirm_cash(self, cr, uid, ids, context=None):
        absl_proxy = self.pool.get('account.bank.statement.line')

        TABLES = ((_('Profit'), 'profit_account_id'), (_('Loss'), 'loss_account_id'),)

        for obj in self.browse(cr, uid, ids, context=context):
            if obj.difference == 0.0:
                continue
            elif obj.difference < 0.0:
                account = obj.journal_id.loss_account_id
                name = _('Loss')
                if not obj.journal_id.loss_account_id:
                    raise osv.except_osv(_('Error!'), _('There is no Loss Account on the journal %s.') % (obj.journal_id.name,))
            else: # obj.difference > 0.0
                account = obj.journal_id.profit_account_id
                name = _('Profit')
                if not obj.journal_id.profit_account_id:
                    raise osv.except_osv(_('Error!'), _('There is no Profit Account on the journal %s.') % (obj.journal_id.name,))

            values = {
                'statement_id' : obj.id,
                'journal_id' : obj.journal_id.id,
                'account_id' : account.id,
                'amount' : obj.difference,
                'name' : name,
            }
            absl_proxy.create(cr, uid, values, context=context)

        return super(account_cash_statement, self).button_confirm_bank(cr, uid, ids, context=context)


    def _update_balances(self, cr, uid, ids, context=None):
        """
            Set starting and ending balances according to pieces count
        """
        res = {}
        for statement in self.browse(cr, uid, ids, context=context):
            if (statement.journal_id.type not in ('cash',)):
                continue
            if not statement.journal_id.cash_control:
                prec = self.pool['decimal.precision'].precision_get(cr, uid, 'Account')
                if float_compare(statement.balance_end_real, statement.balance_end, precision_digits=prec):
                    statement.write({'balance_end_real' : statement.balance_end})
                continue
            start = end = 0
            for line in statement.details_ids:
                start += line.subtotal_opening
                end += line.subtotal_closing
            data = {
                'balance_start': start,
                'balance_end_real': end,
            }
            res[statement.id] = data
            super(account_cash_statement, self).write(cr, uid, [statement.id], data, context=context)
        return res

    def _get_sum_entry_encoding(self, cr, uid, ids, name, arg, context=None):

        """ Find encoding total of statements "
        @param name: Names of fields.
        @param arg: User defined arguments
        @return: Dictionary of values.
        """
        res = {}
        for statement in self.browse(cr, uid, ids, context=context):
            res[statement.id] = sum((line.amount for line in statement.line_ids), 0.0)
        return res

    def _get_company(self, cr, uid, context=None):
        user_pool = self.pool.get('res.users')
        company_pool = self.pool.get('res.company')
        user = user_pool.browse(cr, uid, uid, context=context)
        company_id = user.company_id
        if not company_id:
            company_id = company_pool.search(cr, uid, [])
        return company_id and company_id[0] or False

    def _get_statement_from_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.bank.statement.line').browse(cr, uid, ids, context=context):
            result[line.statement_id.id] = True
        return result.keys()

    def _compute_difference(self, cr, uid, ids, fieldnames, args, context=None):
        result =  dict.fromkeys(ids, 0.0)

        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.balance_end_real - obj.balance_end

        return result

    def _compute_last_closing_balance(self, cr, uid, ids, fieldnames, args, context=None):
        result = dict.fromkeys(ids, 0.0)

        for obj in self.browse(cr, uid, ids, context=context):
            if obj.state == 'draft':
                statement_ids = self.search(cr, uid,
                    [('journal_id', '=', obj.journal_id.id),('state', '=', 'confirm')],
                    order='create_date desc',
                    limit=1,
                    context=context
                )

                if not statement_ids:
                    continue
                else:
                    st = self.browse(cr, uid, statement_ids[0], context=context)
                    result[obj.id] = st.balance_end_real

        return result

    def onchange_journal_id(self, cr, uid, ids, journal_id, context=None):
        result = super(account_cash_statement, self).onchange_journal_id(cr, uid, ids, journal_id)

        if not journal_id:
            return result

        statement_ids = self.search(cr, uid,
                [('journal_id', '=', journal_id),('state', '=', 'confirm')],
                order='create_date desc',
                limit=1,
                context=context
        )

        opening_details_ids = self._get_cash_open_box_lines(cr, uid, journal_id, context)
        if opening_details_ids:
            result['value']['opening_details_ids'] = opening_details_ids

        if not statement_ids:
            return result

        st = self.browse(cr, uid, statement_ids[0], context=context)
        result.setdefault('value', {}).update({'last_closing_balance' : st.balance_end_real})

        return result

    _columns = {
        'total_entry_encoding': fields.function(_get_sum_entry_encoding, string="Total Transactions",
            store = {
                'account.bank.statement': (lambda self, cr, uid, ids, context=None: ids, ['line_ids','move_line_ids'], 10),
                'account.bank.statement.line': (_get_statement_from_line, ['amount'], 10),
            },
            help="Total of cash transaction lines."),
        'closing_date': fields.datetime("Closed On"),
        'details_ids' : fields.one2many('account.cashbox.line', 'bank_statement_id', string='CashBox Lines', copy=True),
        'opening_details_ids' : fields.one2many('account.cashbox.line', 'bank_statement_id', string='Opening Cashbox Lines'),
        'closing_details_ids' : fields.one2many('account.cashbox.line', 'bank_statement_id', string='Closing Cashbox Lines'),
        'user_id': fields.many2one('res.users', 'Responsible', required=False),
        'difference' : fields.function(_compute_difference, method=True, string="Difference", type="float", help="Difference between the theoretical closing balance and the real closing balance."),
        'last_closing_balance' : fields.function(_compute_last_closing_balance, method=True, string='Last Closing Balance', type='float'),
    }
    _defaults = {
        'state': 'draft',
        'date': lambda self, cr, uid, context={}: context.get('date', time.strftime("%Y-%m-%d %H:%M:%S")),
        'user_id': lambda self, cr, uid, context=None: uid,
    }

    def _get_cash_open_box_lines(self, cr, uid, journal_id, context):
        details_ids = []
        if not journal_id:
            return details_ids
        journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
        if journal and (journal.type == 'cash'):
            last_pieces = None

            if journal.with_last_closing_balance == True:
                domain = [('journal_id', '=', journal.id),
                          ('state', '=', 'confirm')]
                last_bank_statement_ids = self.search(cr, uid, domain, limit=1, order='create_date desc', context=context)
                if last_bank_statement_ids:
                    last_bank_statement = self.browse(cr, uid, last_bank_statement_ids[0], context=context)

                    last_pieces = dict(
                        (line.pieces, line.number_closing) for line in last_bank_statement.details_ids
                    )
            for value in journal.cashbox_line_ids:
                nested_values = {
                    'number_closing' : 0,
                    'number_opening' : last_pieces.get(value.pieces, 0) if isinstance(last_pieces, dict) else 0,
                    'pieces' : value.pieces
                }
                details_ids.append([0, False, nested_values])
        return details_ids

    def create(self, cr, uid, vals, context=None):
        journal_id = vals.get('journal_id')
        if journal_id and not vals.get('opening_details_ids'):
            vals['opening_details_ids'] = vals.get('opening_details_ids') or self._get_cash_open_box_lines(cr, uid, journal_id, context)
        res_id = super(account_cash_statement, self).create(cr, uid, vals, context=context)
        self._update_balances(cr, uid, [res_id], context)
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        """
        Update redord(s) comes in {ids}, with new value comes as {vals}
        return True on success, False otherwise

        @param cr: cursor to database
        @param user: id of current user
        @param ids: list of record ids to be update
        @param vals: dict of new values to be set
        @param context: context arguments, like lang, time zone

        @return: True on success, False otherwise
        """
        if vals.get('journal_id', False):
            cashbox_line_obj = self.pool.get('account.cashbox.line')
            cashbox_ids = cashbox_line_obj.search(cr, uid, [('bank_statement_id', 'in', ids)], context=context)
            cashbox_line_obj.unlink(cr, uid, cashbox_ids, context)
        res = super(account_cash_statement, self).write(cr, uid, ids, vals, context=context)
        self._update_balances(cr, uid, ids, context)
        return res

    def _user_allow(self, cr, uid, statement_id, context=None):
        return True

    def button_open(self, cr, uid, ids, context=None):
        """ Changes statement state to Running.
        @return: True
        """
        obj_seq = self.pool.get('ir.sequence')
        if context is None:
            context = {}
        statement_pool = self.pool.get('account.bank.statement')
        for statement in statement_pool.browse(cr, uid, ids, context=context):
            vals = {}
            if not self._user_allow(cr, uid, statement.id, context=context):
                raise osv.except_osv(_('Error!'), (_('You do not have rights to open this %s journal!') % (statement.journal_id.name, )))

            if statement.name and statement.name == '/':
                c = {'fiscalyear_id': statement.period_id.fiscalyear_id.id}
                if statement.journal_id.sequence_id:
                    st_number = obj_seq.next_by_id(cr, uid, statement.journal_id.sequence_id.id, context=c)
                else:
                    st_number = obj_seq.next_by_code(cr, uid, 'account.cash.statement', context=c)
                vals.update({
                    'name': st_number
                })

            vals.update({
                'state': 'open',
            })
            self.write(cr, uid, [statement.id], vals, context=context)
        return True

    def statement_close(self, cr, uid, ids, journal_type='bank', context=None):
        if journal_type == 'bank':
            return super(account_cash_statement, self).statement_close(cr, uid, ids, journal_type, context)
        vals = {
            'state':'confirm',
            'closing_date': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return self.write(cr, uid, ids, vals, context=context)

    def check_status_condition(self, cr, uid, state, journal_type='bank'):
        if journal_type == 'bank':
            return super(account_cash_statement, self).check_status_condition(cr, uid, state, journal_type)
        return state=='open'

    def button_confirm_cash(self, cr, uid, ids, context=None):
        absl_proxy = self.pool.get('account.bank.statement.line')

        TABLES = ((_('Profit'), 'profit_account_id'), (_('Loss'), 'loss_account_id'),)

        for obj in self.browse(cr, uid, ids, context=context):
            if obj.difference == 0.0:
                continue
            elif obj.difference < 0.0:
                account = obj.journal_id.loss_account_id
                name = _('Loss')
                if not obj.journal_id.loss_account_id:
                    raise osv.except_osv(_('Error!'), _('There is no Loss Account on the journal %s.') % (obj.journal_id.name,))
            else: # obj.difference > 0.0
                account = obj.journal_id.profit_account_id
                name = _('Profit')
                if not obj.journal_id.profit_account_id:
                    raise osv.except_osv(_('Error!'), _('There is no Profit Account on the journal %s.') % (obj.journal_id.name,))

            values = {
                'statement_id' : obj.id,
                'journal_id' : obj.journal_id.id,
                'account_id' : account.id,
                'amount' : obj.difference,
                'name' : name,
            }
            absl_proxy.create(cr, uid, values, context=context)

        return super(account_cash_statement, self).button_confirm_bank(cr, uid, ids, context=context)


class cash_Register(models.Model):
    _name = "cash.register"
    _description = "Cash Register"

    journal_id = fields.Many2one('account.journal',string="Journal")
    responsible = fields.Many2one('res.users',string="Responsible")
    date = fields.Date(string="Date")
    closed_on = fields.Date(string="Closed on")
    period = fields.Date(string="Period")




