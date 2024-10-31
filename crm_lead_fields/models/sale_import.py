# -*- coding: utf-8 -*-

import tempfile
import binascii
from odoo import models, fields, api,_,exceptions
from odoo.exceptions import ValidationError
import base64
import xlrd
import datetime
from datetime import datetime
import time

class SaleOrderImport(models.Model):
    _name = "sale.order.import"
    _description = "sale order import"



    partner_id = fields.Many2one('res.partner', 'Customer',domain="[('customer', '=', True)]")
    file_import = fields.Binary(string='Import',
            help="This is the file created by the anonymization process. It should have the '.pickle' extention.")
    # use_sections =fields.Boolean('Use Product Sections?')
    # use_contract = fields.Boolean('Is a Contract?')
    crm_lead_id = fields.Many2one('crm.lead', 'Opportunity ID')
    sale_order_id = fields.Many2one('sale.order', 'Sale ID')
    cubit_import_id = fields.Integer(string="Cubit ID")


    @api.model
    def _prepare_default_get(self, order):
        default = {
            'partner_id': order.partner_id.id,
            'crm_lead_id':order.id if self._context.get('active_model') == 'crm.lead' else False,
            'sale_order_id':order.id if self._context.get('active_model') == 'sale.order' else False
        }
        return default

    @api.model
    def default_get(self, fields):
        res = super(SaleOrderImport, self).default_get(fields)
        if self._context.get('active_model') == 'crm.lead':
        # assert self._context.get('active_model') == 'crm.lead', \
        #     'active_model should be crm.lead'
            order = self.env['crm.lead'].browse(self._context.get('active_id'))
            default = self._prepare_default_get(order)
            res.update(default)
        if self._context.get('active_model') == 'sale.order':
            order = self.env['sale.order'].browse(self._context.get('active_id'))
            default = self._prepare_default_get(order)
            res.update(default)
        return res


    def prepare_sale_requset(self,lines):


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
        if self._context.get('active_model', False) == 'sale.order':
            revison = True
            sale_value = self.env['sale.order'].browse(self._context.get('active_id', False))
            sale_id = sale_value.id
            list = []
            for sheet in workbook.sheets():
                for row in range(sheet.nrows):
                    if row >= 1:
                        line = sheet.row_values(row)
                        missing_fields = []
                        if not line[10]:
                            missing_fields.append(line[10])
                        if not line[11]:
                            missing_fields.append(line[11])
                        if not line[12]:
                            missing_fields.append(line[12])
                        if not line[13]:
                            missing_fields.append(line[13])
                        if not line[14]:
                            missing_fields.append(line[14])
                        if not line[15]:
                            missing_fields.append(line[15])
                        if not line[16]:
                            missing_fields.append(line[16])
                        if len(missing_fields) > 1:
                            raise ValidationError(_('Missing fields In the Excel file'))

                        technology = line[15]
                        brand = line[14]

                        if line[12] not in ['Renewal', 'Non Renewal', 'renewal', 'non renewal']:
                            raise ValidationError(
                                _('You cannot import File without Renewal Category Fill the column with either Renewal or Non Renewal'))
                        if line[12] == 'Renewal' or line[12] == 'renewal':
                            line[12] = 'renewal'
                        if line[12] == 'Non Renewal' or line[12] == 'non renewal':
                            line[12] = 'non_renewal'

                        section = line[10]
                        if not section:
                            raise ValidationError(_('You cannot import File without Section'))
                        category = line[11]
                        if not category:
                            raise ValidationError(_('You cannot import File without Category'))
                        if not line[12]:
                            raise ValidationError(_('You cannot import File without Renewal Category'))
                        if not line[13]:
                            raise ValidationError(_('You cannot import File without Service Duration Months'))
                        if not line[14]:
                            raise ValidationError(_('You cannot import File without Brand'))
                        if not line[15]:
                            raise ValidationError(_('You cannot import File without Technology'))
                        if not line[16]:
                            raise ValidationError(_('You cannot import File without Distributor'))

                        technology_ids = self.env['sale.line.technology'].search([('name', '=', technology)])
                        if not technology_ids:
                            raise ValidationError(_('Kindly Update the Technology'))

                        brand_ids = self.env['sale.line.brand'].search([('name', '=', brand)])
                        if not brand_ids:
                            raise ValidationError(_('Kindly Update the Brand'))
                        category_ids = self.env['sale.line.category'].search([('name', '=', category)])
                        if not category_ids:
                            raise ValidationError(_('Kindly Update the Category'))
                        section_id = False
                        if section:
                            section_ids = self.env['sale_layout.category'].search([('name', '=', section)])
                            if section_ids:
                                section_id = section_ids[0]
                            else:
                                section_id = self.env['sale_layout.category'].create({'name': section})
                        if line[2] != '':
                            if line[0]:
                                sequence = line[0]
                            else:
                                sequence = 10
                            serial_num = line[17]
                            service_suk = line[18]
                            begin_date = line[19]
                            end_date = line[20]
                            # DEFAULT_DATE_FORMAT = '%d-%m-%Y'
                            DEFAULT_DATE_FORMAT = '%d/%m/%Y'
                            if begin_date:
                                if type(begin_date) is float:
                                    date_obj = datetime.strptime(str(begin_date).split('.')[0], '%Y%m%d')
                                    # date_str = begin_date
                                    # date_obj = datetime.strptime(str(date_str), DEFAULT_DATE_FORMAT)
                                    begin_date = date_obj.date()
                                else:
                                    date_str = begin_date
                                    date_obj = datetime.strptime(str(date_str), DEFAULT_DATE_FORMAT)
                                    begin_date = date_obj.date()
                                    # begin_date.split('-')


                            else:
                                begin_date = False
                            if end_date:
                                if type(end_date) is float:
                                    date_obj = datetime.strptime(str(end_date).split('.')[0], '%Y%m%d')
                                    # date_str = end_date
                                    # date_obj = datetime.strptime(str(date_str), DEFAULT_DATE_FORMAT)
                                    end_date = date_obj.date()
                                else:
                                    date_str = end_date
                                    date_obj = datetime.strptime(str(date_str), DEFAULT_DATE_FORMAT)
                                    end_date = date_obj.date()
                                    # end_date.split('-')
                                # if type(end_date) is float:
                                #     end_date = datetime(*xlrd.xldate_as_tuple(end_date, 0))
                                # elif type(end_date) is unicode:
                                #     # end_date = datetime.strptime(end_date, '%d/%m/%Y')
                                #     end_date = datetime.strptime(end_date, import_date_format)
                            else:
                                end_date = False
                            line_defaults = {
                                'sequence': sequence,
                                'part_number': line[1],
                                'name': line[2],
                                'product_uom_qty': line[3],
                                'list_price': line[4],
                                'supplier_discount': line[5],
                                'currency_rate': line[6],
                                'tax': line[7],
                                'margin': line[8],
                                'options': line[9],
                                'service_duration': line[13],
                                'sale_layout_cat_id': section_id[0].id if section_id else False,
                                'line_technology_id': technology_ids[0].id if technology_ids else False,
                                'line_brand_id': brand_ids[0].id if brand_ids else False,
                                'line_category_id': category_ids[0].id if category_ids else False,
                                'begin_date': begin_date,
                                'end_date': end_date,
                                'presales_person': line[21],
                                'hs_code': line[22],
                                'country_of_origin': line[23],
                                'th_weight': line[24],
                                'order_id': sale_id,
                                'serial_num': serial_num,
                                'service_suk': service_suk,
                                'distributor': line[16],
                                'renewal_category': line[12]

                            }
                            # self.env['sale.order.line'].create(line_defaults)
                            list.append([0, 0, line_defaults])
                            sale_value.order_line = [(6, 0, [])]
                        sale_value.write({'order_line': list})
            # for obj in self.env['sale.order'].browse(self._context.get('active_id', False)):
            #     sale_value = self.env['sale.order'].browse(self._context.get('active_id', False))
            #     sale_id = sale_value.id
            #     list = []
            #

                # for line in lines[1:]:
                    # for line in lines:
                    # missing_fields = []
                    # if not line[10]:
                    #     missing_fields.append(line[10])
                    # if not line[11]:
                    #     missing_fields.append(line[11])
                    # if not line[12]:
                    #     missing_fields.append(line[12])
                    # if not line[13]:
                    #     missing_fields.append(line[13])
                    # if not line[14]:
                    #     missing_fields.append(line[14])
                    # if not line[15]:
                    #     missing_fields.append(line[15])
                    # if not line[16]:
                    #     missing_fields.append(line[16])
                    # if len(missing_fields) > 1:
                    #     raise ValidationError(_('Missing fields In the Excel file'))
                    #
                    # technology = line[15]
                    # brand = line[14]
                    #
                    # if line[12] not in ['Renewal', 'Non Renewal', 'renewal', 'non renewal']:
                    #     raise ValidationError(
                    #         _('You cannot import File without Renewal Category Fill the column with either Renewal or Non Renewal'))
                    # if line[12] == 'Renewal' or line[12] == 'renewal':
                    #     line[12] = 'renewal'
                    # if line[12] == 'Non Renewal' or line[12] == 'non renewal':
                    #     line[12] = 'non_renewal'
                    #
                    # section = line[10]
                    # if not section:
                    #     raise ValidationError(_('You cannot import File without Section'))
                    # category = line[11]
                    # if not category:
                    #     raise ValidationError(_('You cannot import File without Category'))
                    # if not line[12]:
                    #     raise ValidationError(_('You cannot import File without Renewal Category'))
                    # if not line[13]:
                    #     raise ValidationError(_('You cannot import File without Service Duration Months'))
                    # if not line[14]:
                    #     raise ValidationError(_('You cannot import File without Brand'))
                    # if not line[15]:
                    #     raise ValidationError(_('You cannot import File without Technology'))
                    # if not line[16]:
                    #     raise ValidationError(_('You cannot import File without Distributor'))
                    #
                    # technology_ids = self.env['sale.line.technology'].search([('name', '=', technology)])
                    # if not technology_ids:
                    #     raise ValidationError(_('Kindly Update the Technology'))
                    #
                    # brand_ids = self.env['sale.line.brand'].search([('name', '=', brand)])
                    # if not brand_ids:
                    #     raise ValidationError(_('Kindly Update the Brand'))
                    # category_ids = self.env['sale.line.category'].search([('name', '=', category)])
                    # if not category_ids:
                    #     raise ValidationError(_('Kindly Update the Category'))
                    # section_id = False
                    # if section:
                    #     section_ids = self.env['sale_layout.category'].search([('name', '=', section)])
                    #     if section_ids:
                    #         section_id = section_ids[0]
                    #     else:
                    #         section_id = self.env['sale_layout.category'].create({'name': section})
                    # if line[2] != '':
                    #     if line[0]:
                    #         sequence = line[0]
                    #     else:
                    #         sequence = 10
                    #     serial_num = line[17]
                    #     service_suk = line[18]
                    #     begin_date = line[19]
                    #     end_date = line[20]
                    #     # DEFAULT_DATE_FORMAT = '%d-%m-%Y'
                    #     DEFAULT_DATE_FORMAT = '%d/%m/%Y'
                    #     if begin_date:
                    #         if type(begin_date) is float:
                    #             date_obj = datetime.strptime(str(begin_date).split('.')[0], '%Y%m%d')
                    #             # date_str = begin_date
                    #             # date_obj = datetime.strptime(str(date_str), DEFAULT_DATE_FORMAT)
                    #             begin_date = date_obj.date()
                    #         else:
                    #             date_str = begin_date
                    #             date_obj = datetime.strptime(str(date_str), DEFAULT_DATE_FORMAT)
                    #             begin_date = date_obj.date()
                    #             # begin_date.split('-')
                    #
                    #
                    #     else:
                    #         begin_date = False
                    #     if end_date:
                    #         if type(end_date) is float:
                    #             date_obj = datetime.strptime(str(end_date).split('.')[0], '%Y%m%d')
                    #             # date_str = end_date
                    #             # date_obj = datetime.strptime(str(date_str), DEFAULT_DATE_FORMAT)
                    #             end_date = date_obj.date()
                    #         else:
                    #             date_str = end_date
                    #             date_obj = datetime.strptime(str(date_str), DEFAULT_DATE_FORMAT)
                    #             end_date = date_obj.date()
                    #             # end_date.split('-')
                    #         # if type(end_date) is float:
                    #         #     end_date = datetime(*xlrd.xldate_as_tuple(end_date, 0))
                    #         # elif type(end_date) is unicode:
                    #         #     # end_date = datetime.strptime(end_date, '%d/%m/%Y')
                    #         #     end_date = datetime.strptime(end_date, import_date_format)
                    #     else:
                    #         end_date = False
                    #     line_defaults = {
                    #         'sequence': sequence,
                    #         'part_number': line[1],
                    #         'name': line[2],
                    #         'product_uom_qty': line[3],
                    #         'list_price': line[4],
                    #         'supplier_discount': line[5],
                    #         'currency_rate': line[6],
                    #         'tax': line[7],
                    #         'margin': line[8],
                    #         'options': line[9],
                    #         'service_duration': line[13],
                    #         'sale_layout_cat_id': section_id[0].id if section_id else False,
                    #         'line_technology_id': technology_ids[0].id if technology_ids else False,
                    #         'line_brand_id': brand_ids[0].id if brand_ids else False,
                    #         'line_category_id': category_ids[0].id if category_ids else False,
                    #         'begin_date': begin_date,
                    #         'end_date': end_date,
                    #         'presales_person': line[21],
                    #         'hs_code': line[22],
                    #         'country_of_origin': line[23],
                    #         'th_weight': line[24],
                    #         'order_id': sale_id,
                    #         'serial_num': serial_num,
                    #         'service_suk': service_suk,
                    #         'distributor': line[16],
                    #         'renewal_category': line[12]
                    #
                    #     }
                    #
                    #     list.append([0, 0, line_defaults])
                    #     sale_value.order_line = [(6, 0, [])]
                    # sale_value.write({'order_line': list})

                value = {
                    'domain': str([('id', 'in', [sale_id])]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Quotation'),
                    'res_id': sale_id
                }

        else:
            for obj in self:

                so_vals = {
                    'partner_id': obj.partner_id.id,
                    'date_order': fields.datetime.now(),
                    'crm_lead_id': obj.crm_lead_id.id,
                    'vendor_detail_id': [(4, sale_ids.id) for sale_ids in obj.crm_lead_id.vendor_detail_id],
                    'presale_id':[(4,line.id) for line in obj.crm_lead_id.presale_id],
                    'trn_number': obj.partner_id.vat,
                }

                sale_value = self.env['sale.order'].create(so_vals)
                sale_id =sale_value.id
                for line in sale_value.vendor_detail_id:
                    line.update({'sale_order_id': sale_value.id,
                                 })



                # if revison:
                #     revision_values += [(4, sale_id)]
                #     self.pool.get('sale.order').write(cr, uid, context.get('active_id', False),
                #                                       {'name': new_name, 'revision_ids': revision_values})
                #     self.pool.get('sale.order').write(cr, uid, sale_id, {'name': name, 'revision': True})
                for line in lines[1:]:
                # for line in lines:
                    missing_fields = []
                    if not line[10]:
                        missing_fields.append(line[10])
                    if not line[11]:
                        missing_fields.append(line[11])
                    if not line[12]:
                        missing_fields.append(line[12])
                    if not line[13]:
                        missing_fields.append(line[13])
                    if not line[14]:
                        missing_fields.append(line[14])
                    if not line[15]:
                        missing_fields.append(line[15])
                    if not line[16]:
                        missing_fields.append(line[16])
                    if len(missing_fields)>1:
                        raise ValidationError(_('Missing fields In the Excel file'))

                    technology = line[15]
                    brand = line[14]

                    if line[12] not in ['Renewal','Non Renewal','renewal','non renewal']:
                        raise ValidationError(_('You cannot import File without Renewal Category Fill the column with either Renewal or Non Renewal'))
                    if line[12] == 'Renewal' or line[12] == 'renewal':
                        line[12] = 'renewal'
                    if line[12] == 'Non Renewal' or line[12] == 'non renewal':
                        line[12] = 'non_renewal'

                    section = line[10]
                    if not section:
                        raise ValidationError(_('You cannot import File without Section'))
                    category = line[11]
                    if not category:
                        raise ValidationError(_('You cannot import File without Category'))
                    if not line[12]:
                        raise ValidationError(_('You cannot import File without Renewal Category'))
                    if not line[13]:
                        raise ValidationError(_('You cannot import File without Service Duration Months'))
                    if not line[14]:
                        raise ValidationError(_('You cannot import File without Brand'))
                    if not line[15]:
                        raise ValidationError(_('You cannot import File without Technology'))
                    if not line[16]:
                        raise ValidationError(_('You cannot import File without Distributor'))


                    technology_ids = self.env['sale.line.technology'].search([('name', '=', technology)])
                    if not technology_ids:
                        raise ValidationError(_('Kindly Update the Technology'))

                    brand_ids = self.env['sale.line.brand'].search([('name', '=', brand)])
                    if not brand_ids:
                        raise ValidationError(_('Kindly Update the Brand'))
                    category_ids = self.env['sale.line.category'].search([('name', '=', category)])
                    if not category_ids:
                        raise ValidationError(_('Kindly Update the Category'))
                    section_id = False
                    if section:
                        section_ids = self.env['sale_layout.category'].search([('name', '=', section)])
                        if section_ids:
                            section_id = section_ids[0]
                        else:
                            section_id = self.env['sale_layout.category'].create({'name': section})
                    if line[2] != '':
                        if line[0]:
                            sequence = line[0]
                        else:
                            sequence = 10
                        serial_num = line[17]
                        service_suk = line[18]
                        begin_date = line[19]
                        end_date = line[20]
                        # DEFAULT_DATE_FORMAT = '%d-%m-%Y'
                        DEFAULT_DATE_FORMAT = '%d/%m/%Y'
                        if begin_date:
                            if type(begin_date) is float:
                                date_obj = datetime.strptime(str(begin_date).split('.')[0],'%Y%m%d')
                                # date_str = begin_date
                                # date_obj = datetime.strptime(str(date_str), DEFAULT_DATE_FORMAT)
                                begin_date = date_obj.date()
                            else:
                                date_str = begin_date
                                date_obj = datetime.strptime(str(date_str), DEFAULT_DATE_FORMAT)
                                begin_date = date_obj.date()
                                # begin_date.split('-')


                        else:
                            begin_date = False
                        if end_date:
                            if type(end_date) is float:
                                date_obj = datetime.strptime(str(end_date).split('.')[0],'%Y%m%d')
                                # date_str = end_date
                                # date_obj = datetime.strptime(str(date_str), DEFAULT_DATE_FORMAT)
                                end_date = date_obj.date()
                            else:
                                date_str = end_date
                                date_obj = datetime.strptime(str(date_str), DEFAULT_DATE_FORMAT)
                                end_date = date_obj.date()
                                # end_date.split('-')
                            # if type(end_date) is float:
                            #     end_date = datetime(*xlrd.xldate_as_tuple(end_date, 0))
                            # elif type(end_date) is unicode:
                            #     # end_date = datetime.strptime(end_date, '%d/%m/%Y')
                            #     end_date = datetime.strptime(end_date, import_date_format)
                        else:
                            end_date = False
                        line_defaults = {
                            'sequence': sequence,
                            'part_number': line[1],
                            'name': line[2],
                            'product_uom_qty': line[3],
                            'list_price': line[4],
                            'supplier_discount': line[5],
                            'currency_rate': line[6],
                            'tax': line[7],
                            'margin': line[8],
                            'options': line[9],
                            'service_duration': line[13],
                            'sale_layout_cat_id': section_id[0].id if section_id else False,
                            'line_technology_id': technology_ids[0].id if technology_ids else False,
                            'line_brand_id': brand_ids[0].id if brand_ids else False,
                            'line_category_id':  category_ids[0].id if category_ids else False,
                            'begin_date': begin_date,
                            'end_date': end_date,
                            'presales_person': line[21],
                            'hs_code': line[22],
                            'country_of_origin': line[23],
                            'th_weight': line[24],
                            'order_id': sale_id,
                            'serial_num': serial_num,
                            'service_suk': service_suk,
                            'distributor':line[16],
                            'renewal_category':line[12]

                        }
                        self.env['sale.order.line'].create(line_defaults)

                value = {
                    'domain': str([('id', 'in', [sale_id])]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Quotation'),
                    'res_id': sale_id
                }


        crm_lead = self.env['crm.lead'].browse(self.crm_lead_id.id)
        lead_stage_ids = self.env['crm.stage'].search([('is_import', '=', True)]).ids
        for lead in crm_lead:
            if lead_stage_ids:
                lead.stage_id = lead_stage_ids[0]
                lead.write({'stage_id' : lead_stage_ids[0],
                            'imported_stage':True

                            })
        return value
    #
    def make_sale_requset(self):
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

            if not line.partner_id:
                raise ValidationError(_('Choose The Customer Before Import the Quotation'))
            if not line.file_import:
                raise ValidationError("File Not Selected!")
            csv_data_lines = base64.b64decode(line.file_import)
            wb = xlrd.open_workbook(file_contents=csv_data_lines)
            #total number of sheets
            # res = wb.nsheets
            res = len(wb.sheet_names())
            if res>1:
                raise ValidationError(_('Your File has extra Excel Sheet please refer sample file'))

            sheet = wb.sheet_by_index(0)
            line = []
            for row_no in range(sheet.nrows):
                line = [k.value for k in sheet.row(row_no)]
            if len(line) > 25:
                raise ValidationError(_('Your File has extra column please refer sample file'))
            if len(line) < 25:
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