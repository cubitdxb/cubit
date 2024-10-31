# # -*- coding: utf-8 -*-
# from odoo import models, api, fields, _
# from odoo.tools.misc import format_date, get_lang
# def _get_billwise_move_lines(self, account_type, from_date, target_move, period_length):
#     # This method can receive the context key 'include_nullified_amount' {Boolean}
#     # Do an invoice and a payment and unreconcile. The amount will be nullified
#     # By default, the partner wouldn't appear in this report.
#     # The context key allow it to appear
#     periods = {}
#     start = datetime.strptime(str(from_date), "%Y-%m-%d")
#     for i in range(13)[::-1]:
#         stop = start - relativedelta(days=period_length)
#         periods[str(i)] = {
#             'name': (i != 0 and (str((13 - (i + 1)) * period_length) + '-' + str((13 - i) * period_length)) or (
#                         '+' + str(12 * period_length))),
#             'stop': start.strftime('%Y-%m-%d'),
#             'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
#         }
#         start = stop - relativedelta(days=1)
#     res = []
#     total = []
#     cr = self.env.cr
#     company_ids = self.env.context.get('company_ids', (self.env.user.company_id.id,))
#     user_company = self.env.user.company_id
#     user_currency = user_company.currency_id
#     ResCurrency = self.env['res.currency'].with_context(date=from_date)
#     move_state = ['draft', 'posted']
#     if target_move == 'posted':
#         move_state = ['posted']
#     arg_list = (tuple(move_state), tuple(account_type))
#     # build the reconciliation clause to see what partner needs to be printed
#     reconciliation_clause = '(l.reconciled IS FALSE)'
#     cr.execute('SELECT debit_move_id, credit_move_id FROM account_partial_reconcile where create_date > %s',
#                (from_date,))
#     reconciled_after_date = []
#     for row in cr.fetchall():
#         reconciled_after_date += [row[0], row[1]]
#     if reconciled_after_date:
#         reconciliation_clause = '(l.reconciled IS FALSE OR l.id IN %s)'
#         arg_list += (tuple(reconciled_after_date),)
#     arg_list += (from_date, tuple(company_ids))
#     query = '''
#         SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
#         FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
#         WHERE (l.account_id = account_account.id)
#             AND (l.move_id = am.id)
#             AND (am.state IN %s)
#             AND (account_account.internal_type IN %s)
#             AND ''' + reconciliation_clause + '''
#             AND (l.date <= %s)
#             AND l.company_id IN %s
#         ORDER BY UPPER(res_partner.name)'''
#     cr.execute(query, arg_list)
#     partners = cr.dictfetchall()
#     # put a total of 0
#     for i in range(7):
#         total.append(0)
#
#     # Build a string like (1,2,3) for easy use in SQL query
#     partner_ids = [partner['partner_id'] for partner in partners if partner['partner_id']]
#     lines = dict((partner['partner_id'] or False, []) for partner in partners)
#     if not partner_ids:
#         return [], [], {}, periods
#
#     # This dictionary will store the not due amount of all partners
#     undue_amounts = {}
#     query = '''SELECT l.id
#             FROM account_move_line AS l, account_account, account_move am
#             WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
#                 AND (am.state IN %s)
#                 AND (account_account.internal_type IN %s)
#                 AND (COALESCE(l.date_maturity,l.date) >= %s)\
#                 AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
#             AND (l.date <= %s)
#             AND l.company_id IN %s'''
#     cr.execute(query,
#                (tuple(move_state), tuple(account_type), from_date, tuple(partner_ids), from_date, tuple(company_ids)))
#     aml_ids = cr.fetchall()
#     aml_ids = aml_ids and [x[0] for x in aml_ids] or []
#     for line in self.env['account.move.line'].browse(aml_ids):
#         partner_id = line.partner_id.id or False
#         if partner_id not in undue_amounts:
#             undue_amounts[partner_id] = 0.0
#         line_amount = line.balance
#         if line.balance == 0:
#             continue
#         for partial_line in line.matched_debit_ids:
#             if partial_line.max_date <= from_date:
#                 line_amount += partial_line.amount
#         for partial_line in line.matched_credit_ids:
#             if partial_line.max_date <= from_date:
#                 line_amount -= partial_line.amount
#         if not self.env.user.company_id.currency_id.is_zero(line_amount):
#             undue_amounts[partner_id] += line_amount
#             lines[partner_id].append({
#                 'line': line,
#                 'amount': line_amount,
#                 'period': 6,
#             })
#
#     # Use one query per period and store results in history (a list variable)
#     # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
#     history = []
#     for i in range(13):
#         args_list = (tuple(move_state), tuple(account_type), tuple(partner_ids),)
#         dates_query = '(COALESCE(l.date_maturity,l.date)'
#         if periods[str(i)]['start'] and periods[str(i)]['stop']:
#             dates_query += ' BETWEEN %s AND %s)'
#             args_list += (periods[str(i)]['start'], periods[str(i)]['stop'])
#         elif periods[str(i)]['start']:
#             dates_query += ' >= %s)'
#             args_list += (periods[str(i)]['start'],)
#         else:
#             dates_query += ' <= %s)'
#             args_list += (periods[str(i)]['stop'],)
#         args_list += (from_date, tuple(company_ids))
#
#         query = '''SELECT l.id
#                 FROM account_move_line AS l, account_account, account_move am
#                 WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
#                     AND (am.state IN %s)
#                     AND (account_account.internal_type IN %s)
#                     AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
#                     AND ''' + dates_query + '''
#                 AND (l.date <= %s)
#                 AND l.company_id IN %s'''
#         cr.execute(query, args_list)
#         partners_amount = {}
#         aml_ids = cr.fetchall()
#         aml_ids = aml_ids and [x[0] for x in aml_ids] or []
#         for line in self.env['account.move.line'].browse(aml_ids).with_context(prefetch_fields=False):
#             partner_id = line.partner_id.id or False
#             if partner_id not in partners_amount:
#                 partners_amount[partner_id] = 0.0
#             line_amount = ResCurrency._compute(line.company_id.currency_id, user_currency, line.balance)
#             if user_currency.is_zero(line_amount):
#                 continue
#             for partial_line in line.matched_debit_ids:
#                 if partial_line.max_date <= from_date:
#                     line_amount += ResCurrency._compute(partial_line.company_id.currency_id, user_currency,
#                                                         partial_line.amount)
#             for partial_line in line.matched_credit_ids:
#                 if partial_line.max_date <= from_date:
#                     line_amount -= ResCurrency._compute(partial_line.company_id.currency_id, user_currency,
#                                                         partial_line.amount)
#             if not self.env.user.company_id.currency_id.is_zero(line_amount):
#                 partners_amount[partner_id] += line_amount
#                 lines[partner_id].append({
#                     'line': line,
#                     'amount': line_amount,
#                     'period': i + 1,
#                 })
#         history.append(partners_amount)
#     for partner in partners:
#         if partner['partner_id'] is None:
#             partner['partner_id'] = False
#         at_least_one_amount = False
#         values = {}
#         undue_amt = 0.0
#         if partner['partner_id'] in undue_amounts:  # Making sure this partner actually was found by the query
#             undue_amt = undue_amounts[partner['partner_id']]
#
#         total[6] = total[6] + undue_amt
#         values['direction'] = undue_amt
#         if not float_is_zero(values['direction'], precision_rounding=self.env.user.company_id.currency_id.rounding):
#             at_least_one_amount = True
#
#         for i in range(5):
#             during = False
#             if partner['partner_id'] in history[i]:
#                 during = [history[i][partner['partner_id']]]
#             # Adding counter
#             total[(i)] = total[(i)] + (during and during[0] or 0)
#             values[str(i)] = during and during[0] or 0.0
#             if not float_is_zero(values[str(i)], precision_rounding=self.env.user.company_id.currency_id.rounding):
#                 at_least_one_amount = True
#         values['total'] = sum([values['direction']] + [values[str(i)] for i in range(5)])
#         ## Add for total
#         total[(i + 1)] += values['total']
#         values['partner_id'] = partner['partner_id']
#         if partner['partner_id']:
#             browsed_partner = self.env['res.partner'].browse(partner['partner_id'])
#             values['name'] = browsed_partner.name and len(browsed_partner.name) >= 45 and browsed_partner.name[
#                                                                                           0:40] + '...' or browsed_partner.name
#             values['trust'] = browsed_partner.trust
#         else:
#             values['name'] = _('Unknown Partner')
#             values['trust'] = False
#
#         if at_least_one_amount or (self._context.get('include_nullified_amount') and lines[partner['partner_id']]):
#             res.append(values)
#     return res, total, lines, periods


# query='''
#                         SELECT
#                             account_move_line.id, account_move_line.move_id, account_move_line.name, account_move_line.account_id, account_move_line.journal_id, account_move_line.company_id, account_move_line.currency_id, account_move_line.analytic_account_id, account_move_line.display_type, account_move_line.date, account_move_line.debit, account_move_line.credit, account_move_line.balance,
#                             account_move_line.amount_residual_currency as amount_currency,
#                             account_move_line.partner_id AS partner_id,
#                             partner.name AS partner_name,
#                             COALESCE(trust_property.value_text, 'normal') AS partner_trust,
#                             COALESCE(account_move_line.currency_id, journal.currency_id) AS report_currency_id,
#                             account_move_line.payment_id AS payment_id,
#                             COALESCE(account_move_line.date_maturity, account_move_line.date) AS report_date,
#                             move.invoice_date AS invoice_date,
#                             --account_move_line.expected_pay_date AS expected_pay_date,
#                             COALESCE(account_move_line.date_maturity, account_move_line.date) AS expected_pay_date,
#                             move.move_type AS move_type,
#                             move.name AS move_name,
#                             move.ref AS move_ref,
#                             account.code || ' ' || COALESCE(NULLIF(account_tr.value, ''), account.name) AS account_name,
#                             account.code AS account_code,
#                             CASE WHEN period_table.period_index = 0
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period0,
#                             CASE WHEN period_table.period_index = 1
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period1,
#                             CASE WHEN period_table.period_index = 2
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period2,
#                             CASE WHEN period_table.period_index = 3
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period3,
#                             CASE WHEN period_table.period_index = 4
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period4,
#                             CASE WHEN period_table.period_index = 5
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period5,
#                             CASE WHEN period_table.period_index = 6
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period6,
#                             CASE WHEN period_table.period_index = 7
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period7,
#                             CASE WHEN period_table.period_index = 8
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period8,
#                             CASE WHEN period_table.period_index = 9
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period9,
#                             CASE WHEN period_table.period_index = 10
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period10,
#                             CASE WHEN period_table.period_index = 11
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period11,
#                             CASE WHEN period_table.period_index = 12
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period12,
#                             CASE WHEN period_table.period_index = 13
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period13
#                         FROM account_move_line
#                         JOIN account_move move ON account_move_line.move_id = move.id
#                         JOIN account_journal journal ON journal.id = account_move_line.journal_id
#                         JOIN account_account account ON account.id = account_move_line.account_id
#                         LEFT JOIN res_partner partner ON partner.id = account_move_line.partner_id
#                         LEFT JOIN ir_property trust_property ON (
#                             trust_property.res_id = 'res.partner,'|| account_move_line.partner_id
#                             AND trust_property.name = 'trust'
#                             AND trust_property.company_id = account_move_line.company_id
#                         )
#                         JOIN (VALUES (1, 1.0, 2)) AS currency_table(company_id, rate, precision) ON currency_table.company_id = account_move_line.company_id
#                         LEFT JOIN LATERAL (
#                             SELECT part.amount, part.debit_move_id
#                             FROM account_partial_reconcile part
#                             WHERE part.max_date <= %(date)s
#                         ) part_debit ON part_debit.debit_move_id = account_move_line.id
#                         LEFT JOIN LATERAL (
#                             SELECT part.amount, part.credit_move_id
#                             FROM account_partial_reconcile part
#                             WHERE part.max_date <= %(date)s
#                         ) part_credit ON part_credit.credit_move_id = account_move_line.id
#                         JOIN (VALUES (NULL, '2023-06-13', 0),('2023-06-12', '2023-05-14', 1),('2023-05-13', '2023-04-14', 2),('2023-04-13', '2023-03-15', 3),('2023-03-14', '2023-02-13', 4),('2023-02-12', '2023-01-14', 5),('2023-01-13', '2022-12-15', 6),('2022-12-14', '2022-11-15', 7),('2022-11-14', '2022-10-16', 8),('2022-10-15', '2022-09-16', 9),('2022-09-15', '2022-08-17', 10),('2022-08-16', '2022-07-18', 11),('2022-07-17', '2022-06-18', 12),('2022-06-17', NULL, 13)) AS period_table(date_start, date_stop, period_index) ON (
#                             period_table.date_start IS NULL
#                             OR move.invoice_date <= DATE(period_table.date_start)
#                         )
#                         AND (
#                             period_table.date_stop IS NULL
#                             OR move.invoice_date >= DATE(period_table.date_stop)
#                         )
#                         LEFT JOIN ir_translation account_tr ON (
#                             account_tr.name = 'account.account,name'
#                             AND account_tr.res_id = account.id
#                             AND account_tr.type = 'model'
#                             AND account_tr.lang = %(lang)s
#                         )
#                         WHERE account.internal_type = %(account_type)s
#                         AND account.exclude_from_aged_reports IS NOT TRUE
#                         GROUP BY account_move_line.id, partner.id, trust_property.id, journal.id, move.id, account.id,
#                                  period_table.period_index, currency_table.rate, currency_table.precision, account_name
#                         HAVING ROUND(account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0), currency_table.precision) != 0
#                     '''


{'account_type': 'receivable', 'date': '2023-06-13', 'lang': 'en_US', 'sign': 1}
#
# from dateutil.relativedelta import relativedelta
# from itertools import chain
#
#
#
# class ReportAccountAgedPartner(models.AbstractModel):
#     _inherit = "account.aged.partner"
#
#     def _get_hierarchy_details(self, options):
#         if self.env.context.get('model') == "account.aged.payable.invoice.number" or self.env.context.get(
#             'model') == "account.aged.receivable.invoice.number":
#             return [
#                 self._hierarchy_level('account_id', foldable=True, namespan=len(self._get_column_details(options)) - 7),
#                 self._hierarchy_level('id'),
#             ]
#         else:
#             return [
#             self._hierarchy_level('partner_id', foldable=True, namespan=len(self._get_column_details(options)) - 7),
#             self._hierarchy_level('id'),
#         ]
#
#
#     @api.model
#     def _get_sql(self):
#         if self.env.context.get('model') == "account.aged.payable.invoice.date" or self.env.context.get(
#                 'model') == "account.aged.receivable.invoice.date":
#             options = self.env.context['report_options']
#             query = ("""
#                         SELECT
#                             {move_line_fields},
#                             account_move_line.amount_residual_currency as amount_currency,
#                             account_move_line.partner_id AS partner_id,
#                             partner.name AS partner_name,
#                             COALESCE(trust_property.value_text, 'normal') AS partner_trust,
#                             COALESCE(account_move_line.currency_id, journal.currency_id) AS report_currency_id,
#                             account_move_line.payment_id AS payment_id,
#                             COALESCE(account_move_line.date_maturity, account_move_line.date) AS report_date,
#                             move.invoice_date AS invoice_date,
#                             --account_move_line.expected_pay_date AS expected_pay_date,
#                             COALESCE(account_move_line.date_maturity, account_move_line.date) AS expected_pay_date,
#                             move.move_type AS move_type,
#                             move.name AS move_name,
#                             move.ref AS move_ref,
#                             account.code || ' ' || COALESCE(NULLIF(account_tr.value, ''), account.name) AS account_name,
#                             account.code AS account_code,""" + ','.join([("""
#                             CASE WHEN period_table.period_index = {i}
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period{i}""").format(i=i) for i in range(14)]) + """
#                         FROM account_move_line
#                         JOIN account_move move ON account_move_line.move_id = move.id
#                         JOIN account_journal journal ON journal.id = account_move_line.journal_id
#                         JOIN account_account account ON account.id = account_move_line.account_id
#                         LEFT JOIN res_partner partner ON partner.id = account_move_line.partner_id
#                         LEFT JOIN ir_property trust_property ON (
#                             trust_property.res_id = 'res.partner,'|| account_move_line.partner_id
#                             AND trust_property.name = 'trust'
#                             AND trust_property.company_id = account_move_line.company_id
#                         )
#                         JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
#                         LEFT JOIN LATERAL (
#                             SELECT part.amount, part.debit_move_id
#                             FROM account_partial_reconcile part
#                             WHERE part.max_date <= %(date)s
#                         ) part_debit ON part_debit.debit_move_id = account_move_line.id
#                         LEFT JOIN LATERAL (
#                             SELECT part.amount, part.credit_move_id
#                             FROM account_partial_reconcile part
#                             WHERE part.max_date <= %(date)s
#                         ) part_credit ON part_credit.credit_move_id = account_move_line.id
#                         JOIN {period_table} ON (
#                             period_table.date_start IS NULL
#                             OR move.invoice_date <= DATE(period_table.date_start)
#                         )
#                         AND (
#                             period_table.date_stop IS NULL
#                             OR move.invoice_date >= DATE(period_table.date_stop)
#                         )
#                         LEFT JOIN ir_translation account_tr ON (
#                             account_tr.name = 'account.account,name'
#                             AND account_tr.res_id = account.id
#                             AND account_tr.type = 'model'
#                             AND account_tr.lang = %(lang)s
#                         )
#                         WHERE account.internal_type = %(account_type)s
#                         AND account.exclude_from_aged_reports IS NOT TRUE
#                         GROUP BY account_move_line.id, partner.id, trust_property.id, journal.id, move.id, account.id,
#                                  period_table.period_index, currency_table.rate, currency_table.precision, account_name
#                         HAVING ROUND(account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0), currency_table.precision) != 0
#                     """).format(
#                 move_line_fields=self._get_move_line_fields('account_move_line'),
#                 currency_table=self.env['res.currency']._get_query_currency_table(options),
#                 period_table=self._get_query_period_table(options),
#             )
#
#         elif self.env.context.get('model') == "account.aged.payable.invoice.number" or self.env.context.get(
#                 'model') == "account.aged.receivable.invoice.number":
#             options = self.env.context['report_options']
#             query = ("""
#                         SELECT
#                             {move_line_fields},
#                             account_move_line.amount_residual_currency as amount_currency,
#                             account_move_line.partner_id AS partner_id,
#                             max(partner.name) AS partner_name,
#                             COALESCE(trust_property.value_text, 'normal') AS partner_trust,
#                             COALESCE(account_move_line.currency_id, journal.currency_id) AS report_currency_id,
#                             account_move_line.payment_id AS payment_id,
#                             COALESCE(account_move_line.date_maturity, account_move_line.date) AS report_date,
#                             move.invoice_date AS invoice_date,
#                             --account_move_line.expected_pay_date AS expected_pay_date,
#                             COALESCE(account_move_line.date_maturity, account_move_line.date) AS expected_pay_date,
#                             move.move_type AS move_type,
#                             move.name AS move_name,
#                             move.name AS amount_total,
#                             move.name AS amount_paid,
#                             move.ref AS move_ref,
#                             account.code || ' ' || COALESCE(NULLIF(account_tr.value, ''), account.name) AS account_name,
#                             account.code AS account_code,""" + ','.join([("""
#                             CASE WHEN period_table.period_index = {i}
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period{i}""").format(i=i) for i in range(14)]) + """
#                         FROM account_move_line
#                         JOIN account_move move ON account_move_line.move_id = move.id
#                         JOIN account_journal journal ON journal.id = account_move_line.journal_id
#                         JOIN account_account account ON account.id = account_move_line.account_id
#                         LEFT JOIN res_partner partner ON partner.id = account_move_line.partner_id
#                         LEFT JOIN ir_property trust_property ON (
#                             trust_property.res_id = 'res.partner,'|| account_move_line.partner_id
#                             AND trust_property.name = 'trust'
#                             AND trust_property.company_id = account_move_line.company_id
#                         )
#                         JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
#                         LEFT JOIN LATERAL (
#                             SELECT part.amount, part.debit_move_id
#                             FROM account_partial_reconcile part
#                             WHERE part.max_date <= %(date)s
#                         ) part_debit ON part_debit.debit_move_id = account_move_line.id
#                         LEFT JOIN LATERAL (
#                             SELECT part.amount, part.credit_move_id
#                             FROM account_partial_reconcile part
#                             WHERE part.max_date <= %(date)s
#                         ) part_credit ON part_credit.credit_move_id = account_move_line.id
#                         JOIN {period_table} ON (
#                             period_table.date_start IS NULL
#                             OR move.invoice_date <= DATE(period_table.date_start)
#                         )
#                         AND (
#                             period_table.date_stop IS NULL
#                             OR move.invoice_date >= DATE(period_table.date_stop)
#                         )
#                         LEFT JOIN ir_translation account_tr ON (
#                             account_tr.name = 'account.account,name'
#                             AND account_tr.res_id = account.id
#                             AND account_tr.type = 'model'
#                             AND account_tr.lang = %(lang)s
#                         )
#                         WHERE account.internal_type = %(account_type)s
#                         AND account.exclude_from_aged_reports IS NOT TRUE
#                         GROUP BY move.id,account_move_line.id, partner.id, trust_property.id, journal.id, account.id,
#                                  period_table.period_index, currency_table.rate, currency_table.precision, account_name
#                         HAVING ROUND(account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0), currency_table.precision) != 0
#                         order by move.id
#                     """).format(
#                 move_line_fields=self._get_move_line_fields('account_move_line'),
#                 currency_table=self.env['res.currency']._get_query_currency_table(options),
#                 period_table=self._get_query_period_table(options),
#             )
#
#
#         else:
#             options = self.env.context['report_options']
#             query = ("""
#                         SELECT
#                             {move_line_fields},
#                             account_move_line.amount_residual_currency as amount_currency,
#                             account_move_line.partner_id AS partner_id,
#                             partner.name AS partner_name,
#                             COALESCE(trust_property.value_text, 'normal') AS partner_trust,
#                             COALESCE(account_move_line.currency_id, journal.currency_id) AS report_currency_id,
#                             account_move_line.payment_id AS payment_id,
#                             COALESCE(account_move_line.date_maturity, account_move_line.date) AS report_date,
#                             move.invoice_date AS invoice_date,
#                             --move.invoice_date AS invoice_date,
#                             --account_move_line.expected_pay_date AS expected_pay_date,
#                             COALESCE(account_move_line.date_maturity, account_move_line.date) AS expected_pay_date,
#                             move.move_type AS move_type,
#                             move.name AS move_name,
#                             move.ref AS move_ref,
#                             account.code || ' ' || COALESCE(NULLIF(account_tr.value, ''), account.name) AS account_name,
#                             account.code AS account_code,""" + ','.join([("""
#                             CASE WHEN period_table.period_index = {i}
#                             THEN %(sign)s * ROUND((
#                                 account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
#                             ) * currency_table.rate, currency_table.precision)
#                             ELSE 0 END AS period{i}""").format(i=i) for i in range(14)]) + """
#                         FROM account_move_line
#                         JOIN account_move move ON account_move_line.move_id = move.id
#                         JOIN account_journal journal ON journal.id = account_move_line.journal_id
#                         JOIN account_account account ON account.id = account_move_line.account_id
#                         LEFT JOIN res_partner partner ON partner.id = account_move_line.partner_id
#                         LEFT JOIN ir_property trust_property ON (
#                             trust_property.res_id = 'res.partner,'|| account_move_line.partner_id
#                             AND trust_property.name = 'trust'
#                             AND trust_property.company_id = account_move_line.company_id
#                         )
#                         JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
#                         LEFT JOIN LATERAL (
#                             SELECT part.amount, part.debit_move_id
#                             FROM account_partial_reconcile part
#                             WHERE part.max_date <= %(date)s
#                         ) part_debit ON part_debit.debit_move_id = account_move_line.id
#                         LEFT JOIN LATERAL (
#                             SELECT part.amount, part.credit_move_id
#                             FROM account_partial_reconcile part
#                             WHERE part.max_date <= %(date)s
#                         ) part_credit ON part_credit.credit_move_id = account_move_line.id
#                         JOIN {period_table} ON (
#                             period_table.date_start IS NULL
#                             OR COALESCE(account_move_line.date_maturity, account_move_line.date) <= DATE(period_table.date_start)
#                         )
#                         AND (
#                             period_table.date_stop IS NULL
#                             OR COALESCE(account_move_line.date_maturity, account_move_line.date) >= DATE(period_table.date_stop)
#                         )
#                         LEFT JOIN ir_translation account_tr ON (
#                             account_tr.name = 'account.account,name'
#                             AND account_tr.res_id = account.id
#                             AND account_tr.type = 'model'
#                             AND account_tr.lang = %(lang)s
#                         )
#                         WHERE account.internal_type = %(account_type)s
#                         AND account.exclude_from_aged_reports IS NOT TRUE
#                         GROUP BY account_move_line.id, partner.id, trust_property.id, journal.id, move.id, account.id,
#                                  period_table.period_index, currency_table.rate, currency_table.precision, account_name
#                         HAVING ROUND(account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0), currency_table.precision) != 0
#                     """).format(
#                 move_line_fields=self._get_move_line_fields('account_move_line'),
#                 currency_table=self.env['res.currency']._get_query_currency_table(options),
#                 period_table=self._get_query_period_table(options),
#             )
#         params = {
#             'account_type': options['filter_account_type'],
#             'sign': 1 if options['filter_account_type'] == 'receivable' else -1,
#             'date': options['date']['date_to'],
#             'lang': self.env.user.lang or get_lang(self.env).code,
#         }
#         return self.env.cr.mogrify(query, params).decode(self.env.cr.connection.encoding)
#
#     @api.model
#     def _get_column_details(self, options):
#         if self.env.context.get('model') == "account.aged.payable.invoice.date" or self.env.context.get(
#                 'model') == "account.aged.receivable.invoice.date":
#             columns = [
#                 self._header_column(),
#                 self._field_column('invoice_date'),
#                 self._field_column('account_name', name=_("Account"), ellipsis=True),
#                 self._field_column('expected_pay_date'),
#                 self._field_column('period0', name=_("As of: %s", format_date(self.env, options['date']['date_to']))),
#                 self._field_column('period1', sortable=True),
#                 self._field_column('period2', sortable=True),
#                 self._field_column('period3', sortable=True),
#                 self._field_column('period4', sortable=True),
#
#                 self._field_column('period5', sortable=True),
#
#                 self._field_column('period6', sortable=True),
#                 self._field_column('period7', sortable=True),
#                 self._field_column('period8', sortable=True),
#                 self._field_column('period9', sortable=True),
#                 self._field_column('period10', sortable=True),
#                 self._field_column('period11', sortable=True),
#                 self._field_column('period12', sortable=True),
#                 self._field_column('period13', sortable=True),
#
#                 self._custom_column(  # Avoid doing twice the sub-select in the view
#                     name=_('Total'),
#                     classes=['number'],
#                     formatter=self.format_value,
#                     getter=(
#                         lambda v: v['period0'] + v['period1'] + v['period2'] + v['period3'] + v['period4'] + v[
#                             'period5'] +
#                                   v['period6'] + v['period7'] + v['period8'] + v['period9'] + v['period10'] + v[
#                                       'period11'] +
#                                   + v['period12'] + v['period13']
#                     ),
#                     sortable=True,
#                 ),
#             ]
#         elif self.env.context.get('model') == "account.aged.payable.invoice.number" or self.env.context.get(
#                 'model') == "account.aged.receivable.invoice.number":
#             columns = [
#                 self._header_column(),
#                 self._field_column('invoice_date'),
#                 # self._field_column('account_name', name=_("Account"), ellipsis=True),
#                 # self._field_column('expected_pay_date'),
#                 self._field_column('move_name'),
#                 self._field_column('move_ref'),
#                 self._field_column('expected_pay_date'),
#                 # self._field_column('amount_total'),
#                 # self._field_column('amount_paid'),
#
#                 self._field_column('period0', name=_("As of: %s", format_date(self.env, options['date']['date_to']))),
#                 self._field_column('period1', sortable=True),
#                 self._field_column('period2', sortable=True),
#                 self._field_column('period3', sortable=True),
#                 self._field_column('period4', sortable=True),
#
#                 self._field_column('period5', sortable=True),
#
#                 self._field_column('period6', sortable=True),
#                 self._field_column('period7', sortable=True),
#                 self._field_column('period8', sortable=True),
#                 self._field_column('period9', sortable=True),
#                 self._field_column('period10', sortable=True),
#                 self._field_column('period11', sortable=True),
#                 self._field_column('period12', sortable=True),
#                 self._field_column('period13', sortable=True),
#
#                 self._custom_column(  # Avoid doing twice the sub-select in the view
#                     name=_('Total'),
#                     classes=['number'],
#                     formatter=self.format_value,
#                     getter=(
#                         lambda v: v['period0'] + v['period1'] + v['period2'] + v['period3'] + v['period4'] + v[
#                             'period5'] +
#                                   v['period6'] + v['period7'] + v['period8'] + v['period9'] + v['period10'] + v[
#                                       'period11'] +
#                                   + v['period12'] + v['period13']
#                     ),
#                     sortable=True,
#                 ),
#             ]
#         else:
#             columns = [
#                 self._header_column(),
#                 self._field_column('report_date'),
#
#                 self._field_column('account_name', name=_("Account"), ellipsis=True),
#                 self._field_column('expected_pay_date'),
#                 self._field_column('period0', name=_("As of: %s", format_date(self.env, options['date']['date_to']))),
#                 self._field_column('period1', sortable=True),
#                 self._field_column('period2', sortable=True),
#                 self._field_column('period3', sortable=True),
#                 self._field_column('period4', sortable=True),
#
#                 self._field_column('period5', sortable=True),
#
#                 self._field_column('period6', sortable=True),
#                 self._field_column('period7', sortable=True),
#                 self._field_column('period8', sortable=True),
#                 self._field_column('period9', sortable=True),
#                 self._field_column('period10', sortable=True),
#                 self._field_column('period11', sortable=True),
#                 self._field_column('period12', sortable=True),
#                 self._field_column('period13', sortable=True),
#
#                 self._custom_column(  # Avoid doing twice the sub-select in the view
#                     name=_('Total'),
#                     classes=['number'],
#                     formatter=self.format_value,
#                     getter=(
#                         lambda v: v['period0'] + v['period1'] + v['period2'] + v['period3'] + v['period4'] + v[
#                             'period5'] +
#                                   v['period6'] + v['period7'] + v['period8'] + v['period9'] + v['period10'] + v[
#                                       'period11'] +
#                                   + v['period12'] + v['period13']
#                     ),
#                     sortable=True,
#                 ),
#             ]
#
#         if self.user_has_groups('base.group_multi_currency'):
#             columns[2:2] = [
#                 self._field_column('amount_currency'),
#                 self._field_column('currency_id'),
#             ]
#         return columns
#
#
# class ReportAccountAgedReceivableNumber(models.Model):
#     _name = 'account.aged.receivable.invoice.number'
#     _description = "Aged Receivable By Invoice Number"
#     _inherit = "account.aged.partner"
#     _auto = False
#
#     def _get_options(self, previous_options=None):
#         # OVERRIDE
#         options = super(ReportAccountAgedReceivableNumber, self)._get_options(previous_options=previous_options)
#         options['filter_account_type'] = 'receivable'
#         options['date'].update({
#
#             'enable_interval': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'enable_interval') or True,
#             'interval': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval') or 30,
#             'interval2': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval2') or 30,
#             'interval3': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval3') or 30,
#             'interval4': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval4') or 30,
#             'interval5': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval5') or 30,
#             'interval6': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval6') or 30,
#             'interval7': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval7') or 30,
#             'interval8': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval8') or 30,
#             'interval9': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval9') or 30,
#             'interval10': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval10') or 30,
#             'interval11': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval11') or 30,
#             'interval12': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval12') or 30,
#             'interval13': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval13') or 30,
#
#         })
#         return options
#
#     @api.model
#     def _get_report_name(self):
#         return _("Aged Receivable")
#
#     @api.model
#     def _get_templates(self):
#         # OVERRIDE
#         templates = super(ReportAccountAgedReceivableNumber, self)._get_templates()
#         templates['line_template'] = 'account_reports.line_template_aged_receivable_report'
#         return templates
#
#
# class ReportAccountAgedPayableNumber(models.Model):
#     _name = "account.aged.payable.invoice.number"
#     _description = "Aged Payable By Invoice Numbet"
#     _inherit = "account.aged.partner"
#     _auto = False
#
#     def _get_options(self, previous_options=None):
#         # OVERRIDE
#         options = super(ReportAccountAgedPayableNumber, self)._get_options(previous_options=previous_options)
#         options['filter_account_type'] = 'payable'
#         options['date'].update({
#
#             'enable_interval': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'enable_interval') or True,
#             'interval': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval') or 30,
#             'interval2': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval2') or 30,
#             'interval3': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval3') or 30,
#             'interval4': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval4') or 30,
#             'interval5': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval5') or 30,
#             'interval6': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval6') or 30,
#             'interval7': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval7') or 30,
#             'interval8': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval8') or 30,
#             'interval9': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval9') or 30,
#             'interval10': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval10') or 30,
#             'interval11': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval11') or 30,
#             'interval12': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval12') or 30,
#
#             'interval13': previous_options and previous_options.get('date') and previous_options['date'].get(
#                 'interval13') or 30,
#
#         })
#         return options
#
#     @api.model
#     def _get_report_name(self):
#         return _("Aged Payable")
#
#     @api.model
#     def _get_templates(self):
#         # OVERRIDE
#         templates = super(ReportAccountAgedPayableNumber, self)._get_templates()
#         templates['line_template'] = 'account_reports.line_template_aged_payable_report'
#         return templates
