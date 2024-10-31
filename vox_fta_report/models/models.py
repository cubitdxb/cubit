# -*- coding: utf-8 -*-

from odoo import models
import datetime
from datetime import datetime
from xlsxwriter.utility import xl_range



class SalesXlsx(models.AbstractModel):
    _name = 'report.vox_fta_report.vox_fta_report_xls.xslx'
    _inherit = 'report.report_xlsx.abstract'

    def get_lines(self, data):

        lines = []

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        company_id = data['form']['company_id']
        report_id = data['form']['report_id']
        tax_ids = data['form']['tax_ids']
        # date_start = data.date_start
        # date_end = data.date_end
        # company_id = data.company_id
        # report_id = data.report_id
        # tax_ids = data.tax_ids
        if date_start:
            date_object_date_start = datetime.strptime(str(date_start), '%Y-%m-%d').date()
        if date_end:
            date_object_date_end = datetime.strptime(str(date_end), '%Y-%m-%d').date()

        sl = 0

        if report_id == 'std_rated_sales':

            query = """
            
              select 
				
				max(company.name) as company_name,
				account_move_line__move_id.company_id as company_id,
				account_move_line__move_id.name as invoice_number,
				account_move_line__move_id.invoice_date as invoice_date,
				SUM(account_move_line.price_subtotal * (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_amount,
				SUM((account_move_line.price_total-account_move_line.price_subtotal) * (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_tax,
				max(rs.name) as partner_name,
				max(rs.vat) as customer_vat,
				max(tax.name) as vat_description
				
			FROM account_move_line_account_tax_rel tax_rel
                JOIN account_tax tax ON tax.id = tax_rel.account_tax_id
                JOIN account_move_line ON account_move_line.id = tax_rel.account_move_line_id 
                LEFT JOIN account_tax src_tax ON src_tax.id = account_move_line.tax_line_id
                LEFT JOIN account_tax src_group_tax ON src_group_tax.id = account_move_line.group_tax_id
                JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
				left join res_partner as rs on rs.id=account_move_line__move_id.partner_id
				JOIN res_company company ON account_move_line.company_id = company.id
                WHERE 
				account_move_line__move_id.move_type IN ('out_invoice', 'out_refund')
				and account_move_line__move_id.state = 'posted'
				and tax.type_tax_use IN ('sale')
				and  to_char(date_trunc('day',account_move_line__move_id.invoice_date),'YYYY-MM-DD')::date between %s and %s
				and tax_rel.account_tax_id in %s
				group by account_move_line__move_id.id
            
            """
            # self.env.cr.execute(query, (
            #     date_object_date_start.strftime('%Y-%m-%d'), date_object_date_end.strftime('%Y-%m-%d'),tuple(tax_ids.ids),
            # ))
            self.env.cr.execute(query, (
                date_start, date_end,tuple(tax_ids),
            ))
            for row in self.env.cr.dictfetchall():
                sl += 1
                company_name = row['company_name'] if row['company_name'] else " "
                invoice_number = row['invoice_number'] if row['invoice_number'] else " "
                invoice_date = row['invoice_date'] if row['invoice_date'] else ""
                invoice_amount = row['invoice_amount'] if row['invoice_amount'] else 0.0
                invoice_tax = row['invoice_tax'] if row['invoice_tax'] else 0.0
                partner_name = row['partner_name'] if row['partner_name'] else " "
                customer_vat = row['customer_vat'] if row['customer_vat'] else 0
                vat_description = row['vat_description'] if row['vat_description'] else " "
                company_value_id = row['company_id'] if row['company_id'] else " "
                if company_value_id:
                    vat = self.env['res.company'].browse(company_value_id).vat
                else:
                    vat = ""

                # date_start = data.date_start
                # date_end = data.date_end


                date_start = data['form']['date_start']
                date_end = data['form']['date_end']
                if date_start:
                    date_object_date_start = datetime.strptime(str(date_start), '%Y-%m-%d').date()
                if date_end:
                    date_object_date_end = datetime.strptime(str(date_end), '%Y-%m-%d').date()

                if invoice_date:
                    date_value = datetime.strptime(str(invoice_date), '%Y-%m-%d').date()
                    invoice_date = date_value.strftime('%d/%m/%Y')
                else:
                    invoice_date =" "

                res = {
                    'sl_no': sl,
                    'company_name': company_name,
                    'company_vat': vat,
                    'invoice_number': invoice_number if invoice_number else " ",
                    'invoice_date': invoice_date if invoice_date else 0.0,
                    'reporting_period': date_object_date_start.strftime(
                        '%d/%m/%Y') + " to " + date_object_date_end.strftime(
                        '%d/%m/%Y'),
                    'invoice_amount': invoice_amount if invoice_amount else 0.0,
                    'invoice_tax': invoice_tax if invoice_tax else 0.0,
                    'partner_name': partner_name if partner_name else " ",
                    'customer_vat': customer_vat if customer_vat else 0.0,
                    'vat_description': vat_description if vat_description else " ",

                }

                lines.append(res)
            if lines:
                return lines
            else:
                return []


        elif report_id == 'out_of_scope_sales':

            query = """

                          select 

            				max(company.name) as company_name,
            				account_move_line__move_id.company_id as company_id,
            				account_move_line__move_id.name as invoice_number,
            				account_move_line__move_id.invoice_date as invoice_date,
            				SUM(account_move_line.price_subtotal* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_amount,
            				SUM((account_move_line.price_total-account_move_line.price_subtotal)* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_tax,
            				max(rs.name) as partner_name,
            				max(rs.vat) as customer_vat,
            				max(tax.name) as vat_description

            			FROM account_move_line_account_tax_rel tax_rel
                            JOIN account_tax tax ON tax.id = tax_rel.account_tax_id
                            JOIN account_move_line ON account_move_line.id = tax_rel.account_move_line_id 
                            LEFT JOIN account_tax src_tax ON src_tax.id = account_move_line.tax_line_id
                            LEFT JOIN account_tax src_group_tax ON src_group_tax.id = account_move_line.group_tax_id
                            JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
            				left join res_partner as rs on rs.id=account_move_line__move_id.partner_id
            				JOIN res_company company ON account_move_line.company_id = company.id
                            WHERE 
            				account_move_line__move_id.move_type IN ('out_invoice', 'out_refund')
            				and account_move_line__move_id.state = 'posted'
            				and tax.type_tax_use IN ('sale')
            				and  to_char(date_trunc('day',account_move_line__move_id.invoice_date),'YYYY-MM-DD')::date between %s and %s
            				and tax_rel.account_tax_id in %s
            				group by account_move_line__move_id.id

                        """
            # self.env.cr.execute(query, (
            #     date_object_date_start.strftime('%Y-%m-%d'), date_object_date_end.strftime('%Y-%m-%d'),tuple(tax_ids.ids),
            # ))
            self.env.cr.execute(query, (
                date_start, date_end, tuple(tax_ids),
            ))
            for row in self.env.cr.dictfetchall():
                sl += 1
                company_name = row['company_name'] if row['company_name'] else " "
                invoice_number = row['invoice_number'] if row['invoice_number'] else " "
                invoice_date = row['invoice_date'] if row['invoice_date'] else ""
                invoice_amount = row['invoice_amount'] if row['invoice_amount'] else 0.0
                invoice_tax = row['invoice_tax'] if row['invoice_tax'] else 0.0
                partner_name = row['partner_name'] if row['partner_name'] else " "
                customer_vat = row['customer_vat'] if row['customer_vat'] else 0
                vat_description = row['vat_description'] if row['vat_description'] else " "
                company_value_id = row['company_id'] if row['company_id'] else " "
                if company_value_id:
                    vat = self.env['res.company'].browse(company_value_id).vat
                else:
                    vat = ""

                # date_start = data.date_start
                # date_end = data.date_end

                date_start = data['form']['date_start']
                date_end = data['form']['date_end']
                if date_start:
                    date_object_date_start = datetime.strptime(str(date_start), '%Y-%m-%d').date()
                if date_end:
                    date_object_date_end = datetime.strptime(str(date_end), '%Y-%m-%d').date()

                if invoice_date:
                    date_value = datetime.strptime(str(invoice_date), '%Y-%m-%d').date()
                    invoice_date = date_value.strftime('%d/%m/%Y')
                else:
                    invoice_date =" "

                res = {
                    'sl_no': sl,
                    'company_name': company_name,
                    'company_vat': vat,
                    'invoice_number': invoice_number if invoice_number else " ",
                    'invoice_date': invoice_date if invoice_date else 0.0,
                    'reporting_period': date_object_date_start.strftime(
                        '%d/%m/%Y') + " to " + date_object_date_end.strftime(
                        '%d/%m/%Y'),
                    'invoice_amount': invoice_amount if invoice_amount else 0.0,
                    'invoice_tax': invoice_tax if invoice_tax else 0.0,
                    'partner_name': partner_name if partner_name else " ",
                    'customer_vat': customer_vat if customer_vat else 0.0,
                    'vat_description': vat_description if vat_description else " ",

                }

                lines.append(res)
            if lines:
                return lines
            else:
                return []

        elif report_id == 'tourist_refund_adj':

            query = """

                          select 

            				max(company.name) as company_name,
            				account_move_line__move_id.company_id as company_id,
            				account_move_line__move_id.name as invoice_number,
            				account_move_line__move_id.invoice_date as invoice_date,
            				SUM(account_move_line.price_subtotal* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_amount,
            				SUM((account_move_line.price_total-account_move_line.price_subtotal)* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_tax,
            				SUM(account_move_line.price_total * (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS total_invoice_amount,
            				max(rs.name) as partner_name,
            				max(rs.vat) as customer_vat,
            				max(tax.name) as vat_description

            			FROM account_move_line_account_tax_rel tax_rel
                            JOIN account_tax tax ON tax.id = tax_rel.account_tax_id
                            JOIN account_move_line ON account_move_line.id = tax_rel.account_move_line_id 
                            LEFT JOIN account_tax src_tax ON src_tax.id = account_move_line.tax_line_id
                            LEFT JOIN account_tax src_group_tax ON src_group_tax.id = account_move_line.group_tax_id
                            JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
            				left join res_partner as rs on rs.id=account_move_line__move_id.partner_id
            				JOIN res_company company ON account_move_line.company_id = company.id
                            WHERE 
            				account_move_line__move_id.move_type IN ('out_invoice', 'out_refund')
            				and account_move_line__move_id.state = 'posted'
            				and tax.type_tax_use IN ('sale')
            				and  to_char(date_trunc('day',account_move_line__move_id.invoice_date),'YYYY-MM-DD')::date between %s and %s
            				and tax_rel.account_tax_id in %s
            				group by account_move_line__move_id.id

                        """
            # self.env.cr.execute(query, (
            #     date_object_date_start.strftime('%Y-%m-%d'), date_object_date_end.strftime('%Y-%m-%d'),tuple(tax_ids.ids),
            # ))
            self.env.cr.execute(query, (
                date_start, date_end, tuple(tax_ids),
            ))
            for row in self.env.cr.dictfetchall():
                sl += 1
                company_name = row['company_name'] if row['company_name'] else " "
                invoice_number = row['invoice_number'] if row['invoice_number'] else " "
                invoice_date = row['invoice_date'] if row['invoice_date'] else ""
                invoice_amount = row['invoice_amount'] if row['invoice_amount'] else 0.0
                invoice_tax = row['invoice_tax'] if row['invoice_tax'] else 0.0
                total_invoice_amount = row['total_invoice_amount'] if row['total_invoice_amount'] else 0.0
                partner_name = row['partner_name'] if row['partner_name'] else " "
                customer_vat = row['customer_vat'] if row['customer_vat'] else 0
                vat_description = row['vat_description'] if row['vat_description'] else " "
                company_value_id = row['company_id'] if row['company_id'] else " "
                if company_value_id:
                    vat = self.env['res.company'].browse(company_value_id).vat
                else:
                    vat = ""

                # date_start = data.date_start
                # date_end = data.date_end

                date_start = data['form']['date_start']
                date_end = data['form']['date_end']
                if date_start:
                    date_object_date_start = datetime.strptime(str(date_start), '%Y-%m-%d').date()
                if date_end:
                    date_object_date_end = datetime.strptime(str(date_end), '%Y-%m-%d').date()

                if invoice_date:
                    date_value = datetime.strptime(str(invoice_date), '%Y-%m-%d').date()
                    invoice_date = date_value.strftime('%d/%m/%Y')
                else:
                    invoice_date =" "

                res = {
                    'sl_no': sl,
                    'company_name': company_name,
                    'company_vat': vat,
                    'invoice_number': invoice_number if invoice_number else " ",
                    'invoice_date': invoice_date if invoice_date else 0.0,
                    'reporting_period': date_object_date_start.strftime(
                        '%d/%m/%Y') + " to " + date_object_date_end.strftime(
                        '%d/%m/%Y'),
                    'invoice_amount': invoice_amount if invoice_amount else 0.0,
                    'invoice_tax': invoice_tax if invoice_tax else 0.0,
                    'total_invoice_amount': total_invoice_amount if total_invoice_amount else 0.0,
                    'partner_name': partner_name if partner_name else " ",
                    'customer_vat': customer_vat if customer_vat else 0.0,
                    'vat_description': vat_description if vat_description else " ",

                }

                lines.append(res)
            if lines:
                return lines
            else:
                return []

        elif report_id == 'import_of_services':

            query = """

                          select 

            				max(company.name) as company_name,
            				account_move_line__move_id.company_id as company_id,
            				account_move_line__move_id.name as invoice_number,
            				account_move_line__move_id.invoice_date as invoice_date,
            				SUM(account_move_line.price_subtotal* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_amount,
            				SUM((account_move_line.price_total-account_move_line.price_subtotal)* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_tax,
            				SUM(account_move_line.price_total* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS total_invoice_amount,
            				max(rs.name) as partner_name,
            				max(rc.name) as location,
            				max(rs.vat) as customer_vat,
            				max(tax.name) as vat_description

            			FROM account_move_line_account_tax_rel tax_rel
                            JOIN account_tax tax ON tax.id = tax_rel.account_tax_id
                            JOIN account_move_line ON account_move_line.id = tax_rel.account_move_line_id 
                            LEFT JOIN account_tax src_tax ON src_tax.id = account_move_line.tax_line_id
                            LEFT JOIN account_tax src_group_tax ON src_group_tax.id = account_move_line.group_tax_id
                            JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
            				left join res_partner as rs on rs.id=account_move_line__move_id.partner_id
            				left join res_country as rc on rs.country_id=rc.id
            				JOIN res_company company ON account_move_line.company_id = company.id
                            WHERE 
            				account_move_line__move_id.move_type IN ('in_invoice', 'in_refund')
            				and account_move_line__move_id.state = 'posted'
            				and tax.type_tax_use IN ('purchase')
            				and  to_char(date_trunc('day',account_move_line__move_id.invoice_date),'YYYY-MM-DD')::date between %s and %s
            				and tax_rel.account_tax_id in %s
            				group by account_move_line__move_id.id

                        """
            # self.env.cr.execute(query, (
            #     date_object_date_start.strftime('%Y-%m-%d'), date_object_date_end.strftime('%Y-%m-%d'),tuple(tax_ids.ids),
            # ))
            self.env.cr.execute(query, (
                date_start, date_end, tuple(tax_ids),
            ))
            for row in self.env.cr.dictfetchall():
                sl += 1
                company_name = row['company_name'] if row['company_name'] else " "
                invoice_number = row['invoice_number'] if row['invoice_number'] else " "
                invoice_date = row['invoice_date'] if row['invoice_date'] else ""
                invoice_amount = row['invoice_amount'] if row['invoice_amount'] else 0.0
                invoice_tax = row['invoice_tax'] if row['invoice_tax'] else 0.0
                total_invoice_amount = row['total_invoice_amount'] if row['total_invoice_amount'] else 0.0
                partner_name = row['partner_name'] if row['partner_name'] else " "
                location = row['location'] if row['location'] else " "
                customer_vat = row['customer_vat'] if row['customer_vat'] else 0
                vat_description = row['vat_description'] if row['vat_description'] else " "
                company_value_id = row['company_id'] if row['company_id'] else " "
                if company_value_id:
                    vat = self.env['res.company'].browse(company_value_id).vat
                else:
                    vat = ""

                # date_start = data.date_start
                # date_end = data.date_end

                date_start = data['form']['date_start']
                date_end = data['form']['date_end']
                if date_start:
                    date_object_date_start = datetime.strptime(str(date_start), '%Y-%m-%d').date()
                if date_end:
                    date_object_date_end = datetime.strptime(str(date_end), '%Y-%m-%d').date()

                if invoice_date:
                    date_value = datetime.strptime(str(invoice_date), '%Y-%m-%d').date()
                    invoice_date = date_value.strftime('%d/%m/%Y')
                else:
                    invoice_date =" "

                res = {
                    'sl_no': sl,
                    'company_name': company_name,
                    'company_vat': vat,
                    'invoice_number': invoice_number if invoice_number else " ",
                    'invoice_date': invoice_date if invoice_date else 0.0,
                    'reporting_period': date_object_date_start.strftime(
                        '%d/%m/%Y') + " to " + date_object_date_end.strftime(
                        '%d/%m/%Y'),
                    'invoice_amount': invoice_amount if invoice_amount else 0.0,
                    'invoice_tax': invoice_tax if invoice_tax else 0.0,
                    'total_invoice_amount': total_invoice_amount if total_invoice_amount else 0.0,
                    'partner_name': partner_name if partner_name else " ",
                    'location': location if location else " ",
                    'customer_vat': customer_vat if customer_vat else 0.0,
                    'vat_description': vat_description if vat_description else " ",

                }

                lines.append(res)
            if lines:
                return lines
            else:
                return []


        elif report_id == 'zero_rated_sales':

            query = """

                          select 

            				max(company.name) as company_name,
            				account_move_line__move_id.company_id as company_id,
            				account_move_line__move_id.name as invoice_number,
            				account_move_line__move_id.invoice_date as invoice_date,
            				SUM(account_move_line.price_subtotal* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_amount,
            				SUM((account_move_line.price_total-account_move_line.price_subtotal)* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_tax,
            				SUM(account_move_line.price_total* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS total_invoice_amount,
            				max(rs.name) as partner_name,
            				max(rc.name) as location,
            				max(rs.vat) as customer_vat,
            				max(tax.name) as vat_description

            			FROM account_move_line_account_tax_rel tax_rel
                            JOIN account_tax tax ON tax.id = tax_rel.account_tax_id
                            JOIN account_move_line ON account_move_line.id = tax_rel.account_move_line_id 
                            LEFT JOIN account_tax src_tax ON src_tax.id = account_move_line.tax_line_id
                            LEFT JOIN account_tax src_group_tax ON src_group_tax.id = account_move_line.group_tax_id
                            JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
            				left join res_partner as rs on rs.id=account_move_line__move_id.partner_id
            				left join res_country as rc on rs.country_id=rc.id
            				JOIN res_company company ON account_move_line.company_id = company.id
                            WHERE 
            				account_move_line__move_id.move_type IN ('out_invoice', 'out_refund')
            				and account_move_line__move_id.state = 'posted'
            				and tax.type_tax_use IN ('sale')
            				and  to_char(date_trunc('day',account_move_line__move_id.invoice_date),'YYYY-MM-DD')::date between %s and %s
            				and tax_rel.account_tax_id in %s
            				group by account_move_line__move_id.id

                        """
            # self.env.cr.execute(query, (
            #     date_object_date_start.strftime('%Y-%m-%d'), date_object_date_end.strftime('%Y-%m-%d'),tuple(tax_ids.ids),
            # ))
            self.env.cr.execute(query, (
                date_start, date_end, tuple(tax_ids),
            ))
            for row in self.env.cr.dictfetchall():
                sl += 1
                company_name = row['company_name'] if row['company_name'] else " "
                invoice_number = row['invoice_number'] if row['invoice_number'] else " "
                invoice_date = row['invoice_date'] if row['invoice_date'] else ""
                invoice_amount = row['invoice_amount'] if row['invoice_amount'] else 0.0
                invoice_tax = row['invoice_tax'] if row['invoice_tax'] else 0.0
                total_invoice_amount = row['total_invoice_amount'] if row['total_invoice_amount'] else 0.0
                partner_name = row['partner_name'] if row['partner_name'] else " "
                location = row['location'] if row['location'] else " "
                customer_vat = row['customer_vat'] if row['customer_vat'] else 0
                vat_description = row['vat_description'] if row['vat_description'] else " "
                company_value_id = row['company_id'] if row['company_id'] else " "
                if company_value_id:
                    vat = self.env['res.company'].browse(company_value_id).vat
                else:
                    vat = ""

                # date_start = data.date_start
                # date_end = data.date_end

                date_start = data['form']['date_start']
                date_end = data['form']['date_end']
                if date_start:
                    date_object_date_start = datetime.strptime(str(date_start), '%Y-%m-%d').date()
                if date_end:
                    date_object_date_end = datetime.strptime(str(date_end), '%Y-%m-%d').date()

                if invoice_date:
                    date_value = datetime.strptime(str(invoice_date), '%Y-%m-%d').date()
                    invoice_date = date_value.strftime('%d/%m/%Y')
                else:
                    invoice_date =" "

                res = {
                    'sl_no': sl,
                    'company_name': company_name,
                    'company_vat': vat,
                    'invoice_number': invoice_number if invoice_number else " ",
                    'invoice_date': invoice_date if invoice_date else 0.0,
                    'reporting_period': date_object_date_start.strftime(
                        '%d/%m/%Y') + " to " + date_object_date_end.strftime(
                        '%d/%m/%Y'),
                    'invoice_amount': invoice_amount if invoice_amount else 0.0,
                    'invoice_tax': invoice_tax if invoice_tax else 0.0,
                    'total_invoice_amount': total_invoice_amount if total_invoice_amount else 0.0,
                    'partner_name': partner_name if partner_name else " ",
                    'location': location if location else " ",
                    'customer_vat': customer_vat if customer_vat else 0.0,
                    'vat_description': vat_description if vat_description else " ",

                }

                lines.append(res)
            if lines:
                return lines
            else:
                return []

        elif report_id == 'exempt_supplies':

            query = """

                          select 

            				max(company.name) as company_name,
            				account_move_line__move_id.company_id as company_id,
            				account_move_line__move_id.name as invoice_number,
            				account_move_line__move_id.invoice_date as invoice_date,
            				SUM(account_move_line.price_subtotal* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_amount,
            				SUM((account_move_line.price_total-account_move_line.price_subtotal)* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_tax,
            				SUM(account_move_line.price_total* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS total_invoice_amount,
            				max(rs.name) as partner_name,
            				max(rs.city) as location,
            				max(rs.vat) as customer_vat,
            				max(tax.name) as vat_description

            			FROM account_move_line_account_tax_rel tax_rel
                            JOIN account_tax tax ON tax.id = tax_rel.account_tax_id
                            JOIN account_move_line ON account_move_line.id = tax_rel.account_move_line_id 
                            LEFT JOIN account_tax src_tax ON src_tax.id = account_move_line.tax_line_id
                            LEFT JOIN account_tax src_group_tax ON src_group_tax.id = account_move_line.group_tax_id
                            JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
            				left join res_partner as rs on rs.id=account_move_line__move_id.partner_id
            				JOIN res_company company ON account_move_line.company_id = company.id
                            WHERE 
            				account_move_line__move_id.move_type IN ('out_invoice', 'out_refund')
            				and account_move_line__move_id.state = 'posted'
            				and tax.type_tax_use IN ('sale')
            				and  to_char(date_trunc('day',account_move_line__move_id.invoice_date),'YYYY-MM-DD')::date between %s and %s
            				and tax_rel.account_tax_id in %s
            				group by account_move_line__move_id.id

                        """
            # self.env.cr.execute(query, (
            #     date_object_date_start.strftime('%Y-%m-%d'), date_object_date_end.strftime('%Y-%m-%d'),tuple(tax_ids.ids),
            # ))
            self.env.cr.execute(query, (
                date_start, date_end, tuple(tax_ids),
            ))
            for row in self.env.cr.dictfetchall():
                sl += 1
                company_name = row['company_name'] if row['company_name'] else " "
                invoice_number = row['invoice_number'] if row['invoice_number'] else " "
                invoice_date = row['invoice_date'] if row['invoice_date'] else ""
                invoice_amount = row['invoice_amount'] if row['invoice_amount'] else 0.0
                invoice_tax = row['invoice_tax'] if row['invoice_tax'] else 0.0
                total_invoice_amount = row['total_invoice_amount'] if row['total_invoice_amount'] else 0.0
                partner_name = row['partner_name'] if row['partner_name'] else " "
                location = row['location'] if row['location'] else " "
                customer_vat = row['customer_vat'] if row['customer_vat'] else 0
                vat_description = row['vat_description'] if row['vat_description'] else " "
                company_value_id = row['company_id'] if row['company_id'] else " "
                if company_value_id:
                    vat = self.env['res.company'].browse(company_value_id).vat
                else:
                    vat = ""

                # date_start = data.date_start
                # date_end = data.date_end

                date_start = data['form']['date_start']
                date_end = data['form']['date_end']
                if date_start:
                    date_object_date_start = datetime.strptime(str(date_start), '%Y-%m-%d').date()
                if date_end:
                    date_object_date_end = datetime.strptime(str(date_end), '%Y-%m-%d').date()

                if invoice_date:
                    date_value = datetime.strptime(str(invoice_date), '%Y-%m-%d').date()
                    invoice_date = date_value.strftime('%d/%m/%Y')
                else:
                    invoice_date =" "

                res = {
                    'sl_no': sl,
                    'company_name': company_name,
                    'company_vat': vat,
                    'invoice_number': invoice_number if invoice_number else " ",
                    'invoice_date': invoice_date if invoice_date else 0.0,
                    'reporting_period': date_object_date_start.strftime(
                        '%d/%m/%Y') + " to " + date_object_date_end.strftime(
                        '%d/%m/%Y'),
                    'invoice_amount': invoice_amount if invoice_amount else 0.0,
                    'invoice_tax': invoice_tax if invoice_tax else 0.0,
                    'total_invoice_amount': total_invoice_amount if total_invoice_amount else 0.0,
                    'partner_name': partner_name if partner_name else " ",
                    'location': location if location else " ",
                    'customer_vat': customer_vat if customer_vat else 0.0,
                    'vat_description': vat_description if vat_description else " ",

                }

                lines.append(res)
            if lines:
                return lines
            else:
                return []

        elif report_id == 'goods_imported_into_uae':

            query = """

                          select 

            				max(company.name) as company_name,
            				account_move_line__move_id.company_id as company_id,
            				account_move_line__move_id.name as invoice_number,
            				account_move_line__move_id.invoice_date as invoice_date,
            				SUM(account_move_line.price_subtotal* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_amount,
            				SUM((account_move_line.price_total-account_move_line.price_subtotal)* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_tax,
            				SUM(account_move_line.price_total* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS total_invoice_amount,
            				max(rs.name) as partner_name,
            				max(rc.name) as location,
            				max(rs.vat) as customer_vat,
            				max(tax.name) as vat_description

            			FROM account_move_line_account_tax_rel tax_rel
                            JOIN account_tax tax ON tax.id = tax_rel.account_tax_id
                            JOIN account_move_line ON account_move_line.id = tax_rel.account_move_line_id 
                            LEFT JOIN account_tax src_tax ON src_tax.id = account_move_line.tax_line_id
                            LEFT JOIN account_tax src_group_tax ON src_group_tax.id = account_move_line.group_tax_id
                            JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
            				left join res_partner as rs on rs.id=account_move_line__move_id.partner_id
            				left join res_country as rc on rs.country_id=rc.id
            				JOIN res_company company ON account_move_line.company_id = company.id
                            WHERE 
            				account_move_line__move_id.move_type IN ('in_invoice', 'in_refund')
            				and account_move_line__move_id.state = 'posted'
            				and tax.type_tax_use IN ('purchase')
            				and  to_char(date_trunc('day',account_move_line__move_id.invoice_date),'YYYY-MM-DD')::date between %s and %s
            				and tax_rel.account_tax_id in %s
            				group by account_move_line__move_id.id

                        """
            # self.env.cr.execute(query, (
            #     date_object_date_start.strftime('%Y-%m-%d'), date_object_date_end.strftime('%Y-%m-%d'),tuple(tax_ids.ids),
            # ))
            self.env.cr.execute(query, (
                date_start, date_end, tuple(tax_ids),
            ))
            for row in self.env.cr.dictfetchall():
                sl += 1
                company_name = row['company_name'] if row['company_name'] else " "
                invoice_number = row['invoice_number'] if row['invoice_number'] else " "
                invoice_date = row['invoice_date'] if row['invoice_date'] else ""
                invoice_amount = row['invoice_amount'] if row['invoice_amount'] else 0.0
                invoice_tax = row['invoice_tax'] if row['invoice_tax'] else 0.0
                total_invoice_amount = row['total_invoice_amount'] if row['total_invoice_amount'] else 0.0
                partner_name = row['partner_name'] if row['partner_name'] else " "
                location = row['location'] if row['location'] else " "
                customer_vat = row['customer_vat'] if row['customer_vat'] else 0
                vat_description = row['vat_description'] if row['vat_description'] else " "
                company_value_id = row['company_id'] if row['company_id'] else " "
                if company_value_id:
                    vat = self.env['res.company'].browse(company_value_id).vat
                else:
                    vat = ""

                # date_start = data.date_start
                # date_end = data.date_end

                date_start = data['form']['date_start']
                date_end = data['form']['date_end']
                if date_start:
                    date_object_date_start = datetime.strptime(str(date_start), '%Y-%m-%d').date()
                if date_end:
                    date_object_date_end = datetime.strptime(str(date_end), '%Y-%m-%d').date()

                if invoice_date:
                    date_value = datetime.strptime(str(invoice_date), '%Y-%m-%d').date()
                    invoice_date = date_value.strftime('%d/%m/%Y')
                else:
                    invoice_date =" "

                res = {
                    'sl_no': sl,
                    'company_name': company_name,
                    'company_vat': vat,
                    'invoice_number': invoice_number if invoice_number else " ",
                    'invoice_date': invoice_date if invoice_date else 0.0,
                    'reporting_period': date_object_date_start.strftime(
                        '%d/%m/%Y') + " to " + date_object_date_end.strftime(
                        '%d/%m/%Y'),
                    'invoice_amount': invoice_amount if invoice_amount else 0.0,
                    'invoice_tax': invoice_tax if invoice_tax else 0.0,
                    'total_invoice_amount': total_invoice_amount if total_invoice_amount else 0.0,
                    'partner_name': partner_name if partner_name else " ",
                    'location': location if location else " ",
                    'customer_vat': customer_vat if customer_vat else 0.0,
                    'vat_description': vat_description if vat_description else " ",

                }

                lines.append(res)
            if lines:
                return lines
            else:
                return []

        elif report_id == 'adjustment_goods_import':

            query = """

                          select 

            				max(company.name) as company_name,
            				account_move_line__move_id.company_id as company_id,
            				account_move_line__move_id.name as invoice_number,
            				account_move_line__move_id.invoice_date as invoice_date,
            				SUM(account_move_line.price_subtotal* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_amount,
            				SUM((account_move_line.price_total-account_move_line.price_subtotal)* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_tax,
            				SUM(account_move_line.price_total* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS total_invoice_amount,
            				max(rs.name) as partner_name,
            				max(rc.name) as location,
            				max(rs.vat) as customer_vat,
            				max(tax.name) as vat_description

            			FROM account_move_line_account_tax_rel tax_rel
                            JOIN account_tax tax ON tax.id = tax_rel.account_tax_id
                            JOIN account_move_line ON account_move_line.id = tax_rel.account_move_line_id 
                            LEFT JOIN account_tax src_tax ON src_tax.id = account_move_line.tax_line_id
                            LEFT JOIN account_tax src_group_tax ON src_group_tax.id = account_move_line.group_tax_id
                            JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
            				left join res_partner as rs on rs.id=account_move_line__move_id.partner_id
            				left join res_country as rc on rs.country_id=rc.id
            				JOIN res_company company ON account_move_line.company_id = company.id
                            WHERE 
            				account_move_line__move_id.move_type IN ('in_invoice', 'in_refund')
            				and account_move_line__move_id.state = 'posted'
            				and tax.type_tax_use IN ('purchase')
            				and  to_char(date_trunc('day',account_move_line__move_id.invoice_date),'YYYY-MM-DD')::date between %s and %s
            				and tax_rel.account_tax_id in %s
            				group by account_move_line__move_id.id

                        """
            # self.env.cr.execute(query, (
            #     date_object_date_start.strftime('%Y-%m-%d'), date_object_date_end.strftime('%Y-%m-%d'),tuple(tax_ids.ids),
            # ))
            self.env.cr.execute(query, (
                date_start, date_end, tuple(tax_ids),
            ))
            for row in self.env.cr.dictfetchall():
                sl += 1
                company_name = row['company_name'] if row['company_name'] else " "
                invoice_number = row['invoice_number'] if row['invoice_number'] else " "
                invoice_date = row['invoice_date'] if row['invoice_date'] else ""
                invoice_amount = row['invoice_amount'] if row['invoice_amount'] else 0.0
                invoice_tax = row['invoice_tax'] if row['invoice_tax'] else 0.0
                total_invoice_amount = row['total_invoice_amount'] if row['total_invoice_amount'] else 0.0
                partner_name = row['partner_name'] if row['partner_name'] else " "
                location = row['location'] if row['location'] else " "
                customer_vat = row['customer_vat'] if row['customer_vat'] else 0
                vat_description = row['vat_description'] if row['vat_description'] else " "
                company_value_id = row['company_id'] if row['company_id'] else " "
                if company_value_id:
                    vat = self.env['res.company'].browse(company_value_id).vat
                else:
                    vat = ""

                # date_start = data.date_start
                # date_end = data.date_end

                date_start = data['form']['date_start']
                date_end = data['form']['date_end']
                if date_start:
                    date_object_date_start = datetime.strptime(str(date_start), '%Y-%m-%d').date()
                if date_end:
                    date_object_date_end = datetime.strptime(str(date_end), '%Y-%m-%d').date()

                if invoice_date:
                    date_value = datetime.strptime(str(invoice_date), '%Y-%m-%d').date()
                    invoice_date = date_value.strftime('%d/%m/%Y')
                else:
                    invoice_date =" "

                res = {
                    'sl_no': sl,
                    'company_name': company_name,
                    'company_vat': vat,
                    'invoice_number': invoice_number if invoice_number else " ",
                    'invoice_date': invoice_date if invoice_date else 0.0,
                    'reporting_period': date_object_date_start.strftime(
                        '%d/%m/%Y') + " to " + date_object_date_end.strftime(
                        '%d/%m/%Y'),
                    'invoice_amount': invoice_amount if invoice_amount else 0.0,
                    'invoice_tax': invoice_tax if invoice_tax else 0.0,
                    'total_invoice_amount': total_invoice_amount if total_invoice_amount else 0.0,
                    'partner_name': partner_name if partner_name else " ",
                    'location': location if location else " ",
                    'customer_vat': customer_vat if customer_vat else 0.0,
                    'vat_description': vat_description if vat_description else " ",

                }

                lines.append(res)
            if lines:
                return lines
            else:
                return []

        elif report_id == 'std_rated_purchases':

            query = """

                          select 

            				max(company.name) as company_name,
            				account_move_line__move_id.company_id as company_id,
            				account_move_line__move_id.name as invoice_number,
            				account_move_line__move_id.invoice_date as invoice_date,
            				account_move_line__move_id.invoice_date as refund_invoice_date,
            				SUM(account_move_line.price_subtotal* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_amount,
            				SUM((account_move_line.price_total-account_move_line.price_subtotal)* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_tax,
            				SUM(account_move_line.price_total* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS total_invoice_amount,
            				max(rs.name) as partner_name,
            				max(rs.city) as location,
            				max(rs.vat) as customer_vat,
            				max(tax.name) as vat_description

            			FROM account_move_line_account_tax_rel tax_rel
                            JOIN account_tax tax ON tax.id = tax_rel.account_tax_id
                            JOIN account_move_line ON account_move_line.id = tax_rel.account_move_line_id 
                            LEFT JOIN account_tax src_tax ON src_tax.id = account_move_line.tax_line_id
                            LEFT JOIN account_tax src_group_tax ON src_group_tax.id = account_move_line.group_tax_id
                            JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
            				left join res_partner as rs on rs.id=account_move_line__move_id.partner_id
            				JOIN res_company company ON account_move_line.company_id = company.id
                            WHERE 
            				account_move_line__move_id.move_type IN ('in_invoice', 'in_refund')
            				and account_move_line__move_id.state = 'posted'
            				and tax.type_tax_use IN ('purchase')
            				and  to_char(date_trunc('day',account_move_line__move_id.invoice_date),'YYYY-MM-DD')::date between %s and %s
            				and tax_rel.account_tax_id in %s
            				group by account_move_line__move_id.id

                        """
            # self.env.cr.execute(query, (
            #     date_object_date_start.strftime('%Y-%m-%d'), date_object_date_end.strftime('%Y-%m-%d'),tuple(tax_ids.ids),
            # ))
            self.env.cr.execute(query, (
                date_start, date_end, tuple(tax_ids),
            ))
            for row in self.env.cr.dictfetchall():
                sl += 1
                company_name = row['company_name'] if row['company_name'] else " "
                invoice_number = row['invoice_number'] if row['invoice_number'] else " "
                invoice_date = row['invoice_date'] if row['invoice_date'] else ""
                refund_invoice_date = row['refund_invoice_date'] if row['refund_invoice_date'] else ""
                invoice_amount = row['invoice_amount'] if row['invoice_amount'] else 0.0
                invoice_tax = row['invoice_tax'] if row['invoice_tax'] else 0.0
                total_invoice_amount = row['total_invoice_amount'] if row['total_invoice_amount'] else 0.0
                partner_name = row['partner_name'] if row['partner_name'] else " "
                location = row['location'] if row['location'] else " "
                customer_vat = row['customer_vat'] if row['customer_vat'] else 0
                vat_description = row['vat_description'] if row['vat_description'] else " "
                company_value_id = row['company_id'] if row['company_id'] else " "
                if company_value_id:
                    vat = self.env['res.company'].browse(company_value_id).vat
                else:
                    vat = ""

                # date_start = data.date_start
                # date_end = data.date_end

                date_start = data['form']['date_start']
                date_end = data['form']['date_end']
                if date_start:
                    date_object_date_start = datetime.strptime(str(date_start), '%Y-%m-%d').date()
                if date_end:
                    date_object_date_end = datetime.strptime(str(date_end), '%Y-%m-%d').date()

                if invoice_date:
                    date_value = datetime.strptime(str(invoice_date), '%Y-%m-%d').date()
                    invoice_date = date_value.strftime('%d/%m/%Y')
                else:
                    invoice_date =" "

                res = {
                    'sl_no': sl,
                    'company_name': company_name,
                    'company_vat': vat,
                    'invoice_number': invoice_number if invoice_number else " ",
                    'invoice_date': invoice_date if invoice_date else 0.0,
                    'refund_invoice_date': refund_invoice_date if refund_invoice_date else 0.0,
                    'reporting_period': date_object_date_start.strftime(
                        '%d/%m/%Y') + " to " + date_object_date_end.strftime(
                        '%d/%m/%Y'),
                    'invoice_amount': invoice_amount if invoice_amount else 0.0,
                    'invoice_tax': invoice_tax if invoice_tax else 0.0,
                    'total_invoice_amount': total_invoice_amount if total_invoice_amount else 0.0,
                    'partner_name': partner_name if partner_name else " ",
                    'location': location if location else " ",
                    'customer_vat': customer_vat if customer_vat else 0.0,
                    'vat_description': vat_description if vat_description else " ",

                }

                lines.append(res)
            if lines:
                return lines
            else:
                return []

        elif report_id == 'supplies_subjected_to_rcm':

            query = """

                          select 

            				max(company.name) as company_name,
            				account_move_line__move_id.company_id as company_id,
            				account_move_line__move_id.name as invoice_number,
            				account_move_line__move_id.invoice_date as invoice_date,
            				account_move_line__move_id.invoice_date as refund_invoice_date,
            				SUM(account_move_line.price_subtotal* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_amount,
            				SUM((account_move_line.price_total-account_move_line.price_subtotal)* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS invoice_tax,
            				SUM(account_move_line.price_total* (CASE WHEN account_move_line__move_id.move_type in ('in_refund','out_refund') THEN -1 ELSE 1 END)) AS total_invoice_amount,
            				max(rs.name) as partner_name,
            				max(rc.name) as location,
            				max(rs.vat) as customer_vat,
            				max(tax.name) as vat_description

            			FROM account_move_line_account_tax_rel tax_rel
                            JOIN account_tax tax ON tax.id = tax_rel.account_tax_id
                            JOIN account_move_line ON account_move_line.id = tax_rel.account_move_line_id 
                            LEFT JOIN account_tax src_tax ON src_tax.id = account_move_line.tax_line_id
                            LEFT JOIN account_tax src_group_tax ON src_group_tax.id = account_move_line.group_tax_id
                            JOIN account_move account_move_line__move_id ON account_move_line__move_id.id = account_move_line.move_id
            				left join res_partner as rs on rs.id=account_move_line__move_id.partner_id
            				left join res_country as rc on rs.country_id=rc.id
            				JOIN res_company company ON account_move_line.company_id = company.id
                            WHERE 
            				account_move_line__move_id.move_type IN ('in_invoice', 'in_refund')
            				and account_move_line__move_id.state = 'posted'
            				and tax.type_tax_use IN ('purchase')
            				and  to_char(date_trunc('day',account_move_line__move_id.invoice_date),'YYYY-MM-DD')::date between %s and %s
            				and tax_rel.account_tax_id in %s
            				group by account_move_line__move_id.id

                        """
            # self.env.cr.execute(query, (
            #     date_object_date_start.strftime('%Y-%m-%d'), date_object_date_end.strftime('%Y-%m-%d'),tuple(tax_ids.ids),
            # ))
            self.env.cr.execute(query, (
                date_start, date_end, tuple(tax_ids),
            ))
            for row in self.env.cr.dictfetchall():
                sl += 1
                company_name = row['company_name'] if row['company_name'] else " "
                invoice_number = row['invoice_number'] if row['invoice_number'] else " "
                invoice_date = row['invoice_date'] if row['invoice_date'] else ""
                refund_invoice_date = row['refund_invoice_date'] if row['refund_invoice_date'] else ""
                invoice_amount = row['invoice_amount'] if row['invoice_amount'] else 0.0
                invoice_tax = row['invoice_tax'] if row['invoice_tax'] else 0.0
                total_invoice_amount = row['total_invoice_amount'] if row['total_invoice_amount'] else 0.0
                partner_name = row['partner_name'] if row['partner_name'] else " "
                location = row['location'] if row['location'] else " "
                customer_vat = row['customer_vat'] if row['customer_vat'] else 0
                vat_description = row['vat_description'] if row['vat_description'] else " "
                company_value_id = row['company_id'] if row['company_id'] else " "
                if company_value_id:
                    vat = self.env['res.company'].browse(company_value_id).vat
                else:
                    vat = ""

                # date_start = data.date_start
                # date_end = data.date_end

                date_start = data['form']['date_start']
                date_end = data['form']['date_end']
                if date_start:
                    date_object_date_start = datetime.strptime(str(date_start), '%Y-%m-%d').date()
                if date_end:
                    date_object_date_end = datetime.strptime(str(date_end), '%Y-%m-%d').date()

                if invoice_date:
                    date_value = datetime.strptime(str(invoice_date), '%Y-%m-%d').date()
                    invoice_date = date_value.strftime('%d/%m/%Y')
                else:
                    invoice_date =" "

                res = {
                    'sl_no': sl,
                    'company_name': company_name,
                    'company_vat': vat,
                    'invoice_number': invoice_number if invoice_number else " ",
                    'invoice_date': invoice_date if invoice_date else 0.0,
                    'refund_invoice_date': refund_invoice_date if refund_invoice_date else 0.0,
                    'reporting_period': date_object_date_start.strftime(
                        '%d/%m/%Y') + " to " + date_object_date_end.strftime(
                        '%d/%m/%Y'),
                    'invoice_amount': invoice_amount if invoice_amount else 0.0,
                    'invoice_tax': invoice_tax if invoice_tax else 0.0,
                    'total_invoice_amount': total_invoice_amount if total_invoice_amount else 0.0,
                    'partner_name': partner_name if partner_name else " ",
                    'location': location if location else " ",
                    'customer_vat': customer_vat if customer_vat else 0.0,
                    'vat_description': vat_description if vat_description else " ",

                }

                lines.append(res)
            if lines:
                return lines
            else:
                return []






    # def get_lines(self, obj):
    #     lines = []
    #     customer = obj.customer_id
    #     domain = [
    #         ('date_order', '>=', obj.start_date),
    #         ('date_order', '<=', obj.end_date),
    #     ]
    #     if customer:
    #         domain.append(('partner_id', '=', customer.id))
    #     sale_order = self.env['sale.order'].search(domain)
    #     for value in sale_order:
    #         state = value.state
    #         if state == 'draft':
    #             state = 'Quotation'
    #         elif state == 'sent':
    #             state = 'Quotation sent'
    #         elif state == 'sale':
    #             state = 'Sales Order'
    #         elif state == 'done':
    #             state = 'Locked'
    #         elif state == 'cancel':
    #             state = 'Cancelled'
    #         vals = {
    #             'name': value.name,
    #             'customer': value.partner_id.name,
    #             'amount': value.amount_total,
    #             'date': value.date_order,
    #             'state': state
    #         }
    #         lines.append(vals)
    #     return lines

    def generate_xlsx_report(self, workbook, data, wizard_obj):
        for obj in wizard_obj:
            # lines = self.get_lines(data)
            # report_id = data.report_id
            font_size_8_left = workbook.add_format(
                {'bottom': True, 'top': True, 'left': True, 'font_size': 14, 'align': 'left'})
            font_size_8_center = workbook.add_format(
                {'bottom': True, 'top': True, 'left': True, 'font_size': 14, 'align': 'center'})
            report_id = data['form']['report_id']
            if report_id == 'std_rated_sales':
                worksheet = workbook.add_worksheet('Standard Rated supplies Excel Report')
                bold = workbook.add_format({'bold': True, 'align': 'center','bg_color': '#0070c0','color': 'white'})
                text = workbook.add_format({'font_size': 12, 'align': 'center'})
                worksheet.set_column(0, 0, 15)
                worksheet.set_column(1, 2, 25)
                worksheet.set_column(3, 3, 35)
                worksheet.set_column(4, 4, 25)
                worksheet.set_column(5, 5, 25)
                worksheet.set_column(6, 6, 25)
                worksheet.set_column(7, 7, 25)
                worksheet.set_column(8, 8, 25)
                worksheet.set_column(9, 9, 25)
                worksheet.set_column(10, 10, 25)
                worksheet.set_column(11, 11, 25)
                worksheet.set_column(12, 12, 25)
                worksheet.set_column(13, 13, 25)
                worksheet.set_column(14, 14, 25)
                worksheet.write('A1', 'Serial #', bold)
                worksheet.write('B1', 'Tax Payer TRN', bold)
                worksheet.write('C1', 'Company Name / Member Company Name (If applicable)', bold)
                worksheet.write('D1', 'Tax Invoice/Tax credit note  No', bold)
                worksheet.write('E1', 'Tax Invoice/Tax credit note  Date', bold)
                worksheet.write('F1', 'Reporting period', bold)
                worksheet.write('G1', 'Tax Invoice/Tax credit note Amount AED ', bold)
                worksheet.write('H1', 'VAT Amount AED', bold)
                worksheet.write('I1', 'Customer Name', bold)
                worksheet.write('J1', 'Customer TRN', bold)
                worksheet.write('K1', 'Clear description of the supply', bold)
                worksheet.write('L1', 'VAT Adjustments', bold)
                row = 1
                col = 0
                for res in self.get_lines(data):
                    worksheet.write(row, col, res['sl_no'], text)
                    worksheet.write(row, col + 1, res['company_vat'], text)
                    worksheet.write(row, col + 2, res['company_name'], text)
                    worksheet.write(row, col + 3, res['invoice_number'], text)
                    worksheet.write(row, col + 4, res['invoice_date'], text)
                    worksheet.write(row, col + 5, res['reporting_period'], text)
                    worksheet.write(row, col + 6, res['invoice_amount'], text)
                    worksheet.write(row, col + 7, res['invoice_tax'], text)
                    worksheet.write(row, col + 8, res['partner_name'], text)
                    worksheet.write(row, col + 9, res['customer_vat'], text)
                    worksheet.write(row, col + 10, res['vat_description'], text)
                    worksheet.write(row, col + 11, "", text)
                    row = row + 1
                    col = 0
                col = 0
                worksheet.merge_range(row, 0, row, 2, "TOTAL", font_size_8_left)

                total_cell_range3 = xl_range(1, 3, row - 1, 3)
                total_cell_range4 = xl_range(1, 4, row - 1, 4)
                total_cell_range5 = xl_range(1, 5, row - 1, 5)
                total_cell_range6 = xl_range(1, 6, row - 1, 6)
                total_cell_range7 = xl_range(1, 7, row - 1, 7)
                total_cell_range8 = xl_range(1, 8, row - 1, 8)
                total_cell_range9 = xl_range(1, 9, row - 1, 9)
                total_cell_range10 = xl_range(1, 10, row - 1, 10)
                total_cell_range11 = xl_range(1, 11, row - 1, 11)

                worksheet.write_formula(row, 3, '=SUM(' + total_cell_range3 + ')', font_size_8_center)
                worksheet.write_formula(row, 4, '=SUM(' + total_cell_range4 + ')', font_size_8_center)
                worksheet.write_formula(row, 5, '=SUM(' + total_cell_range5 + ')', font_size_8_center)
                worksheet.write_formula(row, 6, '=SUM(' + total_cell_range6 + ')', font_size_8_center)
                worksheet.write_formula(row, 7, '=SUM(' + total_cell_range7 + ')', font_size_8_center)
                worksheet.write_formula(row, 8, '=SUM(' + total_cell_range8 + ')', font_size_8_center)
                worksheet.write_formula(row, 9, '=SUM(' + total_cell_range9 + ')', font_size_8_center)
                worksheet.write_formula(row, 10, '=SUM(' + total_cell_range10 + ')', font_size_8_center)
                worksheet.write_formula(row, 11, '=SUM(' + total_cell_range11 + ')', font_size_8_center)

            elif report_id == 'out_of_scope_sales':
                worksheet = workbook.add_worksheet('Out of scope Sales')
                bold = workbook.add_format({'bold': True, 'align': 'center','bg_color': '#0070c0','color': 'white'})
                text = workbook.add_format({'font_size': 12, 'align': 'center'})
                worksheet.set_column(0, 0, 15)
                worksheet.set_column(1, 2, 25)
                worksheet.set_column(3, 3, 35)
                worksheet.set_column(4, 4, 25)
                worksheet.set_column(5, 5, 25)
                worksheet.set_column(6, 6, 25)
                worksheet.set_column(7, 7, 25)
                worksheet.set_column(8, 8, 25)
                worksheet.set_column(9, 9, 25)
                worksheet.set_column(10, 10, 25)
                worksheet.set_column(11, 11, 25)
                worksheet.set_column(12, 12, 25)
                worksheet.set_column(13, 13, 25)
                worksheet.set_column(14, 14, 25)
                worksheet.write('A1', 'Serial #', bold)
                worksheet.write('B1', 'Tax Payer TRN', bold)
                worksheet.write('C1', 'Company Name / Member Company Name (If applicable)', bold)
                worksheet.write('D1', 'Tax Invoice/Tax credit note  No', bold)
                worksheet.write('E1', 'Tax Invoice/Tax credit note  Date', bold)
                worksheet.write('F1', 'Reporting period', bold)
                worksheet.write('G1', 'Tax Invoice/Tax credit note Amount AED ', bold)
                worksheet.write('H1', 'VAT Amount AED', bold)
                worksheet.write('I1', 'Customer Name', bold)
                worksheet.write('J1', 'Customer TRN', bold)
                worksheet.write('K1', 'Clear description of the supply', bold)
                worksheet.write('L1', 'Reason of Out-of-Scope Sales treatment', bold)
                row = 1
                col = 0
                for res in self.get_lines(data):
                    worksheet.write(row, col, res['sl_no'], text)
                    worksheet.write(row, col + 1, res['company_vat'], text)
                    worksheet.write(row, col + 2, res['company_name'], text)
                    worksheet.write(row, col + 3, res['invoice_number'], text)
                    worksheet.write(row, col + 4, res['invoice_date'], text)
                    worksheet.write(row, col + 5, res['reporting_period'], text)
                    worksheet.write(row, col + 6, res['invoice_amount'], text)
                    worksheet.write(row, col + 7, res['invoice_tax'], text)
                    worksheet.write(row, col + 8, res['partner_name'], text)
                    worksheet.write(row, col + 9, res['customer_vat'], text)
                    worksheet.write(row, col + 10, res['vat_description'], text)
                    worksheet.write(row, col + 11, "", text)
                    row = row + 1
                    col = 0
                col = 0
                worksheet.merge_range(row, 0, row, 2, "TOTAL", font_size_8_left)

                total_cell_range3 = xl_range(1, 3, row - 1, 3)
                total_cell_range4 = xl_range(1, 4, row - 1, 4)
                total_cell_range5 = xl_range(1, 5, row - 1, 5)
                total_cell_range6 = xl_range(1, 6, row - 1, 6)
                total_cell_range7 = xl_range(1, 7, row - 1, 7)
                total_cell_range8 = xl_range(1, 8, row - 1, 8)
                total_cell_range9 = xl_range(1, 9, row - 1, 9)
                total_cell_range10 = xl_range(1, 10, row - 1, 10)
                total_cell_range11 = xl_range(1, 11, row - 1, 11)

                worksheet.write_formula(row, 3, '=SUM(' + total_cell_range3 + ')', font_size_8_center)
                worksheet.write_formula(row, 4, '=SUM(' + total_cell_range4 + ')', font_size_8_center)
                worksheet.write_formula(row, 5, '=SUM(' + total_cell_range5 + ')', font_size_8_center)
                worksheet.write_formula(row, 6, '=SUM(' + total_cell_range6 + ')', font_size_8_center)
                worksheet.write_formula(row, 7, '=SUM(' + total_cell_range7 + ')', font_size_8_center)
                worksheet.write_formula(row, 8, '=SUM(' + total_cell_range8 + ')', font_size_8_center)
                worksheet.write_formula(row, 9, '=SUM(' + total_cell_range9 + ')', font_size_8_center)
                worksheet.write_formula(row, 10, '=SUM(' + total_cell_range10 + ')', font_size_8_center)
                worksheet.write_formula(row, 11, '=SUM(' + total_cell_range11 + ')', font_size_8_center)

            elif report_id == 'tourist_refund_adj':
                worksheet = workbook.add_worksheet('Tourist Refund Adj')
                bold = workbook.add_format({'bold': True, 'align': 'center','bg_color': '#0070c0','color': 'white'})
                text = workbook.add_format({'font_size': 12, 'align': 'center'})
                worksheet.set_column(0, 0, 15)
                worksheet.set_column(1, 2, 25)
                worksheet.set_column(3, 3, 35)
                worksheet.set_column(4, 4, 25)
                worksheet.set_column(5, 5, 25)
                worksheet.set_column(6, 6, 25)
                worksheet.set_column(7, 7, 25)
                worksheet.set_column(8, 8, 25)
                worksheet.set_column(9, 9, 25)
                worksheet.set_column(10, 10, 25)
                worksheet.set_column(11, 11, 25)
                worksheet.set_column(12, 12, 25)
                worksheet.set_column(13, 13, 25)
                worksheet.set_column(14, 14, 25)
                worksheet.write('A1', 'Invoice #', bold)
                worksheet.write('B1', 'Tax Payer TRN', bold)
                worksheet.write('C1', 'Company Name / Member Company Name (If applicable)', bold)
                worksheet.write('D1', 'Invoice Date', bold)
                worksheet.write('E1', 'Reporting period', bold)
                worksheet.write('F1', 'Invoice Amount', bold)
                row = 1
                col = 0
                for res in self.get_lines(data):
                    worksheet.write(row, col, res['sl_no'], text)
                    worksheet.write(row, col + 1, res['company_vat'], text)
                    worksheet.write(row, col + 2, res['company_name'], text)
                    worksheet.write(row, col + 3, res['invoice_date'], text)
                    worksheet.write(row, col + 4, res['reporting_period'], text)
                    worksheet.write(row, col + 5, res['total_invoice_amount'], text)

                    row = row + 1
                    col = 0
                col = 0
                worksheet.merge_range(row, 0, row, 2, "TOTAL", font_size_8_left)

                total_cell_range3 = xl_range(1, 3, row - 1, 3)
                total_cell_range4 = xl_range(1, 4, row - 1, 4)
                total_cell_range5 = xl_range(1, 5, row - 1, 5)


                worksheet.write_formula(row, 3, '=SUM(' + total_cell_range3 + ')', font_size_8_center)
                worksheet.write_formula(row, 4, '=SUM(' + total_cell_range4 + ')', font_size_8_center)
                worksheet.write_formula(row, 5, '=SUM(' + total_cell_range5 + ')', font_size_8_center)

            elif report_id == 'import_of_services':
                worksheet = workbook.add_worksheet('Import of Services')
                bold = workbook.add_format({'bold': True, 'align': 'center','bg_color': '#0070c0','color': 'white'})
                text = workbook.add_format({'font_size': 12, 'align': 'center'})
                worksheet.set_column(0, 0, 15)
                worksheet.set_column(1, 2, 25)
                worksheet.set_column(3, 3, 35)
                worksheet.set_column(4, 4, 25)
                worksheet.set_column(5, 5, 25)
                worksheet.set_column(6, 6, 25)
                worksheet.set_column(7, 7, 25)
                worksheet.set_column(8, 8, 25)
                worksheet.set_column(9, 9, 25)
                worksheet.set_column(10, 10, 25)
                worksheet.set_column(11, 11, 25)
                worksheet.set_column(12, 12, 25)
                worksheet.set_column(13, 13, 25)
                worksheet.set_column(14, 14, 25)
                worksheet.write('A1', 'Serial #', bold)
                worksheet.write('B1', 'Tax Payer TRN', bold)
                worksheet.write('C1', 'Company Name / Member Company Name (If applicable)', bold)
                worksheet.write('D1', 'Tax Invoice/Tax credit note  No', bold)
                worksheet.write('E1', 'Tax Invoice/Tax credit note  Date', bold)
                worksheet.write('F1', 'Reporting period', bold)
                worksheet.write('G1', 'Invoice/credit note Amount AED ', bold)
                worksheet.write('H1', 'VAT Amount AED', bold)
                worksheet.write('I1', 'Supplier Name', bold)
                worksheet.write('J1', 'Location of the Supplier', bold)
                worksheet.write('K1', 'Clear description of the Transaction', bold)
                row = 1
                col = 0
                for res in self.get_lines(data):
                    worksheet.write(row, col, res['sl_no'], text)
                    worksheet.write(row, col + 1, res['company_vat'], text)
                    worksheet.write(row, col + 2, res['company_name'], text)
                    worksheet.write(row, col + 3, res['invoice_number'], text)
                    worksheet.write(row, col + 4, res['invoice_date'], text)
                    worksheet.write(row, col + 5, res['reporting_period'], text)
                    worksheet.write(row, col + 6, res['invoice_amount'], text)
                    worksheet.write(row, col + 7, res['invoice_tax'], text)
                    worksheet.write(row, col + 8, res['partner_name'], text)
                    worksheet.write(row, col + 9, res['location'], text)
                    worksheet.write(row, col + 10, res['vat_description'], text)
                    row = row + 1
                    col = 0
                col = 0
                worksheet.merge_range(row, 0, row, 2, "TOTAL", font_size_8_left)

                total_cell_range3 = xl_range(1, 3, row - 1, 3)
                total_cell_range4 = xl_range(1, 4, row - 1, 4)
                total_cell_range5 = xl_range(1, 5, row - 1, 5)
                total_cell_range6 = xl_range(1, 6, row - 1, 6)
                total_cell_range7 = xl_range(1, 7, row - 1, 7)
                total_cell_range8 = xl_range(1, 8, row - 1, 8)
                total_cell_range9 = xl_range(1, 9, row - 1, 9)
                total_cell_range10 = xl_range(1, 10, row - 1, 10)

                worksheet.write_formula(row, 3, '=SUM(' + total_cell_range3 + ')', font_size_8_center)
                worksheet.write_formula(row, 4, '=SUM(' + total_cell_range4 + ')', font_size_8_center)
                worksheet.write_formula(row, 5, '=SUM(' + total_cell_range5 + ')', font_size_8_center)
                worksheet.write_formula(row, 6, '=SUM(' + total_cell_range6 + ')', font_size_8_center)
                worksheet.write_formula(row, 7, '=SUM(' + total_cell_range7 + ')', font_size_8_center)
                worksheet.write_formula(row, 8, '=SUM(' + total_cell_range8 + ')', font_size_8_center)
                worksheet.write_formula(row, 9, '=SUM(' + total_cell_range9 + ')', font_size_8_center)
                worksheet.write_formula(row, 10, '=SUM(' + total_cell_range10 + ')', font_size_8_center)
            elif report_id == 'zero_rated_sales':
                worksheet = workbook.add_worksheet('Zero Rated Sales')
                bold = workbook.add_format({'bold': True, 'align': 'center','bg_color': '#0070c0','color': 'white'})
                text = workbook.add_format({'font_size': 12, 'align': 'center'})
                worksheet.set_column(0, 0, 15)
                worksheet.set_column(1, 2, 25)
                worksheet.set_column(3, 3, 35)
                worksheet.set_column(4, 4, 25)
                worksheet.set_column(5, 5, 25)
                worksheet.set_column(6, 6, 25)
                worksheet.set_column(7, 7, 25)
                worksheet.set_column(8, 8, 25)
                worksheet.set_column(9, 9, 25)
                worksheet.set_column(10, 10, 25)
                worksheet.set_column(11, 11, 25)
                worksheet.set_column(12, 12, 25)
                worksheet.set_column(13, 13, 25)
                worksheet.set_column(14, 14, 25)
                worksheet.write('A1', 'Serial #', bold)
                worksheet.write('B1', 'Tax Payer TRN', bold)
                worksheet.write('C1', 'Company Name / Member Company Name (If applicable)', bold)
                worksheet.write('D1', 'Tax Invoice/Tax credit note  No', bold)
                worksheet.write('E1', 'Tax Invoice/Tax credit note  Date', bold)
                worksheet.write('F1', 'Reporting period', bold)
                worksheet.write('G1', 'Tax Invoice/Tax credit note Amount AED ', bold)
                worksheet.write('H1', 'Customer Name', bold)
                worksheet.write('I1', 'Customer TRN', bold)
                worksheet.write('J1', 'Location of the Customer', bold)
                worksheet.write('K1', 'Clear description of the Supply', bold)
                row = 1
                col = 0
                for res in self.get_lines(data):
                    worksheet.write(row, col, res['sl_no'], text)
                    worksheet.write(row, col + 1, res['company_vat'], text)
                    worksheet.write(row, col + 2, res['company_name'], text)
                    worksheet.write(row, col + 3, res['invoice_number'], text)
                    worksheet.write(row, col + 4, res['invoice_date'], text)
                    worksheet.write(row, col + 5, res['reporting_period'], text)
                    worksheet.write(row, col + 6, res['total_invoice_amount'], text)
                    worksheet.write(row, col + 7, res['partner_name'], text)
                    worksheet.write(row, col + 8, res['customer_vat'], text)
                    worksheet.write(row, col + 9,res['location'], text)
                    worksheet.write(row, col + 10, res['vat_description'], text)
                    row = row + 1
                    col = 0
                col = 0
                worksheet.merge_range(row, 0, row, 2, "TOTAL", font_size_8_left)

                total_cell_range3 = xl_range(1, 3, row - 1, 3)
                total_cell_range4 = xl_range(1, 4, row - 1, 4)
                total_cell_range5 = xl_range(1, 5, row - 1, 5)
                total_cell_range6 = xl_range(1, 6, row - 1, 6)
                total_cell_range7 = xl_range(1, 7, row - 1, 7)
                total_cell_range8 = xl_range(1, 8, row - 1, 8)
                total_cell_range9 = xl_range(1, 9, row - 1, 9)
                total_cell_range10 = xl_range(1, 10, row - 1, 10)

                worksheet.write_formula(row, 3, '=SUM(' + total_cell_range3 + ')', font_size_8_center)
                worksheet.write_formula(row, 4, '=SUM(' + total_cell_range4 + ')', font_size_8_center)
                worksheet.write_formula(row, 5, '=SUM(' + total_cell_range5 + ')', font_size_8_center)
                worksheet.write_formula(row, 6, '=SUM(' + total_cell_range6 + ')', font_size_8_center)
                worksheet.write_formula(row, 7, '=SUM(' + total_cell_range7 + ')', font_size_8_center)
                worksheet.write_formula(row, 8, '=SUM(' + total_cell_range8 + ')', font_size_8_center)
                worksheet.write_formula(row, 9, '=SUM(' + total_cell_range9 + ')', font_size_8_center)
                worksheet.write_formula(row, 10, '=SUM(' + total_cell_range10 + ')', font_size_8_center)

            elif report_id == 'exempt_supplies':
                worksheet = workbook.add_worksheet('Exempt Supplies')
                bold = workbook.add_format({'bold': True, 'align': 'center','bg_color': '#0070c0','color': 'white'})
                text = workbook.add_format({'font_size': 12, 'align': 'center'})
                worksheet.set_column(0, 0, 15)
                worksheet.set_column(1, 2, 25)
                worksheet.set_column(3, 3, 35)
                worksheet.set_column(4, 4, 25)
                worksheet.set_column(5, 5, 25)
                worksheet.set_column(6, 6, 25)
                worksheet.set_column(7, 7, 25)
                worksheet.set_column(8, 8, 25)
                worksheet.set_column(9, 9, 25)
                worksheet.set_column(10, 10, 25)
                worksheet.set_column(11, 11, 25)
                worksheet.set_column(12, 12, 25)
                worksheet.set_column(13, 13, 25)
                worksheet.set_column(14, 14, 25)
                worksheet.write('A1', 'Serial #', bold)
                worksheet.write('B1', 'Tax Payer TRN', bold)
                worksheet.write('C1', 'Company Name / Member Company Name (If applicable)', bold)
                worksheet.write('D1', 'Tax Invoice/Tax credit note  No', bold)
                worksheet.write('E1', 'Tax Invoice/Tax credit note  Date', bold)
                worksheet.write('F1', 'Reporting period', bold)
                worksheet.write('G1', 'Tax Invoice/Tax credit note Amount AED ', bold)
                worksheet.write('H1', 'Customer Name', bold)
                worksheet.write('I1', 'Customer TRN', bold)
                worksheet.write('J1', 'Clear description of the Supply', bold)
                row = 1
                col = 0
                for res in self.get_lines(data):
                    worksheet.write(row, col, res['sl_no'], text)
                    worksheet.write(row, col + 1, res['company_vat'], text)
                    worksheet.write(row, col + 2, res['company_name'], text)
                    worksheet.write(row, col + 3, res['invoice_number'], text)
                    worksheet.write(row, col + 4, res['invoice_date'], text)
                    worksheet.write(row, col + 5, res['reporting_period'], text)
                    worksheet.write(row, col + 6, res['total_invoice_amount'], text)
                    worksheet.write(row, col + 7, res['partner_name'], text)
                    worksheet.write(row, col + 8, res['customer_vat'], text)
                    worksheet.write(row, col + 9, res['vat_description'], text)
                    row = row + 1
                    col = 0
                col = 0
                worksheet.merge_range(row, 0, row, 2, "TOTAL", font_size_8_left)

                total_cell_range3 = xl_range(1, 3, row - 1, 3)
                total_cell_range4 = xl_range(1, 4, row - 1, 4)
                total_cell_range5 = xl_range(1, 5, row - 1, 5)
                total_cell_range6 = xl_range(1, 6, row - 1, 6)
                total_cell_range7 = xl_range(1, 7, row - 1, 7)
                total_cell_range8 = xl_range(1, 8, row - 1, 8)
                total_cell_range9 = xl_range(1, 9, row - 1, 9)

                worksheet.write_formula(row, 3, '=SUM(' + total_cell_range3 + ')', font_size_8_center)
                worksheet.write_formula(row, 4, '=SUM(' + total_cell_range4 + ')', font_size_8_center)
                worksheet.write_formula(row, 5, '=SUM(' + total_cell_range5 + ')', font_size_8_center)
                worksheet.write_formula(row, 6, '=SUM(' + total_cell_range6 + ')', font_size_8_center)
                worksheet.write_formula(row, 7, '=SUM(' + total_cell_range7 + ')', font_size_8_center)
                worksheet.write_formula(row, 8, '=SUM(' + total_cell_range8 + ')', font_size_8_center)
                worksheet.write_formula(row, 9, '=SUM(' + total_cell_range9 + ')', font_size_8_center)
            elif report_id == 'goods_imported_into_uae':
                worksheet = workbook.add_worksheet('Goods Imported into UAE')
                bold = workbook.add_format({'bold': True, 'align': 'center','bg_color': '#0070c0','color': 'white'})
                text = workbook.add_format({'font_size': 12, 'align': 'center'})
                worksheet.set_column(0, 0, 15)
                worksheet.set_column(1, 2, 25)
                worksheet.set_column(3, 3, 35)
                worksheet.set_column(4, 4, 25)
                worksheet.set_column(5, 5, 25)
                worksheet.set_column(6, 6, 25)
                worksheet.set_column(7, 7, 25)
                worksheet.set_column(8, 8, 25)
                worksheet.set_column(9, 9, 25)
                worksheet.set_column(10, 10, 25)
                worksheet.set_column(11, 11, 25)
                worksheet.set_column(12, 12, 25)
                worksheet.set_column(13, 13, 25)
                worksheet.set_column(14, 14, 25)
                worksheet.write('A1', 'Serial #', bold)
                worksheet.write('B1', 'Tax Payer TRN', bold)
                worksheet.write('C1', 'Company Name / Member Company Name (If applicable)', bold)
                worksheet.write('D1', 'Tax Invoice/Tax credit note  No', bold)
                worksheet.write('E1', 'Tax Invoice/Tax credit note  Date', bold)
                worksheet.write('F1', 'Reporting period', bold)
                worksheet.write('G1', 'Invoice/credit note Amount AED ', bold)
                worksheet.write('H1', 'VAT Amount AED', bold)
                worksheet.write('I1', 'Supplier Name', bold)
                worksheet.write('J1', 'Location of the Supplier', bold)
                worksheet.write('K1', 'Name of the Customs Authority', bold)
                worksheet.write('L1', 'Customs Declaration Number', bold)
                worksheet.write('M1', 'Clear description of the Transaction', bold)
                row = 1
                col = 0
                for res in self.get_lines(data):
                    worksheet.write(row, col, res['sl_no'], text)
                    worksheet.write(row, col + 1, res['company_vat'], text)
                    worksheet.write(row, col + 2, res['company_name'], text)
                    worksheet.write(row, col + 3, res['invoice_number'], text)
                    worksheet.write(row, col + 4, res['invoice_date'], text)
                    worksheet.write(row, col + 5, res['reporting_period'], text)
                    worksheet.write(row, col + 6, res['invoice_amount'], text)
                    worksheet.write(row, col + 7, res['invoice_tax'], text)
                    worksheet.write(row, col + 8, res['partner_name'], text)
                    worksheet.write(row, col + 9, res['location'], text)
                    worksheet.write(row, col + 10, " ", text)
                    worksheet.write(row, col + 11, " ", text)
                    worksheet.write(row, col + 12, res['vat_description'], text)
                    row = row + 1
                    col = 0
                col = 0
                worksheet.merge_range(row, 0, row, 2, "TOTAL", font_size_8_left)

                total_cell_range3 = xl_range(1, 3, row - 1, 3)
                total_cell_range4 = xl_range(1, 4, row - 1, 4)
                total_cell_range5 = xl_range(1, 5, row - 1, 5)
                total_cell_range6 = xl_range(1, 6, row - 1, 6)
                total_cell_range7 = xl_range(1, 7, row - 1, 7)
                total_cell_range8 = xl_range(1, 8, row - 1, 8)
                total_cell_range9 = xl_range(1, 9, row - 1, 9)
                total_cell_range10 = xl_range(1, 10, row - 1, 10)
                total_cell_range11 = xl_range(1, 11, row - 1, 11)
                total_cell_range12 = xl_range(1, 12, row - 1, 12)

                worksheet.write_formula(row, 3, '=SUM(' + total_cell_range3 + ')', font_size_8_center)
                worksheet.write_formula(row, 4, '=SUM(' + total_cell_range4 + ')', font_size_8_center)
                worksheet.write_formula(row, 5, '=SUM(' + total_cell_range5 + ')', font_size_8_center)
                worksheet.write_formula(row, 6, '=SUM(' + total_cell_range6 + ')', font_size_8_center)
                worksheet.write_formula(row, 7, '=SUM(' + total_cell_range7 + ')', font_size_8_center)
                worksheet.write_formula(row, 8, '=SUM(' + total_cell_range8 + ')', font_size_8_center)
                worksheet.write_formula(row, 9, '=SUM(' + total_cell_range9 + ')', font_size_8_center)
                worksheet.write_formula(row, 10, '=SUM(' + total_cell_range10 + ')', font_size_8_center)
                worksheet.write_formula(row, 11, '=SUM(' + total_cell_range11 + ')', font_size_8_center)
                worksheet.write_formula(row, 12, '=SUM(' + total_cell_range12 + ')', font_size_8_center)
            elif report_id == 'adjustment_goods_import':
                worksheet = workbook.add_worksheet('Adjustment - Goods Import')
                bold = workbook.add_format({'bold': True, 'align': 'center','bg_color': '#0070c0','color': 'white'})
                text = workbook.add_format({'font_size': 12, 'align': 'center'})
                worksheet.set_column(0, 0, 15)
                worksheet.set_column(1, 2, 25)
                worksheet.set_column(3, 3, 35)
                worksheet.set_column(4, 4, 25)
                worksheet.set_column(5, 5, 25)
                worksheet.set_column(6, 6, 25)
                worksheet.set_column(7, 7, 25)
                worksheet.set_column(8, 8, 25)
                worksheet.set_column(9, 9, 25)
                worksheet.set_column(10, 10, 25)
                worksheet.set_column(11, 11, 25)
                worksheet.set_column(12, 12, 25)
                worksheet.set_column(13, 13, 25)
                worksheet.set_column(14, 14, 25)
                worksheet.write('A1', 'Serial #', bold)
                worksheet.write('B1', 'Tax Payer TRN', bold)
                worksheet.write('C1', 'Company Name / Member Company Name (If applicable)', bold)
                worksheet.write('D1', 'Tax Invoice/Tax credit note  No', bold)
                worksheet.write('E1', 'Invoice/credit note  Date', bold)
                worksheet.write('F1', 'Reporting period', bold)
                worksheet.write('G1', 'Invoice/credit note Amount AED ', bold)
                worksheet.write('H1', 'VAT Amount AED', bold)
                worksheet.write('I1', 'Supplier Name', bold)
                worksheet.write('J1', 'Location of the Supplier', bold)
                worksheet.write('K1', 'Name of the Customs Authority', bold)
                worksheet.write('L1', 'Customs Declaration Number', bold)
                worksheet.write('M1', 'Reason for the adjustment', bold)
                row = 1
                col = 0
                for res in self.get_lines(data):
                    worksheet.write(row, col, res['sl_no'], text)
                    worksheet.write(row, col + 1, res['company_vat'], text)
                    worksheet.write(row, col + 2, res['company_name'], text)
                    worksheet.write(row, col + 3, res['invoice_number'], text)
                    worksheet.write(row, col + 4, res['invoice_date'], text)
                    worksheet.write(row, col + 5, res['reporting_period'], text)
                    worksheet.write(row, col + 6, res['invoice_amount'], text)
                    worksheet.write(row, col + 7, res['invoice_tax'], text)
                    worksheet.write(row, col + 8, res['partner_name'], text)
                    worksheet.write(row, col + 9, res['location'], text)
                    worksheet.write(row, col + 10, " ", text)
                    worksheet.write(row, col + 11, " ", text)
                    worksheet.write(row, col + 12, " ", text)
                    row = row + 1
                col = 0
                col = 0
                worksheet.merge_range(row, 0, row, 2, "TOTAL", font_size_8_left)

                total_cell_range3 = xl_range(1, 3, row - 1, 3)
                total_cell_range4 = xl_range(1, 4, row - 1, 4)
                total_cell_range5 = xl_range(1, 5, row - 1, 5)
                total_cell_range6 = xl_range(1, 6, row - 1, 6)
                total_cell_range7 = xl_range(1, 7, row - 1, 7)
                total_cell_range8 = xl_range(1, 8, row - 1, 8)
                total_cell_range9 = xl_range(1, 9, row - 1, 9)
                total_cell_range10 = xl_range(1, 10, row - 1, 10)
                total_cell_range11 = xl_range(1, 11, row - 1, 11)
                total_cell_range12 = xl_range(1, 12, row - 1, 12)

                worksheet.write_formula(row, 3, '=SUM(' + total_cell_range3 + ')', font_size_8_center)
                worksheet.write_formula(row, 4, '=SUM(' + total_cell_range4 + ')', font_size_8_center)
                worksheet.write_formula(row, 5, '=SUM(' + total_cell_range5 + ')', font_size_8_center)
                worksheet.write_formula(row, 6, '=SUM(' + total_cell_range6 + ')', font_size_8_center)
                worksheet.write_formula(row, 7, '=SUM(' + total_cell_range7 + ')', font_size_8_center)
                worksheet.write_formula(row, 8, '=SUM(' + total_cell_range8 + ')', font_size_8_center)
                worksheet.write_formula(row, 9, '=SUM(' + total_cell_range9 + ')', font_size_8_center)
                worksheet.write_formula(row, 10, '=SUM(' + total_cell_range10 + ')', font_size_8_center)
                worksheet.write_formula(row, 11, '=SUM(' + total_cell_range11 + ')', font_size_8_center)
                worksheet.write_formula(row, 12, '=SUM(' + total_cell_range12 + ')', font_size_8_center)

            elif report_id == 'std_rated_purchases':
                worksheet = workbook.add_worksheet('Std Rated Purchases')
                bold = workbook.add_format({'bold': True, 'align': 'center','bg_color': '#0070c0','color': 'white'})
                text = workbook.add_format({'font_size': 12, 'align': 'center'})
                worksheet.set_column(0, 0, 15)
                worksheet.set_column(1, 2, 25)
                worksheet.set_column(3, 3, 35)
                worksheet.set_column(4, 4, 25)
                worksheet.set_column(5, 5, 25)
                worksheet.set_column(6, 6, 25)
                worksheet.set_column(7, 7, 25)
                worksheet.set_column(8, 8, 25)
                worksheet.set_column(9, 9, 25)
                worksheet.set_column(10, 10, 25)
                worksheet.set_column(11, 11, 25)
                worksheet.set_column(12, 12, 25)
                worksheet.set_column(13, 13, 25)
                worksheet.set_column(14, 14, 25)
                worksheet.write('A1', 'Serial #', bold)
                worksheet.write('B1', 'Tax Payer TRN', bold)
                worksheet.write('C1', 'Company Name / Member Company Name (If applicable)', bold)
                worksheet.write('D1', 'Tax Invoice/Tax credit note  No', bold)
                worksheet.write('E1', 'Tax Invoice/Tax credit note  Date', bold)
                worksheet.write('F1', 'Tax Invoice/Tax credit note Received Date', bold)
                worksheet.write('G1', 'Reporting period', bold)
                worksheet.write('H1', 'Tax Invoice/Tax credit note Amount AED ', bold)
                worksheet.write('I1', 'VAT Amount AED', bold)
                worksheet.write('J1', 'VAT Amount Recovered AED', bold)
                worksheet.write('K1', 'Supplier Name', bold)
                worksheet.write('L1', 'Supplier  TRN', bold)
                worksheet.write('M1', 'Clear description of the supply', bold)
                worksheet.write('N1', 'VAT Adjustments', bold)

                row = 1
                col = 0
                for res in self.get_lines(data):
                    worksheet.write(row, col, res['sl_no'], text)
                    worksheet.write(row, col + 1, res['company_vat'], text)
                    worksheet.write(row, col + 2, res['company_name'], text)
                    worksheet.write(row, col + 3, res['invoice_number'], text)
                    worksheet.write(row, col + 4, res['invoice_date'], text)
                    worksheet.write(row, col + 5, " ", text)
                    worksheet.write(row, col + 6, res['reporting_period'], text)
                    worksheet.write(row, col + 7, res['invoice_amount'], text)
                    worksheet.write(row, col + 8, res['invoice_tax'], text)
                    worksheet.write(row, col + 9, "", text)
                    worksheet.write(row, col + 10, res['partner_name'], text)
                    worksheet.write(row, col + 11, res['customer_vat'], text)
                    worksheet.write(row, col + 12, res['vat_description'], text)
                    worksheet.write(row, col + 13, " ", text)
                    row = row + 1
                    col = 0
                col = 0
                worksheet.merge_range(row, 0, row, 2, "TOTAL", font_size_8_left)

                total_cell_range3 = xl_range(1, 3, row - 1, 3)
                total_cell_range4 = xl_range(1, 4, row - 1, 4)
                total_cell_range5 = xl_range(1, 5, row - 1, 5)
                total_cell_range6 = xl_range(1, 6, row - 1, 6)
                total_cell_range7 = xl_range(1, 7, row - 1, 7)
                total_cell_range8 = xl_range(1, 8, row - 1, 8)
                total_cell_range9 = xl_range(1, 9, row - 1, 9)
                total_cell_range10 = xl_range(1, 10, row - 1, 10)
                total_cell_range11 = xl_range(1, 11, row - 1, 11)
                total_cell_range12 = xl_range(1, 12, row - 1, 12)
                total_cell_range13 = xl_range(1, 13, row - 1, 13)

                worksheet.write_formula(row, 3, '=SUM(' + total_cell_range3 + ')', font_size_8_center)
                worksheet.write_formula(row, 4, '=SUM(' + total_cell_range4 + ')', font_size_8_center)
                worksheet.write_formula(row, 5, '=SUM(' + total_cell_range5 + ')', font_size_8_center)
                worksheet.write_formula(row, 6, '=SUM(' + total_cell_range6 + ')', font_size_8_center)
                worksheet.write_formula(row, 7, '=SUM(' + total_cell_range7 + ')', font_size_8_center)
                worksheet.write_formula(row, 8, '=SUM(' + total_cell_range8 + ')', font_size_8_center)
                worksheet.write_formula(row, 9, '=SUM(' + total_cell_range9 + ')', font_size_8_center)
                worksheet.write_formula(row, 10, '=SUM(' + total_cell_range10 + ')', font_size_8_center)
                worksheet.write_formula(row, 11, '=SUM(' + total_cell_range11 + ')', font_size_8_center)
                worksheet.write_formula(row, 12, '=SUM(' + total_cell_range12 + ')', font_size_8_center)
                worksheet.write_formula(row, 13, '=SUM(' + total_cell_range13 + ')', font_size_8_center)

            elif report_id == 'supplies_subjected_to_rcm':
                worksheet = workbook.add_worksheet('Supplies subject to RCM')
                bold = workbook.add_format({'bold': True, 'align': 'center','bg_color': '#0070c0','color': 'white'})
                text = workbook.add_format({'font_size': 12, 'align': 'center'})
                worksheet.set_column(0, 0, 15)
                worksheet.set_column(1, 2, 25)
                worksheet.set_column(3, 3, 35)
                worksheet.set_column(4, 4, 25)
                worksheet.set_column(5, 5, 25)
                worksheet.set_column(6, 6, 25)
                worksheet.set_column(7, 7, 25)
                worksheet.set_column(8, 8, 25)
                worksheet.set_column(9, 9, 25)
                worksheet.set_column(10, 10, 25)
                worksheet.set_column(11, 11, 25)
                worksheet.set_column(12, 12, 25)
                worksheet.set_column(13, 13, 25)
                worksheet.set_column(14, 14, 25)
                worksheet.write('A1', 'Serial #', bold)
                worksheet.write('B1', 'Tax Payer TRN', bold)
                worksheet.write('C1', 'Company Name / Member Company Name (If applicable)', bold)
                worksheet.write('D1', 'Tax Invoice/Tax credit note  No', bold)
                worksheet.write('E1', 'Invoice/credit note  Date', bold)
                worksheet.write('F1', 'Reporting period', bold)
                worksheet.write('G1', 'Invoice/credit note Amount AED ', bold)
                worksheet.write('H1', 'VAT Amount AED', bold)
                worksheet.write('I1', 'Supplier Name', bold)
                worksheet.write('J1', 'Location of the Supplier', bold)
                worksheet.write('K1', 'Clear description of the transaction', bold)

                row = 1
                col = 0
                for res in self.get_lines(data):
                    worksheet.write(row, col, res['sl_no'], text)
                    worksheet.write(row, col + 1, res['company_vat'], text)
                    worksheet.write(row, col + 2, res['company_name'], text)
                    worksheet.write(row, col + 3, res['invoice_number'], text)
                    worksheet.write(row, col + 4, res['invoice_date'], text)
                    worksheet.write(row, col + 5, res['reporting_period'], text)
                    worksheet.write(row, col + 6, res['invoice_amount'], text)
                    worksheet.write(row, col + 7, res['invoice_tax'], text)
                    worksheet.write(row, col + 8, res['partner_name'], text)
                    worksheet.write(row, col + 9, res['location'], text)
                    worksheet.write(row, col + 10, res['vat_description'], text)
                    row = row + 1
                    col = 0
                col = 0
                worksheet.merge_range(row, 0, row, 2, "TOTAL", font_size_8_left)

                total_cell_range3 = xl_range(1, 3, row - 1, 3)
                total_cell_range4 = xl_range(1, 4, row - 1, 4)
                total_cell_range5 = xl_range(1, 5, row - 1, 5)
                total_cell_range6 = xl_range(1, 6, row - 1, 6)
                total_cell_range7 = xl_range(1, 7, row - 1, 7)
                total_cell_range8 = xl_range(1, 8, row - 1, 8)
                total_cell_range9 = xl_range(1, 9, row - 1, 9)
                total_cell_range10 = xl_range(1, 10, row - 1, 10)

                worksheet.write_formula(row, 3, '=SUM(' + total_cell_range3 + ')', font_size_8_center)
                worksheet.write_formula(row, 4, '=SUM(' + total_cell_range4 + ')', font_size_8_center)
                worksheet.write_formula(row, 5, '=SUM(' + total_cell_range5 + ')', font_size_8_center)
                worksheet.write_formula(row, 6, '=SUM(' + total_cell_range6 + ')', font_size_8_center)
                worksheet.write_formula(row, 7, '=SUM(' + total_cell_range7 + ')', font_size_8_center)
                worksheet.write_formula(row, 8, '=SUM(' + total_cell_range8 + ')', font_size_8_center)
                worksheet.write_formula(row, 9, '=SUM(' + total_cell_range9 + ')', font_size_8_center)
                worksheet.write_formula(row, 10, '=SUM(' + total_cell_range10 + ')', font_size_8_center)
