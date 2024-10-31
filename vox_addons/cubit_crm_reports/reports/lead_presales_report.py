import base64
import io
from odoo import models, api
from datetime import datetime,timedelta
from operator import itemgetter
import re
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
class PresalesXlsx(models.AbstractModel):
    _name = 'report.cubit_crm_reports.report_presales_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self,workbook,data,complaints):

        user = self.env.user
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        company = self.env.user.company_id
        search_condition = []
        if data:
            start = datetime.combine(datetime.strptime(data['form'][0]['date_from'],'%Y-%m-%d'), datetime.min.time())
            end = datetime.combine(datetime.strptime(data['form'][0]['date_to'],'%Y-%m-%d'), datetime.max.time())
            search_condition =[('create_date','>=',start),
                                ('create_date','<=',end),]
                
            if data['form'][0]['stage_id']:
                search_condition.append(('stage_id','=',data['form'][0]['stage_id'][0]))    
            crm_leads = self.env['crm.lead'].search(search_condition)
            sheet = workbook.add_worksheet('Leads and Presales Report')
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
            sheet.merge_range('B2:L2', 'Leads and Presales Report', merge_format)
            # if company:
            #     logo = io.BytesIO(base64.b64decode(company.logo))
            #     sheet.insert_image(1, 0, "image.png", {'image_data': logo,'x_scale':0.125, 'y_scale':0.2,'border':None})

            sheet.merge_range('B3:D3', 'From Date', merge_format)
            sheet.merge_range('E3:L3', start.strftime('%d/%m/%Y'), merge_format)
            sheet.merge_range('B4:D4', 'To Date', merge_format)
            sheet.merge_range('E4:L4', end.strftime('%d/%m/%Y'), merge_format)
            if data['form'][0]['stage_id']:
                sheet.merge_range('B5:D5', 'Status', merge_format)
                sheet.merge_range('E5:L5', data['form'][0]['stage_id'][1], merge_format)
            row +=3
            sheet.write(row, column, '')
            row +=2
            sheet.write(row, column, 'Sl#', bold)
            sheet.write(row, column+1, 'Customer name', bold)
            sheet.set_column(column+2, column+2, 15)
            sheet.write(row, column+2, 'Contact Person', bold)
            sheet.set_column(column+3, column+3, 15)
            sheet.write(row, column+3, 'Sales Person', bold)
            sheet.set_column(column+4, column+4, 30)
            sheet.write(row, column+4, 'Probability of winning %', bold)
            sheet.set_column(column+5, column+5, 30)
            sheet.write(row, column+5, 'Expected Week of Closing', bold)
            sheet.set_column(column+6, column+6, 30)
            sheet.write(row, column+6, 'Expected Month of Closing', bold)
            sheet.set_column(column+7, column+7, 30)
            sheet.write(row, column+7, 'Expected Year of Closing', bold)
            sheet.set_column(column+8, column+8, 25)
            sheet.write(row, column+8, 'Opportunity Description', bold)
            sheet.set_column(column+9, column+9, 15)
            sheet.write(row, column+9, 'STATUS', bold)
            sheet.set_column(column+10, column+10, 15)
            sheet.write(row, column+10, 'Vendor', bold)
            sheet.set_column(column+11, column+11, 15)
            sheet.write(row, column+11, 'Distributor', bold)

            sheet.set_column(column+12, column+12, 15)
            sheet.write(row, column+12, 'Deal Locking', bold)
            sheet.set_column(column+13, column+13, 15)
            sheet.write(row, column+13, 'Deal ID', bold)
            
            sheet.set_column(column+14, column+14, 30)
            sheet.write(row, column+14, 'Vendor Account Manager', bold)
            sheet.set_column(column+15, column+15, 25)
            sheet.write(row, column+15, 'Pre Sales Team', bold)

            sheet.set_column(column+16, column+16, 25)
            sheet.write(row, column+16, 'Pre Sales Person', bold)
            sheet.set_column(column+17, column+17, 15)
            sheet.write(row, column+17, 'Category', bold)
            sheet.set_column(column+18, column+18, 15)
            sheet.write(row, column+18, 'Competitor', bold)

            
            if crm_leads:
                
                # row = row+1
                t_count = 1
                row = 8
                for service in crm_leads:

                    sheet.write(row, column, t_count)
                    sheet.write(row, column+1, service.partner_id.name if service.partner_id else '' )
                  #  sheet.write(row,column+2, i.create_date.strftime('%d/%m/%Y %H:%M:%S') if i.create_date else '')
                    sheet.write(row, column+2, service.contact_name if service.contact_name else '')
                    sheet.write(row, column+3, service.user_id.name if service.user_id else '')
                    sheet.write(row, column+4, service.sel_probability if service.sel_probability else '')
                    sheet.write(row, column+5, service.expected_week_of_closing if service.expected_week_of_closing else '')
                    sheet.write(row, column+6, service.expected_month_of_closing if service.expected_month_of_closing else '')
                    sheet.write(row, column+7, service.expected_year_of_closing if service.expected_year_of_closing else '')
                    sheet.write(row, column + 8, service.name if service.name else '')
                    sheet.write(row, column+9, service.stage_id.name if service.stage_id else '')
                    sheet.write(row, column + 17, service.category.name if service.category else '')
                    sheet.write(row, column + 18, service.competitor if service.competitor else '')
                    # row1 = row+1
                    # r = row1
                    row1 = row
                    r = row
                    if service.vendor_detail_id:
                        for vendor in service.vendor_detail_id:

                            # r = row1
                            # row1 +=1

                            sheet.write(row1, column+10, vendor.sale_line_brand.name if vendor.sale_line_brand.name else '')
                            sheet.write(row1, column+11, vendor.distributor.name if vendor.distributor else '' )
                            sheet.write(row1, column+12, vendor.dead_locking_status if vendor.dead_locking_status else '' )
                            sheet.write(row1, column+13, vendor.deal_id if vendor.deal_id else '')
                            sheet.write(row1, column+14, vendor.account_manager if vendor.account_manager else '')
                            row1 += 1

                    if service.presale_id:

                        # r = row2
                        for user in service.presale_id:

                            sheet.write(r, column+15, user.presale_department_id.name if user.presale_department_id.name else '')
                            sheet.write(r, column+16, user.presales_person.name if user.presales_person else '' )
                            r += 1
                    if row1 > r:
                        row = row1+1
                    else:
                        row = r + 1
                    r = row1
                    t_count += 1

                    # row += 1
                    # t_count += 1
                    # if row != row1 or row != r:
                    #     if row1 >= r:
                    #         row = row1
                    #     elif row1 < r:
                    #         row = r




            #     row +=1
            #     sheet.write(row, column, 'Group Total -Problem Type', bold)
            #     sheet.write(row, column+2, count, bold)
            # row +=1
            # sheet.write(row, column, 'Group Total', bold)
            # sheet.write(row, column+2, t_count, bold)

