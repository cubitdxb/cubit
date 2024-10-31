# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from dateutil.relativedelta import relativedelta
from itertools import chain
from odoo.tools.misc import format_date, get_lang



class ReportAccountAgedPartner(models.AbstractModel):
    _inherit = "account.aged.partner"


    period5 = fields.Monetary(string='121 - 150')
    period6 = fields.Monetary(string='151 - 180')
    period7 = fields.Monetary(string='181 - 210')
    period8 = fields.Monetary(string='211 - 240')
    period9 = fields.Monetary(string='241 - 270')
    period10 = fields.Monetary(string='271 - 300')
    period11 = fields.Monetary(string='301 - 330')
    period12 = fields.Monetary(string='331 - 360')
    period13 = fields.Monetary(string='360 above')
    # period5 = fields.Monetary(string='Older')


    @api.model
    def _get_sql(self):
        options = self.env.context['report_options']
        query = ("""
            SELECT
                {move_line_fields},
                account_move_line.amount_residual_currency as amount_currency,
                account_move_line.partner_id AS partner_id,
                partner.name AS partner_name,
                COALESCE(trust_property.value_text, 'normal') AS partner_trust,
                COALESCE(account_move_line.currency_id, journal.currency_id) AS report_currency_id,
                account_move_line.payment_id AS payment_id,
                COALESCE(account_move_line.date_maturity, account_move_line.date) AS report_date,
                --account_move_line.expected_pay_date AS expected_pay_date,
                COALESCE(account_move_line.date_maturity, account_move_line.date) AS expected_pay_date,
                move.move_type AS move_type,
                move.name AS move_name,
                move.ref AS move_ref,
                account.code || ' ' || COALESCE(NULLIF(account_tr.value, ''), account.name) AS account_name,
                account.code AS account_code,""" + ','.join([("""
                CASE WHEN period_table.period_index = {i}
                THEN %(sign)s * ROUND((
                    account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
                ) * currency_table.rate, currency_table.precision)
                ELSE 0 END AS period{i}""").format(i=i) for i in range(14)]) + """
            FROM account_move_line
            JOIN account_move move ON account_move_line.move_id = move.id
            JOIN account_journal journal ON journal.id = account_move_line.journal_id
            JOIN account_account account ON account.id = account_move_line.account_id
            LEFT JOIN res_partner partner ON partner.id = account_move_line.partner_id
            LEFT JOIN ir_property trust_property ON (
                trust_property.res_id = 'res.partner,'|| account_move_line.partner_id
                AND trust_property.name = 'trust'
                AND trust_property.company_id = account_move_line.company_id
            )
            JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN LATERAL (
                SELECT part.amount, part.debit_move_id
                FROM account_partial_reconcile part
                WHERE part.max_date <= %(date)s
            ) part_debit ON part_debit.debit_move_id = account_move_line.id
            LEFT JOIN LATERAL (
                SELECT part.amount, part.credit_move_id
                FROM account_partial_reconcile part
                WHERE part.max_date <= %(date)s
            ) part_credit ON part_credit.credit_move_id = account_move_line.id
            JOIN {period_table} ON (
                period_table.date_start IS NULL
                OR COALESCE(account_move_line.date_maturity, account_move_line.date) <= DATE(period_table.date_start)
            )
            AND (
                period_table.date_stop IS NULL
                OR COALESCE(account_move_line.date_maturity, account_move_line.date) >= DATE(period_table.date_stop)
            )
            LEFT JOIN ir_translation account_tr ON (
                account_tr.name = 'account.account,name'
                AND account_tr.res_id = account.id
                AND account_tr.type = 'model'
                AND account_tr.lang = %(lang)s
            )
            WHERE account.internal_type = %(account_type)s
            AND account.exclude_from_aged_reports IS NOT TRUE
            GROUP BY account_move_line.id, partner.id, trust_property.id, journal.id, move.id, account.id,
                     period_table.period_index, currency_table.rate, currency_table.precision, account_name
            HAVING ROUND(account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0), currency_table.precision) != 0
        """).format(
            move_line_fields=self._get_move_line_fields('account_move_line'),
            currency_table=self.env['res.currency']._get_query_currency_table(options),
            period_table=self._get_query_period_table(options),
        )
        params = {
            'account_type': options['filter_account_type'],
            'sign': 1 if options['filter_account_type'] == 'receivable' else -1,
            'date': options['date']['date_to'],
            'lang': self.env.user.lang or get_lang(self.env).code,
        }
        return self.env.cr.mogrify(query, params).decode(self.env.cr.connection.encoding)

    @api.model
    def _get_query_period_table(self, options):
        def minus_days(date_obj, days):
            return fields.Date.to_string(date_obj - relativedelta(days=days))

        date_str = options['date']['date_to']
        date = fields.Date.from_string(date_str)
        period_values = [
            (False, date_str),
            (minus_days(date, 1), minus_days(date, 30)),
            (minus_days(date, 31), minus_days(date, 60)),
            (minus_days(date, 61), minus_days(date, 90)),
            (minus_days(date, 91), minus_days(date, 120)),
            (minus_days(date, 121), minus_days(date, 150)),
            (minus_days(date, 151), minus_days(date, 180)),
            (minus_days(date, 181), minus_days(date, 210)),
            (minus_days(date, 211), minus_days(date, 240)),
            (minus_days(date, 241), minus_days(date, 270)),
            (minus_days(date, 271), minus_days(date, 300)),
            (minus_days(date, 301), minus_days(date, 330)),
            (minus_days(date, 331), minus_days(date, 360)),
            (minus_days(date, 361), False),
        ]

        period_table = ('(VALUES %s) AS period_table(date_start, date_stop, period_index)' %
                        ','.join("(%s, %s, %s)" for i, period in enumerate(period_values)))
        params = list(chain.from_iterable(
            (period[0] or None, period[1] or None, i)
            for i, period in enumerate(period_values)
        ))
        return self.env.cr.mogrify(period_table, params).decode(self.env.cr.connection.encoding)


    def _show_line(self, report_dict, value_dict, current, options):
        # Don't display an aml report line (except the header) with all zero amounts.
        all_zero = all(
            self.env.company.currency_id.is_zero(value_dict[f])
            for f in ['period0', 'period1', 'period2', 'period3', 'period4','period5','period6','period7','period8','period9',
                      'period10','period11','period12','period13']
            # ,'period13' ]
        ) and not value_dict.get('__count')
        return (report_dict['parent_id'] is None
                or report_dict['parent_id'] == 'total-None'
                or (report_dict['parent_id'] in options.get('unfolded_lines', [])
                or options.get('unfold_all'))
                or not self._get_hierarchy_details(options)[len(current) - 2].foldable) and not all_zero
        # return super()._show_line(report_dict, value_dict, current, options) and not all_zero

    @api.model
    def _get_column_details(self, options):
        columns = [
            self._header_column(),
            self._field_column('report_date'),

            self._field_column('account_name', name=_("Account"), ellipsis=True),
            self._field_column('expected_pay_date'),
            self._field_column('period0', name=_("As of: %s", format_date(self.env, options['date']['date_to']))),
            self._field_column('period1', sortable=True),
            self._field_column('period2', sortable=True),
            self._field_column('period3', sortable=True),
            self._field_column('period4', sortable=True),

            self._field_column('period5', sortable=True),

            self._field_column('period6', sortable=True),
            self._field_column('period7', sortable=True),
            self._field_column('period8', sortable=True),
            self._field_column('period9', sortable=True),
            self._field_column('period10', sortable=True),
            self._field_column('period11', sortable=True),
            self._field_column('period12', sortable=True),
            self._field_column('period13', sortable=True),

            self._custom_column(  # Avoid doing twice the sub-select in the view
                name=_('Total'),
                classes=['number'],
                formatter=self.format_value,
                getter=(
                    lambda v: v['period0'] + v['period1'] + v['period2'] + v['period3'] + v['period4'] + v['period5'] +
                              v['period6'] + v['period7'] + v['period8'] + v['period9'] + v['period10'] + v['period11'] +
                              + v['period12'] + v['period13']
                ),
                sortable=True,
            ),
        ]

        if self.user_has_groups('base.group_multi_currency'):
            columns[2:2] = [
                self._field_column('amount_currency'),
                self._field_column('currency_id'),
            ]
        return columns

    def _get_hierarchy_details(self, options):
        return [
            self._hierarchy_level('partner_id', foldable=True, namespan=len(self._get_column_details(options)) - 15),
            self._hierarchy_level('id'),
        ]


    def _format_total_line(self, res, value_dict, options):
        res['name'] = _('Total')
        res['colspan'] = len(self._get_column_details(options)) - 15
        res['columns'] = res['columns'][res['colspan'] - 1:]


class ReportAccountAgedPayable(models.Model):
    _inherit = "account.aged.payable"


    def _get_options(self, previous_options=None):
        # OVERRIDE
        options = super(ReportAccountAgedPayable, self)._get_options(previous_options)
        options['date'].update({

            'enable_interval': previous_options and previous_options.get('date') and previous_options['date'].get('enable_interval') or True,
            'interval': previous_options and previous_options.get('date') and previous_options['date'].get('interval') or 30,
            'interval2': previous_options and previous_options.get('date') and previous_options['date'].get('interval2') or 30,
            'interval3': previous_options and previous_options.get('date') and previous_options['date'].get('interval3') or 30,
            'interval4': previous_options and previous_options.get('date') and previous_options['date'].get('interval4') or 30,
            'interval5': previous_options and previous_options.get('date') and previous_options['date'].get('interval5') or 30,
            'interval6': previous_options and previous_options.get('date') and previous_options['date'].get('interval6') or 30,
            'interval7': previous_options and previous_options.get('date') and previous_options['date'].get('interval7') or 30,
            'interval8': previous_options and previous_options.get('date') and previous_options['date'].get('interval8') or 30,
            'interval9': previous_options and previous_options.get('date') and previous_options['date'].get('interval9') or 30,
            'interval10': previous_options and previous_options.get('date') and previous_options['date'].get('interval10') or 30,
            'interval11': previous_options and previous_options.get('date') and previous_options['date'].get('interval11') or 30,
            'interval12': previous_options and previous_options.get('date') and previous_options['date'].get('interval12') or 30,
            'interval13': previous_options and previous_options.get('date') and previous_options['date'].get('interval13') or 30,


        })
        return options


class ReportAccountAgedReceivable(models.Model):
    _inherit = "account.aged.receivable"


    def _get_options(self, previous_options=None):
        # OVERRIDE
        options = super(ReportAccountAgedReceivable, self)._get_options(previous_options)
        options['date'].update({

            'enable_interval': previous_options and previous_options.get('date') and previous_options['date'].get('enable_interval') or True,
            'interval': previous_options and previous_options.get('date') and previous_options['date'].get('interval') or 30,
            'interval2': previous_options and previous_options.get('date') and previous_options['date'].get('interval2') or 30,
            'interval3': previous_options and previous_options.get('date') and previous_options['date'].get('interval3') or 30,
            'interval4': previous_options and previous_options.get('date') and previous_options['date'].get('interval4') or 30,
            'interval5': previous_options and previous_options.get('date') and previous_options['date'].get('interval5') or 30,
            'interval6': previous_options and previous_options.get('date') and previous_options['date'].get('interval6') or 30,
            'interval7': previous_options and previous_options.get('date') and previous_options['date'].get('interval7') or 30,
            'interval8': previous_options and previous_options.get('date') and previous_options['date'].get('interval8') or 30,
            'interval9': previous_options and previous_options.get('date') and previous_options['date'].get('interval9') or 30,
            'interval10': previous_options and previous_options.get('date') and previous_options['date'].get('interval10') or 30,
            'interval11': previous_options and previous_options.get('date') and previous_options['date'].get('interval11') or 30,
            'interval12': previous_options and previous_options.get('date') and previous_options['date'].get('interval12') or 30,
            'interval13': previous_options and previous_options.get('date') and previous_options['date'].get('interval13') or 30,


        })
        return options