import base64
import io
from odoo import models, api
from datetime import datetime, timedelta
from operator import itemgetter
import re
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class CiscoReportXlsx(models.AbstractModel):
    _name = 'report.cubit_crm_reports.report_cisco_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, complaints):

        user = self.env.user
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        search_condition = []
        company = self.env.user.company_id
        if data:
            start = datetime.combine(datetime.strptime(data['form'][0]['date_from'], '%Y-%m-%d'), datetime.min.time())
            end = datetime.combine(datetime.strptime(data['form'][0]['date_to'], '%Y-%m-%d'), datetime.max.time())
            search_condition = [('order_id.date_order', '>=', start),
                                ('order_id.date_order', '<=', end), ]
                
            sale_orders = self.env['sale.order.line'].search(search_condition)
            sheet = workbook.add_worksheet('Cisco Report')
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
            sheet.merge_range('B2:L2', 'Cisco Report', merge_format)
            # if company:
            #     logo = io.BytesIO(base64.b64decode(company.logo))
            #     sheet.insert_image(1, 0, "image.png", {'image_data': logo,'x_scale':0.125, 'y_scale':0.2,'border':None})

            sheet.merge_range('B3:D3', 'From Date', merge_format)
            sheet.merge_range('E3:L3', start.strftime('%d/%m/%Y'), merge_format)
            sheet.merge_range('B4:D4', 'To Date', merge_format)
            sheet.merge_range('E4:L4', end.strftime('%d/%m/%Y'), merge_format)
            row += 3
            sheet.write(row, column, '')
            row += 1
            sheet.write(row, column, 'SO #', bold)
            sheet.write(row, column + 1, 'SO Date ', bold)
            sheet.set_column(column + 2, column + 2, 15)
            sheet.write(row, column + 2, 'Customer Name', bold)
            sheet.set_column(column + 3, column + 3, 15)
            sheet.write(row, column + 3, 'SO REF', bold)
            sheet.set_column(column + 4, column + 4, 25)
            sheet.write(row, column + 4, 'Email Confirmation', bold)
            sheet.set_column(column + 5, column + 5, 25)
            sheet.write(row, column + 5, 'Cust. PO No.', bold)
            sheet.set_column(column + 6, column + 6, 15)
            sheet.write(row, column + 6, 'SO VALUE', bold)
            sheet.set_column(column + 7, column + 7, 35)
            sheet.write(row, column + 7, 'SO VALUE FOR CISCO', bold)
            sheet.set_column(column + 8, column + 8, 15)
            sheet.write(row, column + 8, 'VAT', bold)
            sheet.set_column(column + 9, column + 9, 40)
            sheet.write(row, column + 9, 'TOTAL SO VALUE INCLUDING VAT', bold)
            sheet.set_column(column + 10, column + 10, 35)
            sheet.write(row, column + 10, 'SO VALUE FOR CISCO', bold)
            sheet.set_column(column + 11, column + 11, 35)
            sheet.write(row, column + 11, 'Sales Person Name', bold)
            sheet.set_column(column + 12, column + 12, 25)
            sheet.write(row, column + 12, 'Supplier Name', bold)

            sheet.set_column(column + 13, column + 13, 15)
            sheet.write(row, column + 13, 'LPO No.', bold)
            sheet.set_column(column + 14, column + 14, 15)
            sheet.write(row, column + 14, 'LPO Date', bold)
            
            sheet.set_column(column + 15, column + 15, 15)
            sheet.write(row, column + 15, 'LPO Value', bold)
            sheet.set_column(column + 16, column + 16, 15)
            sheet.write(row, column + 16, 'VAT', bold)
            sheet.set_column(column + 17, column + 17, 15)
            sheet.write(row, column + 17, 'LPO No with VAT', bold)
            sheet.set_column(column + 18, column + 18, 15)
            sheet.write(row, column + 18, 'Brand', bold)
            sheet.set_column(column + 19, column + 19, 15)
            sheet.write(row, column + 19, 'TECHNOLOGY', bold)
            sheet.set_column(column + 20, column + 20, 15)
            sheet.write(row, column + 20, 'Category', bold)

            
            
            if sale_orders:
                
                
                # row = row+1
                t_count = 0
                for service in sale_orders:
                    if service.line_brand_id.name == "Cisco":
                        po_names= ""
                        numbers = []
                        po = self.env['purchase.order'].search([('name','ilike',service.order_id.po_number)])
                        for order in po:
                            for line in order.order_line:
                                if line.product_id == service.product_id:
                                    if order.name not in numbers:
                                        numbers.append(order.name)
                        if numbers:
                            po_names = ", ".join(numbers)            
                                
                        row += 1
                        t_count += 1
                        sheet.write(row, column, service.order_id.name if service.order_id.name else '')
                        sheet.write(row, column + 1, service.order_id.date_order.strftime('%d/%m/%Y') if service.order_id.date_order else '')
                      #  sheet.write(row,column+2, i.create_date.strftime('%d/%m/%Y %H:%M:%S') if i.create_date else '')
                        sheet.write(row, column + 2, service.order_id.partner_id.name if service.order_id.partner_id else '')
                        sheet.write(row, column + 3, service.order_id.client_order_ref if service.order_id.client_order_ref else '')
                        sheet.write(row, column + 4, "yes" if service.order_id.lpo_email else 'No')
                        
                        sheet.write(row, column + 5, po_names if po_names else '')
                        sheet.write(row, column + 6, service.order_id.amount_untaxed if service.order_id.amount_untaxed else '')
                        sheet.write(row, column + 7, service.price_total_val if service.price_total_val else '')
                        sheet.write(row, column + 8, service.order_id.amount_tax if service.order_id.amount_tax else '')
                        sheet.write(row, column + 9, service.order_id.amount_total if service.order_id.amount_total else '')
                        sheet.write(row, column + 10, service.price_included if service.price_included else '')
                        sheet.write(row, column + 11, service.order_id.user_id.name if service.order_id.user_id else '')


                        po = self.env['purchase.order'].search([('sale_id', '=', service.order_id.id)])
                        
                        # po = self.env['purchase.order'].search([('name', 'ilike', service.order_id.lpo_number)])
                        for rec in po:
                            sheet.write(row, column + 12, rec.partner_id.name if rec.partner_id else '')
                            sheet.write(row, column + 13, service.order_id.lpo_number if service.order_id.lpo_number else '')
                            sheet.write(row, column + 14, rec.create_date.strftime('%d/%m/%Y') if rec.create_date else '')
                            sheet.write(row, column + 15, rec.amount_total if rec.amount_total else 0.0)
                            tax = 0.0
                            for line in rec.order_line:
                                # tax += line.amount_tax1
                                tax += line.price_tax
                            sheet.write(row, column + 16, tax if tax else 0.0)
                            sheet.write(row, column + 17, "" )
                            sheet.write(row, column + 18, service.line_brand_id.name if service.line_brand_id else '')
                            sheet.write(row, column + 19, service.line_category_id.name if service.line_category_id else '')
                            sheet.write(row, column + 20, service.line_technology_id.name if service.line_technology_id else '')

                    # sheet.write(row, column + 18, po.expected_week_of_arrival if po.expected_week_of_arrival else '')
                    # sheet.write(row, column + 19, str(po.expected_month_of_arrival) + "/" + str(po.expected_year_of_arrival) if po.expected_month_of_arrival else '')
                    # sheet.write(row, column + 20, service.delivery_terms.name if service.delivery_terms else '')
                    # sheet.write(row, column + 21, dict(service._fields['invoice_status'].selection).get(service.invoice_status) if service.invoice_status else '')
                    # sheet.write(row, column + 22, service.invoice_ids[0].name if service.invoice_ids else '')
                    # sheet.write(row, column + 23, service.invoiced_amount if service.invoiced_amount else '')
                    # sheet.write(row, column + 24, service.amount_paid_invoice if service.amount_paid_invoice else '')
                    # sheet.write(row, column + 25, service.invoiced_amount - service.amount_paid_invoice or 0.0)
                    # sheet.write(row, column + 26, dict(service._fields['state'].selection).get(service.state) if service.state else '')
                    # sheet.write(row, column + 27, service.cubit_service_cost_price_total if service.cubit_service_cost_price_total else 0.0)
                    # sheet.write(row, column + 28, service.actual_cost_price_total if service.actual_cost_price_total else 0.0)
                    # sheet.write(row, column + 29, service.profit if service.profit else 0.0)

            #     row +=1
            #     sheet.write(row, column, 'Group Total -Problem Type', bold)
            #     sheet.write(row, column+2, count, bold)
            # row +=1
            # sheet.write(row, column, 'Group Total', bold)
            # sheet.write(row, column+2, t_count, bold)

