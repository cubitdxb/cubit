import base64
import io
from odoo import models, api
from datetime import datetime, timedelta
from operator import itemgetter
import re
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class BusinessOperationXlsx(models.AbstractModel):
    _name = 'report.cubit_crm_reports.report_business_operation_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, complaints):

        user = self.env.user
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        company = self.env.user.company_id
        search_condition = []
        if data:
            start = datetime.combine(datetime.strptime(data['form'][0]['date_from'], '%Y-%m-%d'), datetime.min.time())
            end = datetime.combine(datetime.strptime(data['form'][0]['date_to'], '%Y-%m-%d'), datetime.max.time())
            search_condition = [('date_order', '>=', start),
                                ('date_order', '<=', end), ]
                
            sale_orders = self.env['sale.order'].search(search_condition)
            sheet = workbook.add_worksheet('Business Operation Report')
            merge_format = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter', })
            merge_format.set_font_size(16)
            bold = workbook.add_format({'bold':True})
            row = 1
            column = 0
            sheet.set_column(column, column, 15)
            sheet.set_column(column + 2, column + 2, 15)
            sheet.set_column(column + 4, column + 4, 15)
            sheet.set_column(column + 6, column + 6, 15)
            sheet.merge_range('B2:L2', 'Business Operation Report', merge_format)
            # if company:
            #     logo = io.BytesIO(base64.b64decode(company.logo))
            #     sheet.insert_image(1, 0, "image.png", {'image_data': logo,'x_scale':0.125, 'y_scale':0.27,'border':None})

            sheet.merge_range('B3:D3', 'From Date', merge_format)
            sheet.merge_range('E3:L3', start.strftime('%d/%m/%Y'), merge_format)
            sheet.merge_range('B4:D4', 'To Date', merge_format)
            sheet.merge_range('E4:L4', end.strftime('%d/%m/%Y'), merge_format)
            row += 3
            sheet.write(row, column, '')
            row += 1
            sheet.write(row, column, 'SO #', bold)
            sheet.set_column(column + 1, column + 1, 15)
            sheet.write(row, column + 1, 'SO Date ', bold)
            sheet.set_column(column + 2, column + 2, 25)
            sheet.write(row, column + 2, 'Customer Name', bold)
            sheet.set_column(column + 3, column + 3, 15)
            sheet.write(row, column + 3, 'SO REF', bold)
            sheet.set_column(column + 4, column + 4, 25)
            sheet.write(row, column + 4, 'Email Confirmation', bold)
            sheet.set_column(column + 5, column + 5, 15)
            sheet.write(row, column + 5, 'Cust. PO No.', bold)
            sheet.set_column(column + 6, column + 6, 15)
            sheet.write(row, column + 6, 'SO VALUE', bold)
            sheet.set_column(column + 7, column + 7, 15)
            sheet.write(row, column + 7, 'VAT', bold)
            sheet.set_column(column + 8, column + 8, 45)
            sheet.write(row, column + 8, 'TOTAL SO VALUE INCLUDING VAT', bold)
            sheet.set_column(column + 9, column + 9, 30)
            sheet.write(row, column + 9, 'Sales Person Name', bold)
            sheet.set_column(column + 10, column + 10, 30)
            sheet.write(row, column + 10, 'Customer Payment Term', bold)
            sheet.set_column(column + 11, column + 11, 25)
            sheet.write(row, column + 11, 'Supplier Name', bold)

            sheet.set_column(column + 12, column + 12, 15)
            sheet.write(row, column + 12, 'LPO No.', bold)
            sheet.set_column(column + 13, column + 13, 15)
            sheet.write(row, column + 13, 'LPO Date', bold)
            
            sheet.set_column(column + 14, column + 14, 15)
            sheet.write(row, column + 14, 'LPO Value', bold)
            sheet.set_column(column + 15, column + 7, 15)
            sheet.write(row, column + 15, 'LPO VAT', bold)
            sheet.set_column(column + 16, column + 16, 15)
            sheet.write(row, column + 16, 'LPO No with VAT', bold)
            sheet.set_column(column + 17, column + 17, 30)
            sheet.write(row, column + 17, 'ETA Date (DD/MM/YY)', bold)
            sheet.set_column(column + 18, column + 18, 20)
            sheet.write(row, column + 18, 'ETA As per Week', bold)
            sheet.set_column(column + 19, column + 19, 30)
            sheet.write(row, column + 19, 'ETA as per Month (MM/YY)', bold)

            sheet.set_column(column + 20, column + 20, 15)
            sheet.write(row, column + 20, 'Delivery Status.', bold)
            sheet.set_column(column + 21, column + 21, 30)
            sheet.write(row, column + 21, 'Customer Invoice Status', bold)
            
            sheet.set_column(column + 22, column + 22, 30)
            sheet.write(row, column + 22, 'Customer invoice ref id', bold)
            sheet.set_column(column + 23, column + 23, 30)
            sheet.write(row, column + 23, 'Customer invoiced Amount', bold)
            sheet.set_column(column + 24, column + 24, 15)
            sheet.write(row, column + 24, 'Paid amount', bold)
            sheet.set_column(column + 25, column + 25, 15)
            sheet.write(row, column + 25, 'Balance', bold)
            sheet.set_column(column + 26, column + 26, 25)
            sheet.write(row, column + 26, 'Signoff Status', bold)
            sheet.set_column(column + 27, column + 27, 25)
            sheet.write(row, column + 27, 'CUBIT SERVICE COST', bold)

            sheet.set_column(column + 28, column + 28, 25)
            sheet.write(row, column + 28, 'TOTAL FINAL COST', bold)
            sheet.set_column(column + 29, column + 29, 15)
            sheet.write(row, column + 29, 'GP', bold)
            
            if sale_orders:
                
                # row = row+1
                t_count = 0
                for service in sale_orders:
                    row += 1
                    t_count += 1
                    sheet.write(row, column, service.name if service.name else '')
                    sheet.write(row, column + 1, service.create_date.strftime('%d/%m/%Y') if service.create_date else '')
                    sheet.write(row, column + 2, service.partner_id.name if service.partner_id else '')
                    sheet.write(row, column + 3, service.client_order_ref if service.client_order_ref else '')
                    sheet.write(row, column + 4, "yes" if service.lpo_email else 'No')
                    sheet.write(row, column + 5, service.lpo_number if service.lpo_number else '')
                    sheet.write(row, column + 6, service.amount_untaxed if service.amount_untaxed else '')
                    sheet.write(row, column + 7, service.amount_tax if service.amount_tax else '')
                    sheet.write(row, column + 8, service.amount_total if service.amount_total else '')
                    sheet.write(row, column + 9, service.user_id.name if service.user_id else '')
                    sheet.write(row, column + 10, service.payment_term_id.name if service.payment_term_id else '')
                    
                    po = self.env['purchase.order'].search([('sale_id', '=', service.id)])
                    for rec in po:
                        sheet.write(row, column + 11, rec.partner_id.name if rec.partner_id else '')
                        sheet.write(row, column + 12, service.po_number if service.po_number else '')
                        sheet.write(row, column + 13, rec.create_date.strftime('%d/%m/%Y') if rec.create_date else '')
                        # sheet.write(row, column + 14, rec.amount_total if rec.amount_total else 0.0)
                        sheet.write(row, column + 14, rec.amount_untaxed if rec.amount_untaxed else 0.0)
                        tax = 0.0
                        for line in rec.order_line:
                            # tax += line.amount_tax1
                            tax += line.price_tax
                        invoice_names=""
                        if service.invoice_ids:
                            names_list = [names.name for names in service.invoice_ids]
                            invoices = list(set(names_list))
                            join_invoices_number = ', '.join(invoices)
                            invoice_names = join_invoices_number
                        else:
                            invoice_names = " "


                        sheet.write(row, column + 15, tax if tax else 0.0)
                        sheet.write(row, column + 16, rec.amount_total if rec.amount_total else 0.0)
                        sheet.write(row, column + 17, rec.expected_time_of_arrival.strftime('%d/%m/%Y') if rec.expected_time_of_arrival else '')
                        sheet.write(row, column + 18, rec.expected_week_of_arrival if rec.expected_week_of_arrival else '')
                        sheet.write(row, column + 19, str(rec.expected_month_of_arrival) + "/" + str(rec.expected_year_of_arrival) if rec.expected_month_of_arrival else '')
                        sheet.write(row, column + 20, service.delivery_terms.name if service.delivery_terms else '')
                        sheet.write(row, column + 21, dict(service._fields['sale_to_invoice_status'].selection).get(service.sale_to_invoice_status) if service.sale_to_invoice_status else '')
                        # sheet.write(row, column + 22, service.invoice_ids[0].name if service.invoice_ids else '')
                        sheet.write(row, column + 22, invoice_names)
                        sheet.write(row, column + 23, service.invoiced_amount if service.invoiced_amount else '')
                        sheet.write(row, column + 24, service.amount_paid_invoice if service.amount_paid_invoice else '')
                        sheet.write(row, column + 25, service.invoiced_amount - service.amount_paid_invoice or 0.0)
                        sheet.write(row, column + 26, dict(service._fields['state'].selection).get(service.state) if service.state else '')
                        sheet.write(row, column + 27, service.cubit_service_cost_price_total if service.cubit_service_cost_price_total else 0.0)
                        sheet.write(row, column + 28, service.actual_cost_price_total if service.actual_cost_price_total else 0.0)
                        sheet.write(row, column + 29, service.profit if service.profit else 0.0)

            #     row +=1
            #     sheet.write(row, column, 'Group Total -Problem Type', bold)
            #     sheet.write(row, column+2, count, bold)
            # row +=1
            # sheet.write(row, column, 'Group Total', bold)
            # sheet.write(row, column+2, t_count, bold)

