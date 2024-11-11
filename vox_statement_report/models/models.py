# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.misc import formatLang, format_date, get_lang


class Partner(models.Model):
    _inherit = "res.partner"

    # date_start = fields.Date(string="Start Date",default=fields.Date.context_today)
    # date_end = fields.Date(string="End Date",default=fields.Date.context_today)
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")


    def refresh(self):
        for partner in self:
            partner.date_start = False
            partner.date_end = False
            partner._compute_for_followup()
        return

    def res_partner_statement_wizard_button(self):
        action = self.env["ir.actions.actions"]._for_xml_id('vox_statement_report.action_statement_of_account_report')
        return action

    @api.depends('invoice_ids','date_start','date_end')
    @api.onchange('date_start', 'date_end')
    @api.depends_context('company', 'allowed_company_ids')
    def _compute_unreconciled_aml_ids(self):
        values = {
            read['partner_id'][0]: read['line_ids']
            for read in self.env['account.move.line'].read_group(
                domain=self._get_unreconciled_aml_domain(),
                fields=['line_ids:array_agg(id)'],
                groupby=['partner_id']
            )
        }
        for partner in self:
            partner.unreconciled_aml_ids = values.get(partner.id, False)

    # [('move_id.invoice_date', '>=', date_start), ('move_id.invoice_date', '<=', date_end)]
    def _get_unreconciled_aml_domain(self):
        for partner in self:
            if partner.date_start and not partner.date_end:
                return[
                    ('reconciled', '=', False),
                    ('account_id.deprecated', '=', False),
                    ('account_id.internal_type', '=', 'receivable'),
                    ('move_id.state', '=', 'posted'),
                    ('move_id.invoice_date', '>=', partner.date_start),
                    ('partner_id', 'in', self.ids),
                    ('company_id', '=', self.env.company.id),
                ]
            elif partner.date_start and partner.date_end:
                return[
                    ('reconciled', '=', False),
                    ('account_id.deprecated', '=', False),
                    ('account_id.internal_type', '=', 'receivable'),
                    ('move_id.state', '=', 'posted'),
                    ('move_id.invoice_date', '>=', partner.date_start),
                    ('move_id.invoice_date', '<=', partner.date_end),
                    ('partner_id', 'in', self.ids),
                    ('company_id', '=', self.env.company.id),
                ]

            else:
                return [
                    ('reconciled', '=', False),
                    ('account_id.deprecated', '=', False),
                    ('account_id.internal_type', '=', 'receivable'),
                    ('move_id.state', '=', 'posted'),
                    ('partner_id', 'in', self.ids),
                    ('company_id', '=', self.env.company.id),
                ]

    @api.onchange('date_start', 'date_end')
    def statement_print_followups(self):
        self._compute_for_followup()
    #     """
    #     Send a follow-up report by email to customers in self
    #     """
    #     for record in self:
    #         partner = self.env['res.partner'].browse(record.id)
    #         followup_line = partner.followup_level
    #         options = {
    #             'partner_id': record.id,
    #             'followup_level': partner.followup_level
    #         }
    #         self.env['account.followup.report'].get_followup_informations(partner.id, options)
    #         self.env['account.followup.report']._get_lines(options, line_id=None)
    #         self.env['account.followup.report'].print_followups(options)


class AccountFollowupReport(models.AbstractModel):
    _inherit = "account.followup.report"
    _description = "Follow-up Report"

    def _get_columns_name(self, options):
        """
        Override
        Return the name of the columns of the follow-ups report
        """

        headers = [
            {'name': _('Invoice Number'), 'style': 'width: 102px;text-align:center;font-weight: bold;border:1px solid black; background-color:#2E64FE;font-family:Calibri;font-size: 14px;color:white;padding:15px;'},
            {'name': _('Date'), 'class': 'date', 'style': 'width: 100px;text-align:center;font-weight: bold;border:1px solid black; background-color:#2E64FE;font-family:Calibri;font-size: 14px;color:white;padding:5px;'},
            {'name': _('Due Date'), 'class': 'date', 'style': 'width: 100px;text-align:center;font-weight: bold;border:1px solid black; background-color:#2E64FE;font-family:Calibri;font-size: 14px;color:white;padding:5px;'},
            {'name': _('Due Days'), 'class': 'date', 'style': 'width: 100px;text-align:center;font-weight: bold;border:1px solid black; background-color:#2E64FE;font-family:Calibri;font-size: 14px;color:white;padding:5px;'},
            {'name': _('SO Number'), 'style': 'text-align:center;font-weight: bold;border:1px solid black; background-color:#2E64FE;font-family:Calibri;font-size: 14px;color:white;padding:5px;'},
            {'name': _('Project Reference'), 'style': 'text-align:center;font-weight: bold;border:1px solid black; background-color:#2E64FE;font-family:Calibri;font-size: 14px;color:white;padding:5px;'},
            {'name': _('Customer\nLPO Number'), 'style': 'text-align:center;font-weight: bold;border:1px solid black; background-color:#2E64FE;font-family:Calibri;font-size: 14px;color:white;padding:5px;'},
            {'name': _('Communication'), 'style': 'text-align:center;font-weight: bold;border:1px solid black; background-color:#2E64FE;font-family:Calibri;font-size: 14px;color:white;padding:5px;'},
            {'name': _('Expected Date'), 'class': 'date', 'style': 'width: 100px;text-align:center;font-weight: bold;border:1px solid black; background-color:#2E64FE;font-family:Calibri;font-size: 14px;color:white;padding:5px;'},
            {'name': _('Excluded'), 'class': 'date', 'style': 'text-align:center;font-weight: bold;border:1px solid black; background-color:#2E64FE;font-family:Calibri;font-size: 14px;color:white;padding:5px;'},
            {'name': _('Invoice Amount'), 'class': 'date', 'style': 'text-align:center;font-weight: bold;border:1px solid black; background-color:#2E64FE;font-family:Calibri;font-size: 14px;color:white;padding:5px;'},
            {'name': _('Received Amount'), 'class': 'date', 'style': 'text-align:center;font-weight: bold;border:1px solid black; background-color:#2E64FE;font-family:Calibri;font-size: 14px;color:white;padding:5px;'},
            {'name': _('Total Due'), 'class': 'number o_price_total', 'style': 'width: 100px;text-align:center;font-weight: bold;border:1px solid black; background-color:#2E64FE;font-family:Calibri;font-size: 14px;color:white;padding:5px;'},
            {'name': _('Payment Terms'), 'class': 'number o_price_total',
             'style': 'text-align:center;font-weight: bold;border:1px solid black; background-color:#2E64FE;font-family:Calibri;font-size: 14px;color:white;padding:5px;'},
        ]
        if self.env.context.get('print_mode'):
            # headers_style = "border:1px solid black;"
            # for d in headers:
            #
            #     d.update((k, "SO Number") for k, v in d.items() if v == "Source Document")
            #     d.update((k, "text-align:right; white-space:nowrap;border:1px solid black;") for k, v in d.items() if v == "text-align:right; white-space:nowrap;")
            #     d.update((k, "text-align:center; white-space:nowrap;border:1px solid black;") for k, v in d.items() if v == "text-align:center; white-space:nowrap;")
            #     d.update((k, "white-space:nowrap;border:1px solid black;") for k, v in d.items() if v == "white-space:nowrap;")

            headers = headers[:7] + headers[10:]
            headers = [x for x in headers if not ('Project Reference' == x.get('name'))]

            # headers[0]['n'].append('dbms')
            # headers[0]['subjects'].append('dbms')
            # headers = headers.remove(4)# Remove the 'Expected Date' and 'Excluded' columns
        return headers

    def _get_lines(self, options, line_id=None):
        """
        Override
        Compute and return the lines of the columns of the follow-ups report.
        """
        # Get date format for the lang
        partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False
        if not partner:
            return []

        lang_code = partner.lang if self._context.get('print_mode') else self.env.user.lang or get_lang(self.env).code
        lines = []
        res = {}
        today = fields.Date.today()
        line_num = 0
        date_start=''
        date_end =''
        # if partner.date_start and not partner.date_end:
        #     for l in partner.unreconciled_aml_ids.search([('move_id.invoice_date', '>=',partner.date_start)]).sorted().filtered(
        #             lambda aml: not aml.currency_id.is_zero(aml.amount_residual_currency) and
        #             aml.date >= partner.date_start):
        #         date_start = partner.date_start
        #         date_end = partner.date_end
        #
        #         if l.company_id == self.env.company:
        #             if self.env.context.get('print_mode') and l.blocked:
        #                 continue
        #             currency = l.currency_id or l.company_id.currency_id
        #             if currency not in res:
        #                 res[currency] = []
        #             res[currency].append(l)
        #     partner.date_start = False
        #     partner.date_end = False
        # elif partner.date_start and partner.date_end:
        #     for l in partner.unreconciled_aml_ids.search([('move_id.invoice_date', '>=',partner.date_start),('move_id.invoice_date', '<=', partner.date_end)]).sorted().filtered(
        #             lambda aml: not aml.currency_id.is_zero(aml.amount_residual_currency) and
        #             aml.date >= partner.date_start and aml.date >= partner.date_end):
        #         date_start = partner.date_start
        #         date_end = partner.date_end
        #
        #         if l.company_id == self.env.company:
        #             if self.env.context.get('print_mode') and l.blocked:
        #                 continue
        #             currency = l.currency_id or l.company_id.currency_id
        #             if currency not in res:
        #                 res[currency] = []
        #             res[currency].append(l)
        #     partner.date_start = False
        #     partner.date_end = False
        # else:
        for l in partner.unreconciled_aml_ids.sorted().filtered(
                lambda aml: not aml.currency_id.is_zero(aml.amount_residual_currency)):
            date_start = partner.date_start
            date_end = partner.date_end
            # partner.date_start = False
            # partner.date_end = False

            if l.company_id == self.env.company:
                if self.env.context.get('print_mode') and l.blocked:
                    continue
                currency = l.currency_id or l.company_id.currency_id
                if currency not in res:
                    res[currency] = []
                res[currency].append(l)
        for currency, aml_recs in res.items():
            total = 0
            total_issued = 0
            # if date_start and date_end:
            #     # aml_recs = aml_recs.search([('move_id.invoice_date', '>=',date_start),('move_id.invoice_date', '<=', date_end)])
            #     am1 = map(lambda x: x.move_id.invoice_date >= date_start and x.move_id.invoice_date >= date_end,
            #               aml_recs)
            #     am2 = filter(lambda x: x.move_id.invoice_date >= date_start and x.move_id.invoice_date >= date_end,
            #                  aml_recs)
                # aml_recs = aml_recs.filtered(lambda x: x.move_id.invoice_date >= date_start and x.move_id.invoice_date >= date_end)
                # aml_recs = [item for item in aml_recs if item.move_id.invoice_date >= date_start and item.move_id.invoice_date <= date_end]

            #
            # optional = "show"
            # attrs = "{'invisible': [['payment_state', 'in', ('paid', 'in_payment', 'reversed')]]}" / >
            columns =[]
            total_over_due=0.0
            for aml in aml_recs:
                if partner.date_start and partner.date_end:
                    if aml.move_id.invoice_date:
                        if aml.move_id.invoice_date >= partner.date_start and aml.move_id.invoice_date <= partner.date_end:
                            amount = aml.amount_residual_currency if aml.currency_id else aml.amount_residual
                            amount_total = aml.move_id.amount_total
                            amount_paid = aml.move_id.amount_paid
                            invoice_date_due=aml.move_id.invoice_date_due
                            payment_reference = " "
                            if aml.move_id.invoice_payment_term_id:
                                payment_reference = aml.move_id.invoice_payment_term_id.name
                            date_due = format_date(self.env, aml.date_maturity or aml.move_id.invoice_date or aml.date,
                                                   lang_code=lang_code)
                            total += not aml.blocked and amount or 0
                            is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                            is_payment = aml.payment_id
                            if is_overdue or is_payment:
                                total_issued += not aml.blocked and amount or 0.00
                            if is_overdue:
                                date_due = {'name': date_due, 'class': 'color-red date',
                                            'style': 'text-align:center;color: red;font-family:Calibri;'}
                                total_over_due+=amount
                            else:
                                date_due = {'name': date_due,
                                            'style': 'text-align:center;font-family:Calibri;'}
                            if is_payment:
                                date_due = ''
                            move_line_name = self._format_aml_name(aml.name, aml.move_id.ref)
                            if self.env.context.get('print_mode'):
                                move_line_name = {'name': move_line_name, 'style': 'text-align:center; font-family:Calibri;'}
                            # amount = round(amount,2)#formatLang(self.env, amount, currency_obj=currency)
                            line_num += 1
                            expected_pay_date = format_date(self.env, aml.expected_pay_date,
                                                            lang_code=lang_code) if aml.expected_pay_date else ''
                            invoice_origin = aml.move_id.invoice_origin or ''
                            project_reference = aml.move_id.project_id.sudo().sale_id.sudo().client_order_ref or ''
                            lpo_number = aml.move_id.project_id.sudo().sale_id.sudo().lpo_number or ''
                            if len(invoice_origin) > 43:
                                invoice_origin = invoice_origin[:40] + '...'

                            invoice_origin={'name': invoice_origin,
                                                 'style': 'text-align:left;border:1px solid black;padding:5px;font-family:Calibri;'}
                            amount_total = {'name': '{:0.2f}'.format(amount_total if amount_total else 0.00), 'style': 'text-align:right;border:1px solid black;padding:5px;font-family:Calibri;'}
                            amount_paid = {'name': '{:0.2f}'.format(amount_paid if amount_paid else 0.00), 'style': 'text-align:right;border:1px solid black;padding:5px;font-family:Calibri;'}
                            amount = {'name': '{:0.2f}'.format(amount if amount else 0.00),
                                           'style': 'text-align:right;white-space:nowrap;border:1px solid black;padding:5px;font-family:Calibri;'}
                            lpo_number = {'name': lpo_number,
                                          'style': 'text-align:left;white-space:nowrap;border:1px solid black;padding:5px;font-family:Calibri;'}
                            # move_line_name = {'name': move_line_name,
                            #                   'style': 'text-align:center;border:1px solid black;padding:5px;width:150px;'}
                            payment_reference = {'name': payment_reference,
                                                 'style': 'text-align:left;border:1px solid black;padding:5px;font-family:Calibri;'}
                            Date = format_date(self.env, aml.move_id.invoice_date or aml.date, lang_code=lang_code)


                            Date = {'name': Date,
                                    'style': 'text-align:center;border:1px solid black;padding:5px;font-family:Calibri;'}

                            invoice_days_due = {'name': str((today-invoice_date_due).days) + ' Days',
                                                'style': 'text-align:center;border:1px solid black;padding:5px;font-family:Calibri;'}
                            columns = [
                                Date,#format_date(self.env, aml.move_id.invoice_date or aml.date, lang_code=lang_code),
                                date_due,
                                invoice_days_due,
                                # date_due,
                                invoice_origin,
                                project_reference,
                                lpo_number,
                                move_line_name,
                                (expected_pay_date and expected_pay_date + ' ') + (aml.internal_note or ''),
                                {'name': '', 'blocked': aml.blocked},
                                amount_total,
                                amount_paid,
                                amount,
                                payment_reference

                            ]

                            if self.env.context.get('print_mode'):
                                columns = columns[:6] + columns[9:]
                                a = columns.pop(4)
                                columns = columns


                            lines.append({
                                'id': aml.id,
                                'account_move': aml.move_id,
                                'name': aml.move_id.name,
                                'caret_options': 'followup',
                                'move_id': aml.move_id.id,
                                'type': is_payment and 'payment' or 'unreconciled_aml',
                                'unfoldable': False,
                                'style': 'border: 1px solid black' if self.env.context.get(
                                    'print_mode') else '',
                                'columns': [type(v) == dict and v or {'name': v} for v in columns],
                            })
                else:
                    amount = aml.amount_residual_currency if aml.currency_id else aml.amount_residual
                    amount_total = aml.move_id.amount_total
                    amount_total = amount_total if amount_total else 0.00
                    amount_paid = aml.move_id.amount_paid
                    amount_paid=amount_paid if amount_paid else 0.00
                    payment_reference = " "
                    invoice_date_due = aml.move_id.invoice_date_due
                    if aml.move_id.invoice_payment_term_id:
                        payment_reference = aml.move_id.invoice_payment_term_id.name
                    date_due = format_date(self.env, aml.date_maturity or aml.move_id.invoice_date or aml.date,
                                           lang_code=lang_code)
                    total += not aml.blocked and amount or 0
                    is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                    is_payment = aml.payment_id
                    if is_overdue or is_payment:
                        total_issued += not aml.blocked and amount or 0
                    if is_overdue:
                        date_due = {'name': date_due, 'class': 'color-red date',
                                    'style': 'white-space:nowrap;text-align:center;color: red;'}
                    if is_payment:
                        date_due = ''
                    move_line_name = self._format_aml_name(aml.name, aml.move_id.ref)
                    if self.env.context.get('print_mode'):
                        move_line_name = {'name': move_line_name, 'style': 'text-align:center; font-family:Calibri;'}
                    amount = amount#formatLang(self.env, amount, currency_obj=currency)
                    amount=amount if amount else 0.00


                    line_num += 1
                    expected_pay_date = format_date(self.env, aml.expected_pay_date,
                                                    lang_code=lang_code) if aml.expected_pay_date else ''
                    invoice_origin = aml.move_id.invoice_origin or ''
                    project_reference = aml.move_id.project_id.sudo().sale_id.sudo().client_order_ref or ''
                    lpo_number = aml.move_id.project_id.sudo().sale_id.sudo().lpo_number or ''
                    if len(invoice_origin) > 43:
                        invoice_origin = invoice_origin[:40] + '...'

                    invoice_origin = {'name': invoice_origin,
                                      'style': 'text-align:left;border:1px solid black;padding:5px;font-family:Calibri;'}
                    amount_total = {'name': '{:0.2f}'.format(amount_total),
                                    'style': 'text-align:right;border:1px solid black;padding:5px;font-family:Calibri;'}
                    amount_paid = {'name': '{:0.2f}'.format(amount_paid),
                                   'style': 'text-align:right;border:1px solid black;padding:5px;font-family:Calibri;'}
                    amount = {'name': '{:0.2f}'.format(amount),
                              'style': 'text-align:center;border:1px solid black;padding:5px;font-family:Calibri;'}

                    lpo_number = {'name': lpo_number,
                              'style': 'text-align:left;border:1px solid black;padding:5px;font-family:Calibri;'}
                    # move_line_name = {'name': move_line_name,
                    #               'style': 'text-align:center;border:1px solid black;padding:5px;'}

                    payment_reference = {'name': payment_reference,
                                  'style': 'text-align:left;border:1px solid black;padding:5px;font-family:Calibri;'}
                    Date=format_date(self.env, aml.move_id.invoice_date or aml.date, lang_code=lang_code)
                    Date = {'name': Date,
                                         'style': 'text-align:center;border:1px solid black;padding:5px;font-family:Calibri;'}

                    invoice_days_due = {'name': str((today-invoice_date_due).days) + ' Days',
                                        'style': 'text-align:center;border:1px solid black;padding:5px;font-family:Calibri;'}
                    columns = [
                        Date,#format_date(self.env, aml.move_id.invoice_date or aml.date, lang_code=lang_code),
                        date_due,
                        invoice_days_due,
                        invoice_origin,
                        project_reference,
                        lpo_number,
                        move_line_name,
                        (expected_pay_date and expected_pay_date + ' ') + (aml.internal_note or ''),
                        {'name': '', 'blocked': aml.blocked},
                        amount_total,
                        amount_paid,
                        amount,
                        payment_reference

                    ]
                    if self.env.context.get('print_mode'):
                        columns = columns[:6] + columns[9:]
                        a = columns.pop(4)
                        columns = columns
                    invoice_number = {'name': aml.move_id.name,  'style': 'text-align:center;border:1px solid black;padding:5px;font-family:Calibri;'}
                    lines.append({
                        'id': aml.id,
                        'account_move': aml.move_id,
                        'name': aml.move_id.name,
                        'caret_options': 'followup',
                        'move_id': aml.move_id.id,
                        'type': is_payment and 'payment' or 'unreconciled_aml',
                        'style': 'border: 1px solid black' if self.env.context.get(
                            'print_mode') else '',
                        'unfoldable': False,
                        'columns': [type(v) == dict and v or {'name': v} for v in columns],
                    })
            total_due = '{:0.2f}'.format(total)

            # total_due = formatLang(self.env, total, currency_obj=currency)



            line_num += 1
            # columns = [
            #     Date,  # format_date(self.env, aml.move_id.invoice_date or aml.date, lang_code=lang_code),
            #     date_due,
            #     invoice_days_due,
            #     invoice_origin,
            #     project_reference,
            #     lpo_number,
            #     move_line_name,
            #     (expected_pay_date and expected_pay_date + ' ') + (aml.internal_note or ''),
            #     {'name': '', 'blocked': aml.blocked},
            #     amount_total,
            #     amount_paid,
            #     amount,
            #     payment_reference
            #
            # ]

            lines.append({
                'id': line_num,
                'account_move':'',
                'name': '  ',
                'class': 'total',
                'style': 'text-align:right;padding:6px;font-weight: bold;font-size:18px;background-color:#2E64FE;border:1px solid black;padding:5px;font-family:Calibri;',
                # 'style': 'border: 1px solid black' if self.env.context.get(
                #     'print_mode') else 'border-top-style: double',
                # 'style': 'border-top-style: double',
                'unfoldable': False,
                'level': 3,
                'columns': [{'name': v} for v in [''] * (6 if self.env.context.get('print_mode') else 9) + [
                    total >= 0 and _('Total Due') or '', total_due,'']],
            })

            lines.append({
                'id': line_num,
                'account_move': '',
                'name': '  ',
                'class': 'total',
                'style': 'text-align:right;padding:6px;font-weight: bold;font-size:18px;background-color:#2E64FE;border:1px solid black;padding:5px;font-family:Calibri;',
                # 'style': 'border: 1px solid black' if self.env.context.get(
                #     'print_mode') else 'border-top-style: double',
                # 'style': 'border-top-style: double',
                'unfoldable': False,
                'level': 3,
                'columns': [{'name': v} for v in [''] * (6 if self.env.context.get('print_mode') else 9) + [
                    total >= 0 and _('Total Over Due') or '', total_over_due, '']],
            })

            # if total_issued > 0:
            #     total_issued = formatLang(self.env, total_issued, currency_obj=currency)
            #     line_num += 1
            #     lines.append({
            #         'id': line_num,
            #         'name': '',
            #         'class': 'total',
            #         'style': 'text-align:left;padding:6px;font-weight: bold;font-size:18px;border:1px',
            #         # 'style': 'border: 1px solid black' if self.env.context.get(
            #         #     'print_mode') else " ",
            #         'unfoldable': False,
            #         'level': 3,
            #         'columns': [{'name': v} for v in
            #                     [''] * (5 if self.env.context.get('print_mode') else 9) + [_('Total Overdue'),
            #                                                                                total_issued]],
            #     })

            # if self.env.context.get('print_mode'):
            #     line_num += 1
            #     lines.append({
            #         'id': line_num,
            #         'name': '',
            #         'style': 'text-align:left;padding:6px;font-weight: bold;font-size:18px;border:1px',
            #         'class': '',
            #         'unfoldable': False,
            #         'level': 3,
            #         'columns': [],
            #     })
            #     line_num += 1
            #     lines.append({
            #         'id': line_num,
            #         'name': '',
            #         'style': 'text-align:left;padding:6px;font-weight: bold;font-size:18px;border:1px;',
            #         'class': '',
            #         'unfoldable': False,
            #         'level': 3,
            #         'columns': [],
            #     })
            #     line_num += 1
            #     lines.append({
            #             'id': line_num,
            #             'name': '',
            #             'style': 'text-align:left;padding:6px;font-weight: bold;font-size:18px;border:1px;',
            #             'class': 'text-left',
            #             # 'unfoldable': False,
            #             # 'level': 6,
            #             'columns': [{'name': v} for v in [''] * (7 if self.env.context.get('print_mode') else 9) + [
            #         ('Signature') or '']],
            #         })
            # line_num += 1
            # if columns:
            #     lines.append({
            #         'id': line_num,
            #         'name': '',
            #         'class': '',
            #         'style': 'border-bottom-style: none',
            #         'unfoldable': False,
            #         'level': 0,
            #         'columns': [{} for col in columns],
            #     })
            #
            # line_num += 1
            # lines.append({
            #     'id': line_num,
            #     'name': '',
            #     'style': 'text-align:left;padding:6px;font-size:13px;background-color:#ffffff;border-bottom:0px;border-top:0px;border-left:0px;border-right:0px;',
            #     # 'class': 'total',
            #     # 'unfoldable': False,
            #     # 'level': 3,
            #     'columns': [{'name': 'For Cubit Technologies LLC' } + v for v in [''] * (5 if self.env.context.get('print_mode') else 9) ],
            # })

            # Add an empty line after the total to make a space between two currencies
            line_num += 1
            if columns:
                lines.append({
                    'id': line_num,
                    'name': '',
                    # 'class': '',
                    #'style': 'border-bottom-style: none',
                    'style': 'text-align:left;padding:6px;font-weight: bold;font-size:18px;border-style: none;',
                    'unfoldable': False,
                    'level': 3,
                    'columns': [{} for col in columns],
                })


        # Remove the last empty line
        if lines:
            lines.pop()
        return lines

    def _get_report_name(self):
        """
        Override
        Return the name of the report
        """
        return _('')
    # @api.model
    # def statement_report(self, options):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'name': _("Statement Report"),
    #         'res_model': 'statement.account.report.wizard',
    #         'target': 'new',
    #         'views': [(False, "form")],
    #         'context': {
    #             'default_body': self._get_sms_summary(options),
    #             'default_res_model': 'res.partner',
    #             'default_res_id': options.get('partner_id'),
    #             'default_composition_mode': 'comment',
    #         },
    #     }


    # @api.model
    # def print_followups(self, records):
    #     """
    #     Print one or more followups in one PDF
    #     records contains either a list of records (come from an server.action) or a field 'ids' which contains a list of one id (come from JS)
    #     """
    #     res_ids = records['ids'] if 'ids' in records else records.ids
    #     action = self.env["ir.actions.actions"]._for_xml_id('vox_statement_report.action_for_print_account_report')
    #     # action['context'] = {'default_res_ids': res_ids}
    #     return action
        # records come from either JS or server.action
        # action = self.env.ref('account_followup.action_report_followup').report_action(res_ids)
        # if action.get('type') == 'ir.actions.report':
        #     for partner in self.env['res.partner'].browse(res_ids):
        #         partner.message_post(body=_('Follow-up letter printed'))
        # return action
