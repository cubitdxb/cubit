# -*- coding: utf-8 -*-
from odoo import fields,models,api,_
import datetime
from datetime import datetime,date
from odoo.tools import float_compare
import logging
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)


READONLY_STATES = {
    'confirmed': [('readonly', True)],
    'approved': [('readonly', True)],
    'done': [('readonly', True)]
}
class Uom(models.Model):

    _inherit = 'uom.uom'

    purchase_uom = fields.Boolean(string="Purchase Boolean")

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    cubit_id = fields.Integer(string="Cubit ID")
    state = fields.Selection(selection_add=[
        ("approved", "Purchase Confirmed"),
        ("except_invoice", "Invoice Exception"),
    ])

    add_uom = fields.Boolean('Add UOM')

    def compute_purchase_vendor_name(self):
        for order in self:
            move_values = self.env['account.move'].search(
                [('purchase_bill_id.name', '=', order.name), ('id', '=', 93735)])
            move_values_count = self.env['account.move'].search_count([('purchase_bill_id.name', '=', order.name)])
            for moves in move_values:
                order.invoice_ids = [(4, moves.id)]
            order.invoice_count = move_values_count



    def _get_sale_orders(self):
        res = super()._get_sale_orders() | self.sale_id if self.order_line.filtered(lambda f: f.import_purchase==True) else super()._get_sale_orders()
        return res
# return super(PurchaseOrder,self)._get_sale_orders() | self.order_line.move_dest_ids.group_id.sale_id | self.order_line.move_ids.move_dest_ids.group_id.sale_id

    def write(self, vals):
        precision_rounding = 0
        member_ids = []
        member_ids += self.env['crm.team'].search([('team_code', '=', 'procurement')]).mapped('member_ids').ids
        member_ids += self.env['crm.team'].search([('team_code', '=', 'procurement')]).mapped('leader_ids').ids
        _logger.info('members %s', member_ids)
        print(member_ids, 11111111111222222222222222222222)
        if self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id or self.env.uid in member_ids:
            res = super().write(vals)
            return res
        else:
            raise ValidationError(_("You can't edit, Please contact Administrator"))

        if vals.get('order_line') and self.state == 'purchase':
            for order in self:
                pre_order_line_qty = {order_line: order_line.product_qty for order_line in order.mapped('order_line')}

        if vals.get('order_line') and self.state == 'purchase':
            for order in self:
                to_log = {}
                for order_line in order.order_line:
                    if order_line.product_uom:

                        if pre_order_line_qty.get(order_line, False) and float_compare(pre_order_line_qty[order_line], order_line.product_qty, precision_rounding=order_line.product_uom.rounding) > 0:
                            to_log[order_line] = (order_line.product_qty, pre_order_line_qty[order_line])
                    else:
                        if pre_order_line_qty.get(order_line, False) and float_compare(pre_order_line_qty[order_line],
                                                                                       order_line.product_qty,
                                                                                       precision_rounding=2) > 0:
                            to_log[order_line] = (order_line.product_qty, pre_order_line_qty[order_line])
                if to_log:
                    order._log_decrease_ordered_quantity(to_log)
        return super(PurchaseOrder, self).write(vals)

    def import_lines(self):
        for obj in self:
            unlink_ids = [line.id for line in obj.delivery_ids]
            self.env['purchase.delivery.line'].search([('id', 'in', unlink_ids)]).unlink()
            for line in obj.order_line:
                for item in range(0, int(line.product_qty)):
                    vals = {
                        'purchase_order_line_id': line.id,
                        'name': line.name,
                        'part_number': line.part_number,
                        'purchase_id': obj.id,
                        'sale_layout_cat_id': line.sale_layout_cat_id and line.sale_layout_cat_id.id or False,
                        # 'price': line.sale_line_id.unit_price,
                        'price': line.price_unit,
                        'purchase_partner_id': line.order_id.partner_id.id,
                        'sale_order_id': line.sale_line_id.order_id.id,
                    }
                    self.env['purchase.delivery.line'].create(vals)
        return True

    def update_lines(self):
        deliv_line_obj = self.env['purchase.delivery.line']
        for obj in self:
            for deliv_line in obj.delivery_ids:
                if deliv_line.received:
                    deliv_line_ids = deliv_line_obj.search([('received', '=', False),('purchase_id', '=', deliv_line.purchase_id.id)])
                    for line in deliv_line_ids:
                        line.write({'received': True})
                if deliv_line.purchase_date:
                    deliv_line_ids = deliv_line_obj.search([
                        ('purchase_date', '=', False),
                        ('purchase_id', '=', deliv_line.purchase_id.id)
                    ])
                    for line in deliv_line_ids:
                        line.write({'purchase_date': deliv_line.purchase_date, 'received': True})
                if deliv_line.exp_date:
                    deliv_line_ids = deliv_line_obj.search([('exp_date', '=', False),('purchase_id', '=', deliv_line.purchase_id.id)])
                    for line in deliv_line_ids:
                        line.write({'exp_date': deliv_line.exp_date, 'received': True})
                '''if deliv_line.sale_layout_cat_id:
                    if deliv_line.purchase_date:
                        deliv_line_ids = deliv_line_obj.search(cr, uid, [
                            ('sale_layout_cat_id', '=', deliv_line.sale_layout_cat_id.id),
                            ('purchase_date', '=', False),
                            ('purchase_id', '=', deliv_line.purchase_id.id)
                        ])
                        deliv_line_obj.write(cr, uid, deliv_line_ids, {'purchase_date': deliv_line.purchase_date, 'received': True})
                    if deliv_line.exp_date:
                        deliv_line_ids = deliv_line_obj.search(cr, uid, [
                            ('sale_layout_cat_id', '=', deliv_line.sale_layout_cat_id.id),
                            ('exp_date', '=', False),
                            ('purchase_id', '=', deliv_line.purchase_id.id)
                        ])
                        deliv_line_obj.write(cr, uid, deliv_line_ids, {'exp_date': deliv_line.exp_date, 'received': True})
                elif deliv_line.purchase_order_line_id:
                    if deliv_line.purchase_date:
                        deliv_line_ids = deliv_line_obj.search(cr, uid, [
                            ('purchase_order_line_id', '=', deliv_line.purchase_order_line_id.id),
                            ('purchase_date', '=', False),
                            ('purchase_id', '=', deliv_line.purchase_id.id)
                        ])
                        deliv_line_obj.write(cr, uid, deliv_line_ids, {'purchase_date': deliv_line.purchase_date, 'received': True})
                    if deliv_line.exp_date:
                        deliv_line_ids = deliv_line_obj.search(cr, uid, [
                            ('purchase_order_line_id', '=', deliv_line.purchase_order_line_id.id),
                            ('exp_date', '=', False),
                            ('purchase_id', '=', deliv_line.purchase_id.id)
                        ])
                        deliv_line_obj.write(cr, uid, deliv_line_ids, {'exp_date': deliv_line.exp_date, 'received': True})'''
        return True

    def export_purchase(self):
        objects = []
        for obj in self:
            title = {
                0: "Part Number",
                1: "Description",
                2: "Quantity",
                3: "Unit Price",
                4: "Total Price",
            }
            for line in obj.order_line:
                vals = {
                    "0": line.part_number,
                    "1": line.name,
                    "2": line.product_qty,
                    "3": line.price_unit,
                    "4": line.price_subtotal,
                }
                objects.append(vals)
            datas = {
                # 'model': 'report.stock.list',
                'title': obj.name,
                'header': title,
                'sale': objects

            }

            return self.env.ref('vox_task_template.report_purchase_export_xls').report_action(self,data=datas)

    def _minimum_vendor_planned_date(self):
        res = {}
        for purchase in self:
            res[purchase.id] = False
            if purchase.order_line:
                min_date = purchase.order_line[0].deliv_followup_date
                for line in purchase.order_line:
                    if line.state == 'cancel':
                        continue
                    if line.deliv_followup_date and min_date:
                        if line.deliv_followup_date < min_date:
                            min_date = line.deliv_followup_date
                purchase.minimum_vendor_planned_date = min_date
        return res

    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    sale_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)
    task_id = fields.Many2one('project.task', 'Task')
    end_partner_id = fields.Many2one('res.partner', 'End Customer')
    delivery_ids = fields.One2many('purchase.delivery.line', 'purchase_id', 'Receipts')
    user_id = fields.Many2one('res.users', 'Responsible')
    discount_amount = fields.Float('Discount')

    # amount_word = fields.function(_amount_word, type='char', string='Amount word', multi=True)
    customer_id = fields.Many2one('res.partner', 'End Customer')
    show_end_customer = fields.Boolean('Print End Customer')
    quotation_validity = fields.Many2one('quotation.validity', 'Quotation Validity')
    tax_inclusive = fields.Char('Prices')
    add_tax = fields.Boolean('Add Tax',
                             help='By checking this boolean will add TAX automatically in all the line items')

    end_user_details = fields.Boolean(string="End user details required")
    terms_and_conditions=fields.Text(string="Terms and Condition",
                                     default="This LPO is system generated and does not require signature or stamp")
    additional_purchase = fields.Boolean(string="Additional Purchases")
    awaiting_eta = fields.Boolean(string="Awaiting ETA")
    is_professional_service = fields.Boolean(string="Is a Professional Service")
    prof_service_selling_price = fields.Char(string="Prof Service Selling Price")
    expected_time_of_arrival = fields.Date(string="Expected Time of Arrival")
    minimum_vendor_planned_date = fields.Date(compute='_minimum_vendor_planned_date', string='Vendor Date', readonly=False,store=True)
    # compute='_minimum_vendor_planned_date',inverse='_set_minimum_vendor_planned_date',
    #  help="This is computed as the minimum scheduled date of all purchase order lines' products.")

    sale_date_order = fields.Datetime(string='Sale Order Date', readonly=True)
    sale_delivery_date = fields.Date(string='Delivery Date', readonly=True)
    # project_sale_expiry_notify_id = fields.Many2one('project.sale.expiry.notifications', 'Sale Expires')

    vendor_followup_date = fields.Date('Vendor Follow-up', copy=False)
    end_user_name = fields.Char(string="Name")
    end_user_mail = fields.Char(string="Email")
    end_user_address = fields.Char(string="Address")
    end_user_mobile = fields.Char(string="Mobile")
    end_user_fax = fields.Char(string="FAX")
    end_user_website = fields.Char(string="Website")
    end_user_company = fields.Many2one('res.company',string="End user Company")
    end_user_company_value = fields.Char(string="Company")
    end_user_vat = fields.Char(string="VAT")

    dest_address_id = fields.Many2one('res.partner', 'Customer Address (Direct Delivery)')

    bid_date = fields.Date('Bid Received On', readonly=True, help="Date on which the bid was received")
    bid_validity = fields.Date('Bid Valid Until', help="Date on which the bid expired")

    location_id = fields.Many2one('stock.location', 'Destination', domain=[('usage', '<>', 'view')],
                                   states=READONLY_STATES)

    validator = fields.Many2one('res.users', 'Validated by', readonly=True, copy=False)

    shipped = fields.Boolean('Received', readonly=True, copy=False,
                              help="It indicates that a picking has been done")
    invoiced = fields.Boolean(string='Invoice Received',copy=False,
                                help="It indicates that an invoice has been validated")
    # compute = '_invoiced',
    invoice_method = fields.Selection([('manual', 'Based on Purchase Order lines'), ('order', 'Based on generated draft invoice'),
         ('picking', 'Based on incoming shipments'),("partial", "Partial Invoicing (percentage/fixed)")], 'Invoicing Control',
        readonly=True,
        help="Based on Purchase Order lines: place individual lines in 'Invoice Control / On Purchase Order lines' from where you can selectively create an invoice.\n" \
             "Based on generated invoice: create a draft invoice you can validate later.\n" \
             "Based on incoming shipments: let you create an invoice when receipts are validated."
        )
    # inverse = '_set_minimum_planned_date',
    minimum_planned_date = fields.Date(compute='_minimum_planned_date', string='Expected Date',readonly=False,store=True,
                                            help="This is computed as the minimum scheduled date of all purchase order lines' products.")

    @api.onchange('add_tax')
    def onchange_add_tax(self):
        tax = self.env['account.tax'].sudo().search([('sale_add_tax', '=', True), ('type_tax_use', '=', 'purchase')])
        for order in self:
            if order.add_tax == True:
                for line in order.order_line:
                    line.write({'taxes_id': [(4, t.id) for t in tax if t]})
            else:
                for line in order.order_line:
                    line.write({'taxes_id': False})

    @api.onchange('add_uom')
    def onchange_add_uom(self):
        purchse_uom_value = self.env['uom.uom'].search([('purchase_uom', '=', True)])
        uom_id = 0
        for i in purchse_uom_value:
            uom_id = i.id
        for order in self:
            if order.add_uom == True:
                for line in order.order_line:
                    line.write({'product_uom': uom_id})
            else:
                for line in order.order_line:
                    line.write({'product_uom': False})

    def _invoiced(self):
        res = {}
        for purchase in self:
            res[purchase.id] = all(line.invoiced for line in purchase.order_line if line.state != 'cancel')
        return res
    # def _set_minimum_planned_date(self, cr, uid, ids, name, value, arg, context=None):
    #     if not value: return False
    #     if type(ids)!=type([]):
    #         ids=[ids]
    #     pol_obj = self.env['purchase.order.line']
    #     for po in self:
    #         if po.order_line:
    #             pol_ids = pol_obj.search([
    #                 ('order_id', '=', po.id), '|', ('date_planned', '=', po.minimum_planned_date), ('date_planned', '<', value)
    #             ])
    #             pol_ids.write({'date_planned': value})
    #     return True

    def _minimum_planned_date(self):
        for purchase in self:
            if purchase.order_line:
                min_date=purchase.order_line[0].date_planned
                for line in purchase.order_line:
                    if line.state == 'cancel':
                        continue
                    if line.date_planned < min_date:
                        min_date=line.date_planned
                purchase.minimum_planned_date = min_date
        return

    def _get_year_selection(self):
        current_year = date.today()
        year = current_year.year
        extended_year = year + 10
        y = []
        for i in range(year, extended_year):
            y.append((str(i), str(i)))
        return y

    expected_year_of_arrival = fields.Selection(selection=_get_year_selection,string="Expected year of Arrival")
    expected_week_of_arrival = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4')],string="Expected week of Arrival")
    expected_month_of_arrival = fields.Selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
            ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December')],string="Expected Month of Arrival")
    payment_term = fields.Char(string="Payment Terms")


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    cubit_id = fields.Integer(string="Cubit ID")
    part_number = fields.Char('Part Number')
    sequence = fields.Integer('Sl No.')

    # sl_no = fields.Integer(compute = '_get_line_numbers',string='Sl No.')
    serial_num = fields.Char(string='Serial Number')
    service_suk = fields.Char(string='Service SUK')
    begin_date = fields.Date(string='Begin Date')
    end_date = fields.Date(string='End Date')
    sale_layout_cat_id = fields.Many2one('sale_layout.category',string='Section')
    # categ_sequence = fields.Integer(related='sale_layout_cat_id.sequence',string='Layout Sequence', store=True)

    #
    sale_line_id = fields.Many2one('sale.order.line', 'Sale Line')
    delivery_line_ids = fields.One2many('purchase.delivery.line', 'purchase_order_line_id', 'Receipt Lines')
    c_red = fields.Integer(compute='_determine_red', string='Red', store=True)
    c_orange = fields.Integer(compute='_determine_orange', string='Orange', store=True)
    c_blue = fields.Integer(compute='_determine_blue', string='Blue', store=True)
    virtual_delivered_qty = fields.Float(string='Actual Delivered Qty')
    # compute = '_calculate_delivered_qty',
    deliv_next_action = fields.Text('Delivery Next Action', copy=False)
    deliv_followup_date = fields.Date('Delivery Follow-up')
    price_subtotal_tax = fields.Float(string='Total')
    # compute = '_amount_line_tax_total',
    amount_tax1 = fields.Float(string='Tax')
    import_purchase = fields.Boolean('Import Purchase',default=False)

    # compute = '_amount_line_tax',

    _sql_constraints = [
        ('accountable_required_fields',
         'check(1=1)',
         "Missing required fields on accountable purchase order line."),

    ]

    # @api.depends('sequence', 'order_id')
    @api.depends('order_id')
    def _get_line_numbers(self):
        for order in self.mapped('order_id'):
            number = 1
            for line in order.order_line:
                line.sl_no = number
                number += 1

    sl_no = fields.Integer(compute='_get_line_numbers', string='Sl No.', readonly=False, default=False)

    def _determine_blue(self):
        for line in self:
            delivered_qty = line.virtual_delivered_qty
            product_qty = line.product_qty
            state = line.state
            if state not in ['draft', 'cancel'] and delivered_qty != 0.0 and delivered_qty < product_qty:
                line.c_blue = 1
            else:
                line.c_blue = 0
        return

    def _determine_orange(self):

        for line in self:
            delivered_qty = line.virtual_delivered_qty
            product_qty = line.product_qty
            state = line.state
            if state not in ['draft', 'cancel'] and delivered_qty == 0.0:
                line.c_orange = 1
            else:
                line.c_orange = 0
        return

    def _determine_red(self):
        for line in self:
            delivered_qty = line.virtual_delivered_qty
            product_qty = line.product_qty
            state = line.state
            if state not in ['draft', 'cancel'] and delivered_qty > product_qty:
                line.c_red = 1
            else:
                line.c_red = 0
        return


class PurchaseDeliveryLine(models.Model):
    _name = 'purchase.delivery.line'

    @api.onchange('sl_num', 'purchase_date', 'exp_date')
    def onchange_deliv(self):
        values = {'received': False}
        for order in self:
            if order.sl_num or order.purchase_date or order.exp_date:
                values.update({'received': True})
        return {'value': values}

    def _get_line_numbers(self):
        number = 1
        for order in self:
            order.sequence = number
            number += 1

    # @api.depends('purchase_id')
    # def _get_line_numbers(self):
    #     for order in self.mapped('purchase_id'):
    #         number = 1
    #         for line in order.order_line:
    #             line.sequence = number
    #             number += 1

    # def _get_line_numbers(self):
    #
    #     line_num = 1
    #     for line in self:
    #         # res[line.id] = line_num
    #         line_num += 1
    #     '''first_line_rec = self.browse(cr, uid, ids, context=context)[0]
    #     for line_rec in first_line_rec.order_id.order_line:
    #         res[line_rec.id] = line_num
    #         line_num += 1
    #     return res'''
    #     return

    sale_layout_cat_id = fields.Many2one('sale_layout.category',string='Section')
    sequence = fields.Integer(string='Sl No.',compute='_get_line_numbers')
    # 'sl_num': fields.char('Serial No'),
    exp_date_from = fields.Date(string="Expiry Date From")
    exp_date_to = fields.Date(string="Expiry Date To")
    purchase_date_from = fields.Date(string="Purchase Date From")
    purchase_date_to = fields.Date(string="Purchase Date To")
    purchase_partner_id = fields.Many2one('res.partner',string='Supplier', readonly=True,store=True)
    sale_order_id = fields.Many2one('sale.order',string='Sale Order', readonly=True, store=True)
    sale_partner_id = fields.Many2one('res.partner',string='Customer', readonly=True,store=True)
    received = fields.Boolean('Received')
    name = fields.Char('Product Description')
    part_number = fields.Char('Product Part Number')
    purchase_order_line_id = fields.Many2one('purchase.order.line', 'Purchase Order Line')
    type = fields.Selection([('warranty', 'Warranty'), ('guaranty', 'Guaranty')], 'Type',default='warranty')
    # sl_num = fields.Char('Product Code')
    sl_num = fields.Char(string='Serial No')
    exp_date = fields.Date('Expiry Date')
    purchase_date = fields.Date('Purchase Date')
    purchase_id = fields.Many2one('purchase.order', 'Line')
    comment = fields.Text('Note')
    cubit_id = fields.Integer(string="Cubit ID")
    price = fields.Float(string="Price")
    # task_id = fields.Many2one('project.task')



