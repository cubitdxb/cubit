from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import datetime


class CreatePurchase(models.TransientModel):
    _name = 'task.make.purchase'

    cubit_id = fields.Integer(string="Cubit ID")

    name = fields.Char("Name")
    dup_section_ids = fields.Many2many('sale_layout.category', 'task_make_purchase_dup_section_rel', \
                                       "wizard_id", "section_id", "Dup Sections")
    dup_vendors = fields.Many2many('res.partner', 'task_make_purchase_dup_vendors_rel', \
                                   "wizard_id", "vendor_id", "Dup Vendors")
    section_ids = fields.Many2many('sale_layout.category', 'task_make_purchase_section_rel', \
                                   "wizard_id", "section_id", "Sections")
    line_ids = fields.One2many('task.make.purchase.line', 'wizard_id', 'Items')
    partner_id = fields.Many2one('res.partner', 'Supplier')
    task_id = fields.Many2one('project.task', 'Task')
    select_all = fields.Boolean('Line Select All')
    section_select_all = fields.Boolean('Section Select All', default=True)
    section_unselect_all = fields.Boolean('Section UnSelect All', default=False)
    is_professional_service = fields.Boolean('Is a Professional Service', default=False)
    professional_service_sell_price = fields.Char('Prof Service Selling Price')

    def action_line_import(self):
        action = self.env.ref('vox_task_template.action_line_import_wizard').read()[0]
        action.update({'views': [[False, 'form']]})
        return action

    @api.onchange('section_ids')
    def item_delivered_ids_onchange(self):
        self.create_purchase()
        section = self.task_id.sudo().sale_id.sudo().order_line.sudo().sale_layout_cat_id.ids
        # section = self.line_ids.sale_layout_cat_id.ids

        return {'domain': {'section_ids': [('id', 'in', section)]}}

    @api.model
    def default_get(self, fields):
        result = super(CreatePurchase, self).default_get(fields)
        section_ids = []
        vendor_ids = []
        purchase_lines = []
        combined_sale_lines = []
        active_ids = self.env.context.get('active_id')
        active_ids = active_ids or False
        i = 1
        if self.env.context.get('active_id'):
            project_task = self.env['project.task'].browse(active_ids)
            for line in project_task.project_id.sale_id.order_line:
                if line.is_cubit_service == False:
                    if line.product_uom_qty > line.purchase_qty and line.exclude_purchase == False:
                        if line.sale_layout_cat_id and line.sale_layout_cat_id.id not in section_ids:
                            section_ids.append(line.sale_layout_cat_id.id)
                        if line.vendor_id and line.vendor_id.id not in vendor_ids:
                            vendor_ids.append(line.vendor_id.id)
                        price = (((line.list_price - (line.list_price * line.supplier_discount / 100)) + (
                                    line.list_price - (
                                        line.list_price * line.supplier_discount / 100)) * line.tax / 100) * line.currency_rate)

                        if self.section_ids:
                            if line.sale_layout_cat_id.id in self.section_ids.ids:
                                vals = {
                                    'product_id': line.product_id and line.product_id.id or False,
                                    'sale_layout_cat_id': line.sale_layout_cat_id and line.sale_layout_cat_id.id or False,
                                    'vendor_id': line.vendor_id and line.vendor_id.id or False,
                                    'name': line.name,
                                    'sl_no': i,
                                    'product_qty': line.product_uom_qty - line.purchase_qty,
                                    'price_unit': price,
                                    'part_number': line.part_number,
                                    'sale_line_id': line.id,
                                    # 'taxes_id': [(6, 0, line.tax_id.ids)],
                                    # 'order_id': line.order_id.id
                                }
                                i += 1
                                purchase_lines.append((0, 0, vals))
                                print(purchase_lines, 'purchase lines')
                                print(999999999999999999999999999999999999999999999)
                        else:
                            vals = {
                                'product_id': line.product_id and line.product_id.id or False,
                                'sale_layout_cat_id': line.sale_layout_cat_id and line.sale_layout_cat_id.id or False,
                                'vendor_id': line.vendor_id and line.vendor_id.id or False,
                                'name': line.name,
                                'sl_no': i,
                                'product_qty': line.product_uom_qty - line.purchase_qty,
                                'price_unit': price,
                                'part_number': line.part_number,
                                'sale_line_id': line.id,
                                # 'taxes_id': [(6, 0, line.tax_id.ids)],
                                # 'order_id': line.order_id.id
                            }
                            i += 1
                            purchase_lines.append((0, 0, vals))
                        # vals = {
                        #     'product_id': line.product_id and line.product_id.id or False,
                        #     'sale_layout_cat_id': line.sale_layout_cat_id and line.sale_layout_cat_id.id or False,
                        #     'vendor_id': line.vendor_id and line.vendor_id.id or False,
                        #     'name': line.name,
                        #     'sl_no': i,
                        #     'product_qty': line.product_uom_qty - line.purchased_qty,
                        #     'price_unit': price,
                        #     'part_number': line.part_number,
                        #     'sale_line_id': line.id,
                        # }
                        # i += 1
                        # purchase_lines.append((0, 0, vals))
                        print(1111111111111111111111111111111111111111111111111)
                        print(purchase_lines, 'purchase lines')
                        result['line_ids'] = purchase_lines
                    else:
                        result['line_ids'] = False

            for sale in project_task.combined_sale_ids:
                for line in sale.order_line:
                    if line.is_cubit_service == False:
                        if line.product_uom_qty > line.purchase_qty and line.exclude_purchase == False:
                            if line.sale_layout_cat_id and line.sale_layout_cat_id.id not in section_ids:
                                # print "ine.sale_layout_cat_id name and id", line.sale_layout_cat_id.name, line.sale_layout_cat_id.id
                                section_ids.append(line.sale_layout_cat_id.id)
                            if line.vendor_id and line.vendor_id.id not in vendor_ids:
                                vendor_ids.append(line.vendor_id.id)
                            price = (((line.list_price - (line.list_price * line.supplier_discount / 100)) + (
                                        line.list_price - (
                                            line.list_price * line.supplier_discount / 100)) * line.tax / 100) * line.currency_rate)
                            vals = {
                                'product_id': line.product_id and line.product_id.id or False,
                                'sale_layout_cat_id': line.sale_layout_cat_id and line.sale_layout_cat_id.id or False,
                                'vendor_id': line.vendor_id and line.vendor_id.id or False,
                                'name': line.name,
                                'sl_no': i,
                                'product_qty': line.product_uom_qty - line.purchase_qty,
                                'price_unit': price,
                                'part_number': line.part_number,
                                'sale_line_id': line.id,
                            }
                            i += 1
                            combined_sale_lines.append((0, 0, vals))
                        # print(combined_sale_lines, 'combined lines')
                    result['line_ids'] = combined_sale_lines
            t_m_pur = {}

            if len(section_ids) > 0 and section_ids[0] != False:
                t_m_pur = {'section_ids': [(6, 0, section_ids)],
                           'dup_section_ids': [(6, 0, section_ids)],
                           'dup_vendors': [(6, 0, vendor_ids)]}

            self.env['task.make.purchase'].write(t_m_pur)

            result['task_id'] = project_task.id
            # result['partner_id'] = task.partner_id.id
            # result['sale_number'] = task.sale_id.name
            # result['customer_ref'] = task.sale_id.client_order_ref
        print(result, 44444444444444)
        return result


    def create_purchase(self):

        section_ids = []
        vendor_ids = []
        purchase_lines = []
        combined_sale_lines = []
        i = 1
        self.line_ids = False
        for wizard in self:

            if self.task_id:
                project_task = self.env['project.task'].browse(self.task_id.id)
                for line in project_task.project_id.sale_id.order_line:
                    if line.is_cubit_service == False:
                        if line.product_uom_qty > line.purchase_qty and line.exclude_purchase == False:
                            if line.sale_layout_cat_id and line.sale_layout_cat_id.id not in section_ids:
                                section_ids.append(line.sale_layout_cat_id.id)
                            if line.vendor_id and line.vendor_id.id not in vendor_ids:
                                vendor_ids.append(line.vendor_id.id)
                            price = (((line.list_price - (line.list_price * line.supplier_discount / 100)) + (
                                    line.list_price - (
                                    line.list_price * line.supplier_discount / 100)) * line.tax / 100) * line.currency_rate)
                            if self.section_ids:
                                if line.sale_layout_cat_id.id in self.section_ids.ids:
                                    vals = {
                                        'product_id': line.product_id and line.product_id.id or False,
                                        'sale_layout_cat_id': line.sale_layout_cat_id and line.sale_layout_cat_id.id or False,
                                        'vendor_id': line.vendor_id and line.vendor_id.id or False,
                                        'name': line.name,
                                        'sl_no': i,
                                        'product_qty': line.product_uom_qty - line.purchase_qty,
                                        'price_unit': price,
                                        'part_number': line.part_number,
                                        'sale_line_id': line.id,
                                        'taxes_id': [(6, 0, line.tax_id.ids)],
                                        'order_id': line.order_id.id
                                    }
                                    i += 1
                                    purchase_lines.append((0, 0, vals))
                            else:
                                vals = {
                                    'product_id': line.product_id and line.product_id.id or False,
                                    'sale_layout_cat_id': line.sale_layout_cat_id and line.sale_layout_cat_id.id or False,
                                    'vendor_id': line.vendor_id and line.vendor_id.id or False,
                                    'name': line.name,
                                    'sl_no': i,
                                    'product_qty': line.product_uom_qty - line.purchase_qty,
                                    'price_unit': price,
                                    'part_number': line.part_number,
                                    'sale_line_id': line.id,
                                    'taxes_id': [(6, 0, line.tax_id.ids)],
                                    'order_id':line.order_id.id
                                }
                                i += 1
                                purchase_lines.append((0, 0, vals))
                wizard.line_ids = purchase_lines

            for sale in project_task.combined_sale_ids:
                for line in sale.order_line:
                    if line.is_cubit_service == False:
                        if line.product_uom_qty > line.purchase_qty and line.exclude_purchase == False:
                            if line.sale_layout_cat_id and line.sale_layout_cat_id.id not in section_ids:
                                # print "ine.sale_layout_cat_id name and id", line.sale_layout_cat_id.name, line.sale_layout_cat_id.id
                                section_ids.append(line.sale_layout_cat_id.id)
                            if line.vendor_id and line.vendor_id.id not in vendor_ids:
                                vendor_ids.append(line.vendor_id.id)
                            price = (((line.list_price - (line.list_price * line.supplier_discount / 100)) + (
                                    line.list_price - (
                                    line.list_price * line.supplier_discount / 100)) * line.tax / 100) * line.currency_rate)
                            vals = {
                                'product_id': line.product_id and line.product_id.id or False,
                                'sale_layout_cat_id': line.sale_layout_cat_id and line.sale_layout_cat_id.id or False,
                                'vendor_id': line.vendor_id and line.vendor_id.id or False,
                                'name': line.name,
                                'sl_no': i,
                                'product_qty': line.product_uom_qty - line.purchase_qty,
                                'price_unit': price,
                                'part_number': line.part_number,
                                'sale_line_id': line.id,
                                'taxes_id': [(6, 0, line.tax_id.ids)],
                            }
                            i += 1
                            combined_sale_lines.append((0, 0, vals))
                wizard.line_ids = combined_sale_lines
        return
        #     t_m_pur = {}
        #
        #     if len(section_ids) > 0 and section_ids[0] != False:
        #         t_m_pur = {'section_ids': [(6, 0, section_ids)],
        #                    'dup_section_ids': [(6, 0, section_ids)],
        #                    'dup_vendors': [(6, 0, vendor_ids)]}
        #
        #     self.env['task.make.purchase'].write(t_m_pur)
        #
        #     result['task_id'] = project_task.id
        #     # result['partner_id'] = task.partner_id.id
        #     # result['sale_number'] = task.sale_id.name
        #     # result['customer_ref'] = task.sale_id.client_order_ref
        # return result

    @api.onchange('partner_id', 'section_select_all')
    def onchange_vendor(self):
        lines = [(5,)]
        self.create_purchase()
        for obj in self:
            # print(obj, 'object')
            # data = {}

            for line in obj.line_ids:
                # print(line, 'lines')
                data = {
                    'wizard_id': obj.id,
                    'product_id': line.product_id and line.product_id.id or False,
                    'sl_no': line.sl_no,
                    'part_number': line.part_number,
                    'sale_layout_cat_id': line.sale_layout_cat_id and line.sale_layout_cat_id.id or False,
                    'vendor_id': line.vendor_id and line.vendor_id.id or False,
                    'name': line.name,
                    'product_qty': line.product_qty,
                    'price_unit': line.price_unit,
                    'sale_line_id': line.sale_line_id and line.sale_line_id.id or False,
                    'order_id': line.order_id and line.order_id.id or False,
                }
                if obj.section_select_all:
                    data.update({'purchase': True})
                else:
                    data.update({'purchase': False})
                lines.append((0, 0, data))
            # value = {
            #     'line_ids': lines
            # }
            obj.line_ids = lines

        # res = {'value': value}
        return

    @api.onchange('select_all','dup_vendors')
    def onchange_select_all(self, ):

        lines = [(5,)]
        # sect_ids = section_ids[0][2]
        self.create_purchase()
        for obj in self:
            sect_ids = obj.section_ids

            for line in obj.line_ids:
                data = {
                    'wizard_id': obj.id,
                    'product_id': line.product_id and line.product_id.id or False,
                    'sl_no': line.sl_no,
                    'part_number': line.part_number,
                    'sale_layout_cat_id': line.sale_layout_cat_id and line.sale_layout_cat_id.id or False,
                    'vendor_id': line.vendor_id and line.vendor_id.id or False,
                    'name': line.name,
                    'product_qty': line.product_qty,
                    'price_unit': line.price_unit,
                    'sale_line_id': line.sale_line_id and line.sale_line_id.id or False,
                    'order_id': line.order_id and line.order_id.id or False,
                }
                if obj.select_all:
                    data.update({'purchase': True})
                else:
                    data.update({'purchase': False})
                lines.append((0, 0, data))
            obj.line_ids = lines
        return

    @api.onchange('section_ids')
    def onchange_section_ids(self):

        lines = [(5,)]
        self.create_purchase()

        for obj in self:
            sect_ids = False
            if obj.section_ids:
                if obj._origin.section_ids:
                    sect_ids = obj._origin.section_ids.ids
                else:
                    sect_ids = obj.section_ids.ids

            if sect_ids:

                for line in obj.line_ids:
                    if line.sale_layout_cat_id.id in sect_ids:
                        data = {
                            'wizard_id': obj.id,
                            'product_id': line.product_id and line.product_id.id or False,
                            'sl_no': line.sl_no,
                            'part_number': line.part_number,
                            'sale_layout_cat_id': line.sale_layout_cat_id if line.sale_layout_cat_id else False,
                            'vendor_id': line.vendor_id and line.vendor_id.id or False,
                            'name': line.name,
                            'product_qty': line.product_qty,
                            'price_unit': line.price_unit,
                            'sale_line_id': line.sale_line_id and line.sale_line_id.id or False,
                            'order_id': line.order_id and line.order_id.id or False,
                        }
                        lines.append((0, 0, data))
                obj.line_ids = lines
            return

    def make_purchase_requset(self):
        for obj in self:
            purchase_order_line = self.env['purchase.order.line']
            active_id = obj.task_id.id
            purchase_vals = self._prepare_purchase_order(active_id, obj, obj.partner_id)
            if obj.task_id.project_id:
                if obj.task_id.project_id.partner_id:
                    purchase_vals.update({'end_partner_id': obj.task_id.project_id.partner_id.id})
            _skip = False
            purchase_id = False
            for line in obj.line_ids:
                if line.purchase:
                    _skip = True
                    break
            if _skip:
                purchase_id = self.env['purchase.order'].create(purchase_vals)
            for line in obj.line_ids:
                if line.purchase:
                    purchase_line_vals = self._prepare_purchase_order_line(line, purchase_id, obj.partner_id)
                    purchase_line_id = purchase_order_line.create(purchase_line_vals)
        return {'type': 'ir.actions.act_window_close'}

    #
    def _get_picking_in(self):
        obj_data = self.env['ir.model.data']
        type_obj = self.env['stock.picking.type']
        user_obj = self.env.user
        company_id = user_obj.company_id.id
        types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
            if not types:
                ValidationError(_('Make sure you have at least an incoming picking type defined'))
        return types[0]

    #
    def _prepare_purchase_order(self, active_id, wizard, supplier):
        # supplier_pricelist = supplier.property_product_pricelist_purchase
        # supplier_pricelist = supplier.property_product_pricelist
        picking_type_id = self._get_picking_in()
        user = self.env.user
        if picking_type_id:
            picking_type_id = picking_type_id.id
        picking_type_obj = self.env['stock.picking.type'].browse(picking_type_id)
        task_id = self.env['project.task'].browse(active_id)
        sale_order = self.env['sale.order'].browse(task_id.project_id.sale_id.id)
        return {
            'date_order': fields.datetime.now(),
            'partner_id': supplier.id,
            'project_id': task_id.project_id.id,
            'sale_id': task_id.project_id.sale_id.id,
            'company_id': user.company_id.id,
            'task_id': active_id,
            'end_user_name': sale_order.end_user_name,
            'end_user_mail': sale_order.end_user_mail,
            'end_user_address': sale_order.end_user_address,
            'end_user_mobile': sale_order.end_user_mobile,
            'end_user_fax': sale_order.end_user_fax,
            'end_user_website': sale_order.end_user_website,
            'end_user_company_value': sale_order.end_user_company_value,
            'end_user_vat': sale_order.end_user_vat,
            'add_tax': False
        }

    def _prepare_purchase_order_line(self, requisition_line, purchase_id, supplier):
        po_line_obj = self.env['purchase.order.line']
        requisition_line1 = requisition_line.sale_line_id
        price = (((requisition_line1.list_price - (
                requisition_line1.list_price * requisition_line1.supplier_discount / 100)) + (
                          requisition_line1.list_price - (
                          requisition_line1.list_price * requisition_line1.supplier_discount / 100)) * requisition_line1.tax / 100) * requisition_line1.currency_rate)
        sale_line = self.env['sale.order.line'].browse(requisition_line.sale_line_id.id)
        purchse_uom_value  = self.env['uom.uom'].search([('purchase_uom','=',True)])
        uom_id = 0
        for i in purchse_uom_value:
            uom_id = i.id

        vals = {
            'sequence': requisition_line.sl_no,
            'name': requisition_line.name,
            'product_id': requisition_line.product_id and requisition_line.product_id.id or False,
            'product_qty': requisition_line.product_qty,
            'price_unit': requisition_line.price_unit,
            'part_number': requisition_line.part_number,
            'order_id': purchase_id.id if purchase_id else False,
            'date_planned': fields.datetime.now(),
            'deliv_followup_date': fields.datetime.now(),
            'sale_line_id': requisition_line.sale_line_id.id,
            'serial_num': sale_line.serial_num,
            'service_suk': sale_line.service_suk,
            'begin_date': sale_line.begin_date,
            'end_date': sale_line.end_date,
            # 'taxes_id': [(6, 0, sale_line.tax_id.ids)],
            'sale_layout_cat_id':sale_line.sale_layout_cat_id and sale_line.sale_layout_cat_id.id or False,
            'product_uom':uom_id if uom_id else False,
            # 'order_id': requisition_line.order_id.id
            'import_purchase':requisition_line.import_purchase

        }

        purchased_qty = sale_line.purchased_qty
        new_qty = purchased_qty + requisition_line.product_qty
        requisition_line.sale_line_id.write({'purchased_qty': purchased_qty + requisition_line.product_qty})
        return vals


class MakePurchaseOrderLines(models.TransientModel):
    _name = 'task.make.purchase.line'
    _description = "Make purchase Request Line"

    wizard_id = fields.Many2one('task.make.purchase', 'Wizard')
    product_id = fields.Many2one('product.product', 'Product')
    sl_no = fields.Integer('Sl No')
    part_number = fields.Char('Part Number')
    name = fields.Char('Name')
    product_qty = fields.Float('Quantity')
    price_unit = fields.Float('Price')
    sale_line_id = fields.Many2one('sale.order.line', 'Sale Line')
    order_id = fields.Many2one('sale.order', string='Order Reference')
    sale_layout_cat_id = fields.Many2one('sale_layout.category', 'Section')
    purchase = fields.Boolean('Purchase')
    import_purchase = fields.Boolean('Import Purchase',default=False)
    vendor_id = fields.Many2one('res.partner', 'Vendor', domain="[('supplier', '=', True)]")
    taxes_id = fields.Many2many('account.tax', string='Taxes',domain=['|', ('active', '=', False), ('active', '=', True)])

