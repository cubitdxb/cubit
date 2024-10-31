# -*- coding: utf-8 -*-
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import MissingError
import io
import tempfile
import binascii
from odoo.exceptions import UserError, ValidationError
import logging
import os
import logging

import tempfile
import binascii
from odoo import models, fields, api, _, exceptions
from odoo.exceptions import ValidationError
import base64
import xlrd
import datetime
from datetime import datetime
import time

_logger = logging.getLogger(__name__)

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')


class LineImportWizard(models.TransientModel):
    _name = 'line.import.wizard'

    file_import = fields.Binary(string='Import',
                                help="This is the file created by the anonymization process. It should have the '.pickle' extention.")

    def download_example(self):
        active_model = self.env.context.get('active_model')

        if active_model == 'task.make.purchase':
            file_exam = 'line_purchase.xlsx'
        return {
            'type': 'ir.actions.act_url',
            'url': f'/vox_task_template/static/src/{file_exam}',
            'target': 'new',
        }

    def prepare_sale_requset(self, lines):

        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file_import))
            fp.seek(0)
            values = {}
            invoice_ids = []
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
        except Exception:
            raise exceptions.Warning(_("Please select an XLS file or You have selected invalid file"))

        value = {}
        if self._context.get('active_model', False) == 'task.make.purchase':
            revison = True
            task_make_purchase = self.env['task.make.purchase'].browse(self._context.get('active_id', False))
            quotations = task_make_purchase.mapped('line_ids')
            total_no_of_lines = len(quotations)
            sale_id = task_make_purchase.id

            # sale_order_id = task_make_purchase.task_id.sudo().sale_id.sudo()
            list = []
            sheet = workbook.sheet_by_index(0)
            for row in range(1, sheet.nrows):
            # for sheet in workbook.sheets():
            #     try:
            #     for row in range(sheet.nrows):
                if row >= 1:
                    line = sheet.row_values(row)
                    missing_fields = []
                    if not line[3]:
                        missing_fields.append(line[3])
                    if not line[4]:
                        missing_fields.append(line[4])
                    if not line[5]:
                        missing_fields.append(line[5])

                    if len(missing_fields) > 1:
                        raise ValidationError(_('Missing fields In the Excel file'))
                    if not line[3]:
                        raise ValidationError(_('You cannot import File without Name'))
                    # if not line[5]:
                    #     raise ValidationError(_('You cannot import File without QTY'))
                    # if not line[6]:
                    #     raise ValidationError(_('You cannot import File without Price'))
                    part_number = line[1]
                    section = line[2]
                    section_id = False
                    if section:
                        section_ids = self.env['sale_layout.category'].search([('name', '=', section)])
                        if section_ids:
                            section_id = section_ids[0]
                        else:
                            section_id = self.env['sale_layout.category'].create({'name': section})

                    vendor = self.env['res.partner'].search([('name', '=', line[3])], limit=1)

                    name = line[3]
                    product_uom_qty = line[4]
                    price = line[5]

                    total_no_of_lines += 1
                    line_defaults = {
                        # 'product_id': product_id and product_id.id or False,
                        'sale_layout_cat_id': section_id[0].id if section_id else False,
                        'vendor_id': False,
                        'name': name,
                        'sl_no': total_no_of_lines,
                        'product_qty': product_uom_qty,
                        'price_unit': price,
                        'part_number': part_number,
                        'purchase':True,
                        'sale_line_id': False,
                        # 'taxes_id': [(6, 0, line.tax_id.ids)],
                        'order_id': False,
                        # 'order_id': sale_order_id.id,
                        'import_purchase':True
                    }

                    list.append([0, 0, line_defaults])
                    # task_make_purchase.line_ids = [(6, 0, [])]
            task_make_purchase.write({'line_ids': list})
                # except Exception as e:
                #     print(str(e))

            value = {
                    # 'domain': str([('id', 'in', [sale_id])]),
                    'view_mode': 'form',
                    'target':'new',
                    'res_model': 'task.make.purchase',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Create Purchase'),
                    'res_id': sale_id
                }
        # return
        return value

    #
    def action_import(self):
        for line in self:
            try:
                fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                fp.write(binascii.a2b_base64(line.file_import))
                fp.seek(0)
                values = {}
                invoice_ids = []
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise exceptions.ValidationError(_("Please select an XLS file or You have selected invalid file"))

            # if not line.partner_id:
            #     raise ValidationError(_('Choose The Customer Before Import the Quotation'))
            if not line.file_import:
                raise ValidationError("File Not Selected!")
            csv_data_lines = base64.b64decode(line.file_import)
            wb = xlrd.open_workbook(file_contents=csv_data_lines)
            res = len(wb.sheet_names())
            if res > 1:
                raise ValidationError(_('Your File has extra Excel Sheet please refer sample file'))

            sheet = wb.sheet_by_index(0)
            line = []
            for row_no in range(sheet.nrows):
                line = [k.value for k in sheet.row(row_no)]
            if len(line) > 6:
                raise ValidationError(_('Your File has extra column please refer sample file'))
            if len(line) < 6:
                raise ValidationError(_('Not enough column please refer sample file'))
            lines = []
            for s in wb.sheets():
                for row in range(s.nrows):
                    data_row = []
                    for col in range(s.ncols):
                        value = (s.cell(row, col).value)
                        data_row.append(value)
                    lines.append(data_row)
            return self.prepare_sale_requset(lines)

