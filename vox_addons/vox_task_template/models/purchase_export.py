

import time
from datetime import date, datetime
import pytz
import json
import datetime
import io
from odoo import api, fields, models, _
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

from odoo import models
import string


class PayrollReport(models.AbstractModel):
    _name = 'report.vox_task_template.report_helpdesk_ticket_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        # print("lines", lines)
        format1 = workbook.add_format(
            {'font_size': 12, 'align': 'vcenter', 'bold': True, 'bg_color': '#d3dde3', 'color': 'black',
             'bottom': True, })
        format2 = workbook.add_format(
            {'font_size': 12, 'align': 'vcenter', 'bold': True, 'bg_color': '#edf4f7', 'color': 'black',
             'num_format': '#,##0.00'})
        format3 = workbook.add_format({'font_size': 11, 'align': 'center', 'bold': False, 'num_format': '#,##0.00'})
        format3_colored = workbook.add_format(
            {'font_size': 11, 'align': 'vcenter', 'bg_color': '#f7fcff', 'bold': False, 'num_format': '#,##0.00'})
        format4 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True})
        format5 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': False})

        used_structures = []

        sheet = workbook.add_worksheet('Purchase Order')
        cols = list(string.ascii_uppercase) + ['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK',
                                               'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV',
                                               'AW', 'AX', 'AY', 'AZ']
        rules = []
        col_no = 2
        print(lines, 'lines')
        sheet.merge_range('A1:E1', lines.name,format3)
        sheet.write('A2', "Part Number", format3)

        sheet.write('B2', 'Description', format3)
        sheet.write('C2', "Quantity", format3)

        sheet.write('D2', 'Unit Price', format3)

        # List report column headers:
        sheet.write('E2', 'Total Price', format3)


        x = 2
        e_name = 2
        has_payslips = False
        for order in lines.order_line:

            sheet.write(e_name, 0, order.part_number, format3)
            sheet.write(e_name, 1, order.name, format3)
            sheet.write(e_name, 2, order.product_qty, format3)
            sheet.write(e_name, 3, order.price_unit, format3)
            sheet.write(e_name, 4, order.price_subtotal, format3)

            x += 1
            e_name += 1
