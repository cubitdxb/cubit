import base64
import io
from odoo import models, api
from datetime import datetime,timedelta
from operator import itemgetter
import re
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
class ConsolidatedXlsx(models.AbstractModel):
    _name = 'report.cubit_crm_reports.report_consolidated_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self,workbook,data,complaints):

        user = self.env.user
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        search_condition = []
        company = self.env.user.company_id
        if data:
            start = datetime.combine(datetime.strptime(data['form'][0]['date_from'],'%Y-%m-%d'), datetime.min.time())
            end = datetime.combine(datetime.strptime(data['form'][0]['date_to'],'%Y-%m-%d'), datetime.max.time())
            search_condition =[('create_date','>=',start),
                                ('create_date','<=',end),]
                
            crm_leads = self.env['crm.lead'].search(search_condition)
            sheet = workbook.add_worksheet('Sales Consolidated Report')
            merge_format = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',})
            merge_format.set_font_size(16)
            bold = workbook.add_format({'bold':True})
            row = 1
            column = 0
            sheet.set_column(column, column, 15)
            sheet.set_column(column+2, column+2, 15)
            sheet.set_column(column+4, column+4, 15)
            sheet.set_column(column+6, column+6, 15)
            # if company:
            #     logo = io.BytesIO(base64.b64decode(company.logo))
            #     sheet.insert_image(1, 0, "image.png", {'image_data': logo, 'x_scale': 0.125, 'y_scale': 0.2, 'border': None})

            sheet.merge_range('B2:L2', 'Sales Consolidated Report', merge_format)
            sheet.merge_range('B3:D3', 'From Date', merge_format)
            sheet.merge_range('E3:L3', start.strftime('%d/%m/%Y'), merge_format)
            sheet.merge_range('B4:D4', 'To Date', merge_format)
            sheet.merge_range('E4:L4', end.strftime('%d/%m/%Y'), merge_format)
            row +=2
            sheet.write(row, column, '')
            row +=1
            sheet.write(row, column, 'Sales Person', bold)
            sheet.write(row, column+1, 'Sl#', bold)
            sheet.set_column(column+2, column+2, 15)
            sheet.write(row, column+2, 'Customer name', bold)
            sheet.set_column(column+3, column+3, 15)
            sheet.write(row, column+3, 'Contact Person', bold)
            sheet.set_column(column+4, column+4, 30)
            sheet.write(row, column+4, 'Probability of winning %', bold)
            sheet.set_column(column+5, column+5, 30)
            sheet.write(row, column+5, 'Opportunity Description', bold)
            sheet.set_column(column+6, column+6, 25)
            sheet.write(row, column+6, 'Category', bold)
            sheet.set_column(column+7, column+7, 25)
            sheet.write(row, column+7, 'Opportunity Value', bold)
            sheet.set_column(column+8, column+8, 20)
            sheet.write(row, column+8, 'Pre sales involved', bold)
            sheet.set_column(column+9, column+9, 25)
            sheet.write(row, column+9, 'Expected CLosing', bold)
            sheet.set_column(column+10, column+10, 30)
            sheet.write(row, column+10, 'Expected Week of closing', bold)
            sheet.set_column(column+11, column+11, 30)
            sheet.write(row, column+11, 'Expected Month of closing', bold)

            sheet.set_column(column+12, column+12, 30)
            sheet.write(row, column+12, 'Expected Year of closing', bold)
            sheet.set_column(column+13, column+13, 30)
            sheet.write(row, column+13, 'Status', bold)

            
            if crm_leads:
                
                # row = row+1
                t_count = 0
                for service in crm_leads:
                    row +=1
                    t_count += 1
                    sheet.write(row,column, service.user_id.name if service.user_id else '')
                    sheet.write(row,column+1, t_count)
                  #  sheet.write(row,column+2, i.create_date.strftime('%d/%m/%Y %H:%M:%S') if i.create_date else '')
                    sheet.write(row,column+2, service.partner_id.name if service.partner_id else '')
                    sheet.write(row,column+3, service.contact_name if service.contact_name else '')
                    sheet.write(row,column+4, service.sel_probability if service.sel_probability else '')
                    sheet.write(row,column+5, service.name if service.name else '')
                    sheet.write(row,column+6, service.category.name if service.category else '')
                    sheet.write(row,column+7, service.expected_revenue if service.expected_revenue else '')
                    sheet.write(row, column + 8, "Yes" if service.presales_required else 'No')
                    sheet.write(row,column+9, service.date_deadline.strftime('%d/%m/%Y') if service.date_deadline else '')
                    sheet.write(row, column + 10, service.expected_week_of_closing if service.expected_week_of_closing else '')
                    sheet.write(row,column+11, service.expected_month_of_closing if service.expected_month_of_closing else '')
                    sheet.write(row,column+12, service.expected_year_of_closing if service.expected_year_of_closing else '')
                    sheet.write(row,column+13, service.stage_id.name if service.stage_id else '')
            #     row +=1
            #     sheet.write(row, column, 'Group Total -Problem Type', bold)
            #     sheet.write(row, column+2, count, bold)
            # row +=1
            # sheet.write(row, column, 'Group Total', bold)
            # sheet.write(row, column+2, t_count, bold)

