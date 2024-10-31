# -*- coding: utf-8 -*-

import time
from odoo import models, api, fields
from datetime import datetime
from odoo import _
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.tools import float_is_zero
from dateutil.relativedelta import relativedelta
from itertools import chain
from xlsxwriter.utility import xl_range


class BillWiseBalance(models.AbstractModel):
    _name = 'report.vox_ageing_invoice_number.financial_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    @api.model
    def _get_query_period_table(self, options):
        def minus_days(date_obj, days):
            return fields.Date.to_string(date_obj - relativedelta(days=days))

        # date_str = options['date']['date_to']
        date_str = options
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

    @api.model
    def _get_query_currency_table(self, options):
        ''' Construct the currency table as a mapping company -> rate to convert the amount to the user's company
        currency in a multi-company/multi-currency environment.
        The currency_table is a small postgresql table construct with VALUES.
        :param options: The report options.
        :return:        The query representing the currency table.
        '''

        user_company = self.env.company
        user_currency = user_company.currency_id

        companies = user_company
        currency_rates = {user_currency.id: 1.0}

        conversion_rates = []
        for company in companies:
            conversion_rates.extend((
                company.id,
                currency_rates[user_company.currency_id.id] / currency_rates[company.currency_id.id],
                user_currency.decimal_places,
            ))
        query = '(VALUES %s) AS currency_table(company_id, rate, precision)' % ','.join(
            '(%s, %s, %s)' for i in companies)
        return self.env.cr.mogrify(query, conversion_rates).decode(self.env.cr.connection.encoding)

    def get_sale(self, data):

        lines = []
        sl = 0

        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        target_move = data['form']['target_move']
        period_length = data['form']['period_length']
        result_selection = data['form']['result_selection']

        user_company = self.env.company
        user_currency = user_company.currency_id
        companies = user_company
        currency_rates = {user_currency.id: 1.0}
        account_move_type = []

        if result_selection == 'customer':
            account_type = ['receivable']
            account_move_type = ['out_invoice', 'out_refund']
            sign = 1
        elif result_selection == 'supplier':
            account_type = ['payable']
            account_move_type = ['in_invoice', 'in_refund']
            sign = -1
        # else:
        #     account_type = ['payable', 'receivable']
        # target_move = lines['target_move']
        #
        # 'sign': 1 if options['filter_account_type'] == 'receivable' else -1,

        conversion_rates = []
        company_value = False
        currency_rate = False
        decimal_place = False
        for company in companies:
            company_value = company.id
            currency_rate = currency_rates[user_company.currency_id.id] / currency_rates[company.currency_id.id]
            decimal_place = user_currency.decimal_places

            # conversion_rates.extend((
            #     company.id,
            #     currency_rates[user_company.currency_id.id] / currency_rates[company.currency_id.id],
            #     user_currency.decimal_places,
            # ))

        query = ("""
                    SELECT
                        account_move_line.id, 
                        account_move_line.move_id, 
                        account_move_line.name, 
                        account_move_line.account_id, 
                        account_move_line.journal_id, 
                        account_move_line.company_id, 
                        account_move_line.currency_id,
                        account_move_line.analytic_account_id, 
                        account_move_line.display_type, 
                        account_move_line.date, 
                        account_move_line.debit, 
                        account_move_line.credit, 
                        account_move_line.balance,
                        account_move_line.amount_residual_currency as amount_currency,
                        account_move_line.partner_id AS partner_id,
                        partner.name AS partner_name,
                        COALESCE(trust_property.value_text, 'normal') AS partner_trust,
                        COALESCE(account_move_line.currency_id, journal.currency_id) AS report_currency_id,
                        account_move_line.payment_id AS payment_id,
                        COALESCE(account_move_line.date_maturity, account_move_line.date) AS report_date,
                        move.invoice_date AS invoice_date,
                       -- move.amount_paid AS amount_paid,
                        move.amount_total AS amount_total,
                        move.invoice_user_id AS invoice_user_id,
                        move.lpo_number AS lpo_number,
                        move.invoice_date_due AS invoice_date_due,
                       -- payment.write_off_amount AS write_off_amount,
                        move.invoice_payment_term_id AS invoice_payment_term_id,
                        --move.invoice_date AS invoice_date,
                        --account_move_line.expected_pay_date AS expected_pay_date,
                        COALESCE(account_move_line.date_maturity, account_move_line.date) AS expected_pay_date,
                        move.move_type AS move_type,
                        move.name AS move_name,
                        move.ref AS move_ref,
                        account.code || ' ' || COALESCE(NULLIF(account_tr.value, ''), account.name) AS account_name,
                        account.code AS account_code,""" + ','.join([("""
                        CASE WHEN period_table.period_index = {i}
                        THEN %s * ROUND((
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
                        WHERE part.max_date <= %s
                    ) part_debit ON part_debit.debit_move_id = account_move_line.id
                    LEFT JOIN LATERAL (
                        SELECT part.amount, part.credit_move_id
                        FROM account_partial_reconcile part
                        WHERE part.max_date <= %s
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
                        AND account_tr.lang = %s
                    )
                    WHERE account.internal_type in %s and move.move_type in %s
                    AND account.exclude_from_aged_reports IS NOT TRUE and move.state in ('posted')
                    GROUP BY account_move_line.id, partner.id, trust_property.id, journal.id, move.id, account.id,
                             period_table.period_index, currency_table.rate, currency_table.precision, account_name
                    order by move.name
                """).format(
            currency_table=self._get_query_currency_table(to_date),
            period_table=self._get_query_period_table(to_date),
        )
        # HAVING
        # ROUND(account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0),
        #       currency_table.precision) != 0

        self.env.cr.execute(query, (sign, sign, sign, sign, sign, sign, sign, sign, sign, sign, sign, sign, sign, sign,
                                    to_date, to_date,
                                    self.env.user.lang, tuple(account_type), tuple(account_move_type),

                                    ))

        for row in self.env.cr.dictfetchall():

            sl += 1

            period0 = row['period0'] if row['period0'] else 0.0
            period1 = row['period1'] if row['period1'] else 0.0
            period2 = row['period2'] if row['period2'] else 0.0
            period3 = row['period3'] if row['period3'] else 0.0
            period4 = row['period4'] if row['period4'] else 0.0
            period5 = row['period5'] if row['period5'] else 0.0
            period6 = row['period6'] if row['period6'] else 0.0
            period7 = row['period7'] if row['period7'] else 0.0
            period8 = row['period8'] if row['period8'] else 0.0
            period9 = row['period9'] if row['period9'] else 0.0
            period10 = row['period10'] if row['period10'] else 0.0
            period11 = row['period11'] if row['period11'] else 0.0
            period12 = row['period12'] if row['period12'] else 0.0
            period13 = row['period13'] if row['period13'] else 0.0
            total = period0 + period1 + period2 + period3 + period4 + period5 + period6 + period7 + period8 + period9 + period10 + period11 + period12 + period13

            invoice_date = row['invoice_date'] if row['invoice_date'] else ""
            move_id = row['move_id'] if row['move_id'] else ""
            move_name = row['move_name'] if row['move_name'] else ""
            partner_name = row['partner_name'] if row['partner_name'] else ""
            invoice_user_id = row['invoice_user_id'] if row['invoice_user_id'] else 0
            # amount_paid = row['amount_paid'] if row['amount_paid'] else 0
            amount_total = row['amount_total'] if row['amount_total'] else 0
            invoice_date_due = row['invoice_date_due'] if row['invoice_date_due'] else 0
            payment_id = row['payment_id'] if row['payment_id'] else 0
            # payment_date = row['payment_date'] if row['payment_date'] else 0
            lpo_number = row['lpo_number'] if row['lpo_number'] else ""
            # write_off_amount = row['write_off_amount'] if row['write_off_amount'] else 0
            move_id = self.env['account.move'].browse(int(move_id))

            amount_paid = move_id.amount_paid
            balance = move_id.amount_residual
            payment = self.env['account.payment'].search([('ref','=', move_name),('state', '=', 'posted')])
            write_off_amount = 0
            payment_date_list = []
            payment_date_list_string =""
            if payment:
                for payments in payment:
                    write_off_amount += payments.write_off_amount
                    payment_date = payments.date
                    if payment_date:
                        payment_date_values = datetime.strptime(str(payment_date), '%Y-%m-%d').date()
                        payment_date = payment_date_values.strftime('%d/%m/%Y')
                        payment_date_list.append(payment_date)
                        if payment_date_list:
                            payment_date_list_string = ', '.join(payment_date_list)
                        else:
                            payment_date_list_string = ""

                    else:
                        payment_date = " "
            else:
                write_off_amount = 0
                payment_date = " "

            payment_lines = self.env['account.payment.line'].search([('invoice_id', '=', move_id.id), ('payment_id.state', '=', 'posted')])
            payment_line_date_list = ""
            if payment_lines:
                write_off_amount = 0
                for pay_lines in payment_lines:
                    write_off_amount = pay_lines.writeoff_amount
                    payment_line_date_string = datetime.strptime(str(pay_lines.payment_id.date), '%Y-%m-%d').date()
                    payment_line_date_list = payment_line_date_string.strftime('%d/%m/%Y')
            if payment_date_list_string and payment_line_date_list:
                payment_date_list_string = payment_date_list_string + "," + payment_line_date_list
            else:
                payment_date_list_string = payment_date_list_string + payment_line_date_list
            so_numbers = list(set([l.strip() for l in (payment_date_list_string.split(','))]))
            join_date_number = ', '.join(so_numbers)
            payment_date_list_string = join_date_number

            if invoice_user_id:
                sales_persons = self.env['res.users'].browse(invoice_user_id)
                sales_person = sales_persons.name
            else:
                sales_person = ""
            invoice_payment_term_id = row['invoice_payment_term_id'] if row['invoice_payment_term_id'] else 0
            if invoice_payment_term_id:
                payment_term = self.env['account.payment.term'].browse(invoice_payment_term_id)
                payment_terms = payment_term.name
            else:
                payment_terms = ""
            # balance = row['balance'] if row['balance'] else 0
            if invoice_date:
                date_value = datetime.strptime(str(invoice_date), '%Y-%m-%d').date()
                invoice_date = date_value.strftime('%d/%m/%Y')
            else:
                invoice_date = " "
            if invoice_date_due:
                date_values = datetime.strptime(str(invoice_date_due), '%Y-%m-%d').date()
                invoice_date_due = date_values.strftime('%d/%m/%Y')
            else:
                invoice_date_due = " "

            for row1 in self.env.cr.dictfetchall():
                sl += 1

                period0 = row1['period0'] if row1['period0'] else 0.0
            if invoice_date:
                date_start = data['form']['from_date']
                date_end = data['form']['to_date']
                if date_start:
                    date_object_date_start = datetime.strptime(str(date_start), '%Y-%m-%d').date()
                    date_start_value = date_object_date_start.strftime('%d/%m/%Y')
                if date_end:
                    date_object_date_end = datetime.strptime(str(date_end), '%Y-%m-%d').date()
                    date_end_value = date_object_date_end.strftime('%d/%m/%Y')

                if date_value >= date_object_date_start and date_value <= date_object_date_end:

                    res = {
                        'sl_no': sl,
                        'customer_name': partner_name,
                        'invoice_date': invoice_date if invoice_date else "",
                        'invoice_no': move_name if move_name else " ",
                        'source_document': lpo_number if lpo_number else " ",
                        'sales_person': sales_person if sales_person else " ",
                        'payment_terms': payment_terms if payment_terms else " ",
                        'payment_due_date': invoice_date_due if invoice_date_due else "",
                        'invoice_amount': amount_total if amount_total else 0.0,
                        'amount_paid': amount_paid - write_off_amount if amount_paid else 0.0,
                        'bank_collection_date': payment_date_list_string if payment_date_list_string else "",
                        'write_off': write_off_amount if write_off_amount else 0.0,
                        'balance': balance if balance else 0.0,
                        # 'aging': mrp_value if mrp_value else 0.0,
                        'total': total if total else 0.0,
                        'period0': period0 if period0 else 0.0,
                        'period1': period1 if period1 else 0.0,
                        'period2': period2 if period2 else 0.0,
                        'period3': period3 if period3 else 0.0,
                        'period4': period4 if period4 else 0.0,
                        'period5': period5 if period5 else 0.0,
                        'period6': period6 if period6 else 0.0,
                        'period7': period7 if period7 else 0.0,
                        'period8': period8 if period8 else 0.0,
                        'period9': period9 if period9 else 0.0,
                        'period10': period10 if period10 else 0.0,
                        'period11': period11 if period11 else 0.0,
                        'period12': period12 if period12 else 0.0,
                        'period13': period13 if period13 else 0.0,

                    }

                    lines.append(res)
        if lines:
            return lines
        else:
            return []

    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        currency = self.env.user.company_id.currency_id.symbol or ''
        sheet = workbook.add_worksheet()
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 25)
        sheet.set_column(3, 3, 25)
        sheet.set_column(4, 4, 20)
        sheet.set_column(5, 5, 25)
        sheet.set_column(6, 6, 20)
        sheet.set_column(7, 7, 20)
        sheet.set_column(8, 8, 20)
        sheet.set_column(9, 9, 20)
        sheet.set_column(10, 10, 20)
        sheet.set_column(11, 11, 20)
        sheet.set_column(12, 12, 20)
        sheet.set_column(13, 13, 20)
        sheet.set_column(14, 14, 20)
        sheet.set_column(15, 15, 20)
        sheet.set_column(16, 16, 20)
        sheet.set_column(17, 17, 20)
        sheet.set_column(18, 18, 20)
        sheet.set_column(19, 19, 20)
        sheet.set_column(20, 20, 20)
        sheet.set_column(21, 21, 30)
        sheet.set_column(22, 22, 20)
        sheet.set_column(23, 23, 20)
        sheet.set_column(24, 24, 20)

        format1 = workbook.add_format({'font_size': 16, 'align': 'vcenter', 'bg_color': '#D3D3D3', 'bold': True})
        font_size_8_center = workbook.add_format(
            {'bottom': True, 'top': True, 'left': True, 'font_size': 14, 'align': 'center'})
        font_size_8_left = workbook.add_format(
            {'bottom': True, 'top': True, 'left': True, 'font_size': 14, 'align': 'left'})
        format1.set_font_color('#000080')
        format2 = workbook.add_format({'font_size': 12})
        format3 = workbook.add_format({'font_size': 10, 'bold': True})
        format4 = workbook.add_format({'font_size': 10})
        format5 = workbook.add_format({'font_size': 12, 'bold': True, 'bg_color': '#D3D3D3'})
        format1.set_align('center')
        format2.set_align('left')
        format3.set_align('left')
        format4.set_align('center')
        font_size_8blod = workbook.add_format(
            {'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 14, 'bold': True, })

        sheet.merge_range('A2:AH2', 'TR/TP Report', format1)
        date_start = data['form']['from_date']
        date_end = data['form']['to_date']
        if date_start:
            date_object_date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        if date_end:
            date_object_date_end = datetime.strptime(date_end, '%Y-%m-%d').date()

        # if date_start and date_end:
        #
        #     sheet.merge_range('A5:H5',
        #                       "Date : " + date_object_date_start.strftime(
        #                           '%d-%m-%Y') + " to " + date_object_date_end.strftime(
        #                           '%d-%m-%Y'), font_size_8blod)
        # elif date_start:
        #     sheet.merge_range('A5:H5', "Date : " + date_object_date_start.strftime('%d-%m-%Y'),
        #                       font_size_8blod)

        row = 2
        col = 0
        # try:
        if lines['result_selection'] == 'customer':
            account_type = ['receivable']
        elif lines['result_selection'] == 'supplier':
            account_type = ['payable']
        else:
            account_type = ['payable', 'receivable']
        target_move = lines['target_move']

        form = lines
        # sheet.merge_range(row, col, row, col+2, 'Start Date :', format2)
        # sheet.merge_range(row, col+3, row, col+6, form['from_date'], format2)
        # row += 1
        # sheet.merge_range(row, col, row, col+2, 'Period Length (days) :', format2)
        # sheet.merge_range(row, col+3, row, col+6, form['period_length'], format2)
        row += 1
        account_type = ""
        if form['result_selection'] == 'customer':
            account_type = "Receivable Accounts"
        elif lines['result_selection'] == 'supplier':
            account_type = "Payable Accounts"
        elif form['result_selection'] == 'customer_supplier':
            account_type = "Receivable & Payable Accounts"
        target_move = ""
        if form['target_move'] == 'all':
            target_move += "All Entries"
        elif form['result_selection'] == 'posted':
            target_move += "All Posted Entries"
        # sheet.merge_range(row, col, row, col+2, "Partner's :", format2)
        # sheet.merge_range(row, col + 3, row, col + 6, account_type, format2)
        # row += 1
        # sheet.merge_range(row, col, row, col+2, 'Report Type :', format2)
        # sheet.merge_range(row, col+3, row, col+6,
        #                   "Bill-Wise", format2)
        # row += 2

        # constructing the table
        # sheet.merge_range(row, col, row, col+2, "Customer Name", format5)
        # sheet.set_column(col+2, col+9, 10)
        sheet.write(row, col, "Sl No.", format5)
        sheet.write(row, col + 1, "Customer Name", format5)
        sheet.write(row, col + 2, "Invoice Date", format5)
        sheet.write(row, col + 3, "Invoice No.", format5)
        sheet.write(row, col + 4, "Source Document", format5)
        sheet.write(row, col + 5, "Sales Person", format5)
        sheet.write(row, col + 6, "Credit Period (payment terms)", format5)
        sheet.write(row, col + 7, "Payment Due Date", format5)
        sheet.write(row, col + 8, "Invoice Amount", format5)
        sheet.write(row, col + 9, "Amount Paid", format5)
        sheet.write(row, col + 10, "bank collection date", format5)
        sheet.write(row, col + 11, "Write off", format5)
        sheet.write(row, col + 12, "Balance", format5)
        # sheet.write(row, col+13, "Aging", format5)
        sheet.write(row, col + 13, "Not Due", format5)
        sheet.write(row, col + 14, "1-30", format5)
        sheet.write(row, col + 15, "31-60", format5)
        sheet.write(row, col + 16, "61-90", format5)
        sheet.write(row, col + 17, "91-120", format5)
        sheet.write(row, col + 18, "121-150", format5)
        sheet.write(row, col + 19, "151-180", format5)
        sheet.write(row, col + 20, "181-210", format5)
        sheet.write(row, col + 21, "211-240", format5)
        sheet.write(row, col + 22, "241-270", format5)
        sheet.write(row, col + 23, "271-300", format5)
        sheet.write(row, col + 24, "301-330", format5)
        sheet.write(row, col + 25, "331-360", format5)
        sheet.write(row, col + 26, "360 Above", format5)
        sheet.write(row, col + 27, "Total", format5)
        sheet.write(row, col + 28, "Payment Status", format5)
        sheet.write(row, col + 29, "Notes", format5)
        sheet.write(row, col + 30, "Remarks", format5)
        sheet.write(row, col + 31, "Follow up Date", format5)
        sheet.write(row, col + 32, "Month", format5)
        sheet.write(row, col + 33, "Year", format5)

        row += 1
        s=0
        for partner in self.get_sale(data):
            s+=1
            sheet.write(row, col, s, format3)
            sheet.write(row, col + 1, partner['customer_name'], format3)
            sheet.write(row, col + 2, partner['invoice_date'], format3)
            sheet.write(row, col + 3, partner['invoice_no'], format3)
            sheet.write(row, col + 4, partner['source_document'], format3)
            sheet.write(row, col + 5, partner['sales_person'], format3)
            sheet.write(row, col + 6, partner['payment_terms'], format3)
            sheet.write(row, col + 7, partner['payment_due_date'], format3)
            sheet.write(row, col + 8, partner['invoice_amount'], format3)
            sheet.write(row, col + 9, partner['amount_paid'], format3)
            sheet.write(row, col + 10, partner['bank_collection_date'], format3)
            sheet.write(row, col + 11, partner['write_off'], format3)
            sheet.write(row, col + 12, partner['balance'], format3)
            sheet.write(row, col + 13, partner['period0'], format3)
            sheet.write(row, col + 14, partner['period1'], format3)
            sheet.write(row, col + 15, partner['period2'], format3)
            sheet.write(row, col + 16, partner['period3'], format3)
            sheet.write(row, col + 17, partner['period4'], format3)
            sheet.write(row, col + 18, partner['period5'], format3)
            sheet.write(row, col + 19, partner['period6'], format3)
            sheet.write(row, col + 20, partner['period7'], format3)
            sheet.write(row, col + 21, partner['period8'], format3)
            sheet.write(row, col + 22, partner['period9'], format3)
            sheet.write(row, col + 23, partner['period10'], format3)
            sheet.write(row, col + 24, partner['period11'], format3)
            sheet.write(row, col + 25, partner['period12'], format3)
            sheet.write(row, col + 26, partner['period13'], format3)
            sheet.write(row, col + 27, partner['total'], format3)
            sheet.write(row, col + 28, "", format3)
            sheet.write(row, col + 29, "", format3)
            sheet.write(row, col + 30, "", format3)
            sheet.write(row, col + 31, "", format3)
            sheet.write(row, col + 32, "", format3)
            sheet.write(row, col + 33, "", format3)

            row += 1
            # row = row + 1
            line_column = 0

        line_column = 0

        sheet.merge_range(row, 0, row, 6, "TOTAL", font_size_8_left)

        # total_cell_range2 = xl_range(8, 2, row - 1, 2)
        total_cell_range7 = xl_range(4, 7, row - 1, 7)
        total_cell_range8 = xl_range(4, 8, row - 1, 8)
        total_cell_range9 = xl_range(4, 9, row - 1, 9)
        total_cell_range10 = xl_range(4, 10, row - 1, 10)
        total_cell_range11 = xl_range(4, 11, row - 1, 11)
        total_cell_range12 = xl_range(4, 12, row - 1, 12)
        total_cell_range13 = xl_range(4, 13, row - 1, 13)
        total_cell_range14 = xl_range(4, 14, row - 1, 14)
        total_cell_range15 = xl_range(4, 15, row - 1, 15)
        total_cell_range16 = xl_range(4, 16, row - 1, 16)
        total_cell_range17 = xl_range(4, 17, row - 1, 17)
        total_cell_range18 = xl_range(4, 18, row - 1, 18)
        total_cell_range19 = xl_range(4, 19, row - 1, 19)
        total_cell_range20 = xl_range(4, 20, row - 1, 20)
        total_cell_range21 = xl_range(4, 21, row - 1, 21)
        total_cell_range22 = xl_range(4, 22, row - 1, 22)
        total_cell_range23 = xl_range(4, 23, row - 1, 23)
        total_cell_range24 = xl_range(4, 24, row - 1, 24)
        total_cell_range25 = xl_range(4, 25, row - 1, 25)
        total_cell_range26 = xl_range(4, 26, row - 1, 26)
        total_cell_range27 = xl_range(4, 27, row - 1, 27)

        # sheet.write_formula(row, 2, '=SUM(' + total_cell_range2 + ')', font_size_8_center)
        sheet.write_formula(row, 7, '=SUM(' + total_cell_range7 + ')', font_size_8_center)
        sheet.write_formula(row, 8, '=SUM(' + total_cell_range8 + ')', font_size_8_center)
        sheet.write_formula(row, 9, '=SUM(' + total_cell_range9 + ')', font_size_8_center)
        sheet.write_formula(row, 10, '=SUM(' + total_cell_range10 + ')', font_size_8_center)
        sheet.write_formula(row, 11, '=SUM(' + total_cell_range11 + ')', font_size_8_center)
        sheet.write_formula(row, 12, '=SUM(' + total_cell_range12 + ')', font_size_8_center)
        sheet.write_formula(row, 13, '=SUM(' + total_cell_range13 + ')', font_size_8_center)
        sheet.write_formula(row, 14, '=SUM(' + total_cell_range14 + ')', font_size_8_center)
        sheet.write_formula(row, 15, '=SUM(' + total_cell_range15 + ')', font_size_8_center)
        sheet.write_formula(row, 16, '=SUM(' + total_cell_range16 + ')', font_size_8_center)
        sheet.write_formula(row, 17, '=SUM(' + total_cell_range17 + ')', font_size_8_center)
        sheet.write_formula(row, 18, '=SUM(' + total_cell_range18 + ')', font_size_8_center)
        sheet.write_formula(row, 19, '=SUM(' + total_cell_range19 + ')', font_size_8_center)
        sheet.write_formula(row, 20, '=SUM(' + total_cell_range20 + ')', font_size_8_center)
        sheet.write_formula(row, 21, '=SUM(' + total_cell_range21 + ')', font_size_8_center)
        sheet.write_formula(row, 22, '=SUM(' + total_cell_range22 + ')', font_size_8_center)
        sheet.write_formula(row, 23, '=SUM(' + total_cell_range23 + ')', font_size_8_center)
        sheet.write_formula(row, 24, '=SUM(' + total_cell_range24 + ')', font_size_8_center)
        sheet.write_formula(row, 25, '=SUM(' + total_cell_range25 + ')', font_size_8_center)
        sheet.write_formula(row, 26, '=SUM(' + total_cell_range26 + ')', font_size_8_center)
        sheet.write_formula(row, 27, '=SUM(' + total_cell_range27 + ')', font_size_8_center)
