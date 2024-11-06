from odoo import models,fields,api


class SaleExportOrderLine(models.AbstractModel):
    _name = 'report.vox_sale_fields.report_sale_order_line_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, complaints):
        sheet = workbook.add_worksheet('Order Line Export')
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter', })

        sale_order_line = self.env['sale.order.line'].search([('order_id', '=', data['id'])])
        sheet.merge_range('A1:P1', sale_order_line.order_id.name, merge_format)
        sheet.write(1, 0, 'Sl. No')
        sheet.write(1, 1, 'Part Number')
        sheet.write(1, 2, 'Description')
        sheet.write(1, 3, 'Quantity')
        sheet.write(1, 4, 'List Price')
        sheet.write(1, 5, 'Vendor Discount')
        sheet.write(1, 6, 'Currency Rate')
        sheet.write(1, 7, 'Tax')
        sheet.write(1, 8, 'Margin')
        sheet.write(1, 9, 'Unit Price')
        sheet.write(1, 10, 'Total Price')
        sheet.write(1, 11, 'Section')
        sheet.write(1, 12, 'Category')
        sheet.write(1, 13, 'Brand')
        sheet.write(1, 14, 'Technology')
        sheet.write(1, 15, 'Customer Discount')
        row = 2
        column = 0
        for line in sale_order_line:
            unit_price = "%.2f" % line.unit_price
            sheet.write(row, column, line.sl_no)
            sheet.write(row, column+1, line.part_number)
            #  sheet.write(row,column+2, i.create_date.strftime('%d/%m/%Y %H:%M:%S') if i.create_date else '')
            sheet.write(row, column + 2, line.name or '')
            sheet.write(row, column + 3, line.product_uom_qty or '')
            sheet.write(row, column + 4,  line.list_price or '')
            sheet.write(row, column + 5, line.supplier_discount or '')
            sheet.write(row, column + 6, line.currency_rate or '')
            sheet.write(row, column + 7, line.tax or '')
            sheet.write(row, column + 8, line.margin or '')
            sheet.write(row, column + 9, unit_price or '')
            sheet.write(row, column + 10, line.price_included or '')
            sheet.write(row, column + 11, line.sale_layout_cat_id and line.sale_layout_cat_id.name or '')
            sheet.write(row, column + 12, line.line_category_id and line.line_category_id.name or '')
            sheet.write(row, column + 13, line.line_brand_id and line.line_brand_id.name or '')
            sheet.write(row, column + 14, line.line_technology_id and line.line_technology_id.name or '')
            sheet.write(row, column + 15, line.customer_discount)
            row += 1

