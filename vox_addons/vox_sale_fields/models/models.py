# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from collections import defaultdict, Counter
import datetime
from datetime import datetime
from lxml import etree
import simplejson  # If not installed, you have to install it by executing pip install simplejson


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('name', 'state', 'order_line', 'invoice_ids', 'invoice_ids.amount_total')
    def _invoiced_amount(self):
        res = {}
        for sale in self:
            tot = 0.0
            for invoice in sale.invoice_ids:
                if invoice.state not in ('draft', 'cancel'):
                    tot += invoice.amount_total
            sale.bill_invoiced_amount = tot

    bill_invoiced_amount = fields.Float(compute='_invoiced_amount', string='Invoiced Amount', store=True)

    @api.depends('name', 'state', 'order_line', 'invoice_ids', 'order_line.order_id',
                 'project_id.tasks.purchase_ids.sale_id', )
    def _get_so_ref_number(self):
        res = {}
        for order in self:
            sale_order_ids = order.project_id.sudo().tasks.sudo().purchase_ids.sudo().sale_id.sudo().ids
            # sale_order_ids = order.project_id.tasks.purchase_ids.sale_id.ids
            po_obj_ids = self.env['sale.order'].search([('id', 'in', sale_order_ids)])
            for po in po_obj_ids:
                if order.so_number:
                    if po:
                        order.so_number = order.so_number + ', ' + po.name
                    else:
                        order.so_number = order.so_number
                else:
                    order.so_number = po.name
            if order.so_number:
                so_numbers = list(set([l.strip() for l in (order.so_number.split(','))]))
                # so_numbers = list(set(order.so_number.split(',')))
                join_so_number = ', '.join(so_numbers)
                order.so_number = join_so_number




    @api.depends('name', 'state', 'order_line', 'invoice_ids', 'invoice_ids.amount_residual')
    def _get_bill_amount_balance_due(self):
        res = {}
        for order in self:
            val = 0.0
            for line in order.invoice_ids:
                if line.state not in ('draft', 'cancel'):
                    val += line.amount_residual
            order.amount_bill_balance = val

    @api.depends('name', 'state', 'order_line', 'invoice_ids', 'invoice_ids.amount_paid')
    def _get_bill_amount_paid(self):
        res = {}
        for order in self:
            val = 0.0
            for line in order.invoice_ids:
                if line.state not in ('draft', 'cancel'):
                    val += line.amount_paid
            order.amount_paid_bill = val

    so_number = fields.Char(compute="_get_so_ref_number", string="SO Number", store=True)
    amount_paid_bill = fields.Float(compute='_get_bill_amount_paid', string='Paid Amount', store=True)
    amount_bill_balance = fields.Float(compute='_get_bill_amount_balance_due', string='Balance amount', store=True)



class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):

        res = super(SaleOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                     submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'form':
            if not self.env.user.has_group('vox_task_template.group_sale_order_edit'):

                for node in doc.xpath("//field"):
                    if node.get('name') == 'sale_note' or node.get('name')=='client_order_ref' or node.get('name')=='lpo_email' or node.get('name') == 'lpo_email_attachment'\
                            or node.get('name')=='quotation_validity' or node.get('name')=='delivery_terms' or node.get('name')=='tax_inclusive'\
                            or node.get('name')=='user_id' or node.get('name')=='team_id' or node.get('name')=='tag_ids' or node.get('name')=='commitment_date'\
                            or node.get('name')=='fiscal_position_id' or node.get('name')=='origin' or node.get('name')=='campaign_id' or node.get('name')=='medium_id'\
                            or node.get('name')=='source_id' or node.get('name')=='signed_by' or node.get('name')=='signed_on' or node.get('name')=='order_line'\
                            or node.get('name')=='signed_by' or node.get('name')=='introduction_letter_date' or node.get('name')=='terms_and_condition_index'\
                            or node.get('name')=='vendor_detail_id' or node.get('name')=='revision_ids':
                        modifiers = simplejson.loads(node.get("modifiers"))
                        if 'readonly' not in modifiers:
                            modifiers['readonly'] = [['state', 'in', ('sale','done')]]
                            # modifiers['groups'] != [[]]
                        else:
                            if type(modifiers['readonly']) != bool:
                                modifiers['readonly'].insert(0, '|')
                                modifiers['readonly'] += [['state', 'in', ('sale','done')]]
                        node.set('modifiers', simplejson.dumps(modifiers))
                for node in doc.xpath("//field[@name='order_line']"):
                    if node.get('name') == 'sl_no' or node.get('name')=='part_number' or node.get('name')=='name' or node.get('name') == 'unit_price'\
                            or node.get('name')=='product_uom_qty' or node.get('name')=='qty_delivered' or node.get('name')=='qty_invoiced'\
                            or node.get('name')=='round_discount' or node.get('name')=='price_included' or node.get('name')=='tax_total' or node.get('name')=='price_total_val'\
                            or node.get('name')=='list_price' or node.get('name')=='currency_rate' or node.get('name')=='supplier_discount' or node.get('name')=='tax'\
                            or node.get('name')=='margin' or node.get('name')=='customer_discount' or node.get('name')=='cost_price' or node.get('name')=='total_cost'\
                            or node.get('name')=='purchased_qty' or node.get('name')=='actual_cost_price' or node.get('name')=='virtual_delivered_qty'\
                            or node.get('name')=='virtual_purchased_qty' or node.get('name')=='purchase_price' or node.get('name')=='vendor_id' or node.get('name')=='sale_layout_cat_id' or node.get('name')=='line_category_id'\
                            or node.get('name')=='line_brand_id' or node.get('name')=='line_technology_id' or node.get('name')=='c_red' or node.get('name')=='c_orange'\
                            or node.get('name')=='c_blue' or node.get('name')=='remarks' or node.get('name')=='is_cubit_service' or node.get('name')=='serial_num'\
                            or node.get('name')=='service_suk' or node.get('name')=='begin_date' or node.get('name')=='end_date' or node.get('name')=='exclude_purchase'\
                            or node.get('name')=='exclude_costprice' or node.get('name')=='th_weight' or node.get('name')=='option'\
                            or node.get('name')=='renewal_category' or node.get('name')=='service_duration' or node.get('name')=='month' or node.get('name')=='distributor'\
                            or node.get('name')=='presales_person' or node.get('name')=='hs_code' or node.get('name')=='country_of_origin' :
                        modifiers = simplejson.loads(node.get("modifiers"))
                        if 'readonly' not in modifiers:
                            modifiers['readonly'] = [['state', 'in', ('sale','done')]]
                            # modifiers['groups'] != [[]]
                        else:
                            if type(modifiers['readonly']) != bool:
                                modifiers['readonly'].insert(0, '|')
                                modifiers['readonly'] += [['state', 'in', ('sale','done')]]
                        node.set('modifiers', simplejson.dumps(modifiers))
                res['arch'] = etree.tostring(doc)
        return res


    # invoice_ids = fields.Many2many("account.move", string='Invoices', compute="_get_invoiced", copy=False, search="_search_invoice_ids")

    @api.depends('order_line.invoice_lines', 'project_id.tasks.invoice_ids')
    def _get_invoiced(self):
        # sale_orders = defaultdict(lambda: self.env['account.move'])
        move = False
        move_count = 0
        move_list = []

        for order in self:
            tasks = order.project_id.sudo().tasks.sudo().search(
                [('sale_id', '=', order.id), ('task_name', '=', 'Invoice')])
            default_invoices = order.order_line.invoice_lines.move_id.filtered(
                lambda r: r.move_type in ('out_invoice', 'out_refund'))
            sale_task_map_invoices = order.task_invoice_ids.filtered(
                lambda r: r.move_type in ('out_invoice', 'out_refund'))

            invoices = default_invoices + sale_task_map_invoices

            for invoice_lines in invoices:
                if invoice_lines.id not in move_list:
                    move_count += 1
                    move_list.append(invoice_lines.id)

            for move_line in tasks.sudo():
                for moves in move_line.invoice_ids:
                    if moves.id not in move_list:
                        move_count += 1
                        move_list.append(moves.id)
                    # order.invoice_ids =[(4, moves.id)]
            task_invoice_ids = [(4, moves.id) for move_line in tasks.sudo() for moves in (move_line.invoice_ids)]
            sale_invoice = [(4, move_line.id) for move_line in invoices]
            all_invoices = list(set(task_invoice_ids + sale_invoice))
            order.invoice_ids = all_invoices
            order.invoice_count = move_count
            # lot.sale_order_ids = sale_orders[lot.id]

        # for order in self:
        #     move = move_line.invoice_ids
        #     # invoices = order.order_line.invoice_lines.move_id.filtered(
        #     invoices = move.filtered(
        #         lambda r: r.move_type in ('out_invoice', 'out_refund'))
        #     order.invoice_ids = invoices
        #     order.invoice_count = len(invoices)

    # invoice_ids = fields.Many2many('account.move', 'sale_order_invoice_rel', 'order_id', 'move_id', 'Invoices',

    @api.depends('name', 'state', 'order_line', 'invoice_ids', 'invoice_ids.amount_total',
                 'project_id.tasks.invoice_ids',
                 'project_id.tasks.invoice_ids.amount_total')
    def _get_invoiced_amount(self):
        res = {}
        # cur_obj = self.pool.get('res.currency')
        for order in self:
            res[order.id] = {
                'amount_invoice': 0.0,
            }
            val1 = 0.0
            for line in order.invoice_ids:
                if line.state not in ('draft', 'cancel'):
                    val1 += line.amount_total
            order.amount_invoice = val1
        # return res

    @api.depends('name', 'state', 'order_line', 'invoice_ids', 'invoice_ids.amount_paid',
                 'project_id.tasks.invoice_ids',
                 'project_id.tasks.invoice_ids.amount_paid')
    def _get_invoiced_amount_paid(self):
        res = {}
        for order in self:
            # res[order.id] = {
            #     'amount_paid_invoice': 0.0,
            # }
            val = 0.0
            for line in order.invoice_ids:
                if line.state not in ('draft', 'cancel'):
                    val += line.amount_paid
            order.amount_paid_invoice = val
        #     res[order.id] = val
        # return res

    @api.depends('name', 'state', 'order_line', 'invoice_ids', 'invoice_ids.amount_residual',
                 'project_id.tasks.invoice_ids',
                 'project_id.tasks.invoice_ids.amount_residual')
    def _get_invoiced_amount_balance_due(self):
        res = {}
        for order in self:
            # res[order.id] = {
            #     'amount_balance_due': 0.0,
            # }
            val = 0.0
            # cur = order.pricelist_id.currency_id
            for line in order.invoice_ids:
                if line.state not in ('draft', 'cancel'):
                    val += line.amount_residual
            order.amount_balance_due = val
        #     res[order.id] = val
        # return res

    @api.depends('name', 'state', 'order_line', 'invoice_ids', 'invoice_ids.amount_total',
                 'project_id.tasks.invoice_ids',
                 'project_id.tasks.invoice_ids.amount_total')
    def _invoiced_amount(self):
        res = {}
        for sale in self:
            tot = 0.0
            for invoice in sale.invoice_ids:
                if invoice.state not in ('draft', 'cancel'):
                    tot += invoice.amount_total
            sale.invoiced_amount = tot
        #     res[sale.id] = tot
        # return res

    @api.depends('name', 'state', 'order_line', 'amount_total', 'invoiced_amount', 'invoice_ids.amount_total',
                 'project_id.tasks.invoice_ids', 'project_id.tasks.invoice_ids.amount_total',
                 'project_id.tasks.sale_id.invoiced_amount')
    def _pend_invoice_amount(self):
        res = {}
        for sale in self:
            sale_total = sale.amount_total and sale.amount_total or 0.0
            invoiced_amount = sale.invoiced_amount and sale.invoiced_amount or 0.0
            diff = sale_total - invoiced_amount
            sale.pend_invoice_amount = diff
        #     res[sale.id] = diff
        # return res

    @api.depends('name', 'state', 'order_line', 'invoice_ids', 'order_line.order_id',
                 'project_id.tasks.purchase_ids.sale_id', )
    def _get_po_ref_number(self):
        res = {}
        for order in self:
            po_obj_ids = self.env['purchase.order'].search([('sale_id', '=', order.id)])
            for po in po_obj_ids:
                if order.po_number:
                    if po:
                        order.po_number = order.po_number + ', ' + po.name
                    else:
                        order.po_number = order.po_number
                else:
                    order.po_number = po.name
            if order.po_number:
                po_number = list(set([l.strip() for l in (order.po_number.split(','))]))

                # po_number = list(set(order.po_number.split(',')))
                join_po_number = ', '.join(po_number)
                order.po_number = join_po_number

    @api.depends('name', 'state', 'order_line', 'invoice_ids', 'order_line.order_id',
                 'project_id.tasks.purchase_ids.sale_id', 'project_id.tasks.purchase_ids.amount_untaxed', )
    def _get_untaxed_po_amount(self):
        res = {}
        for order in self:
            tot = 0.0
            po_obj_ids = self.env['purchase.order'].search([('sale_id', '=', order.id)])
            for po in po_obj_ids:
                if po.state not in ('draft', 'cancel'):
                    tot += po.amount_untaxed
            order.untaxed_po_amount = tot

    @api.depends('name', 'state', 'order_line', 'invoice_ids', 'invoice_ids.amount_total',
                 'project_id.tasks.invoice_ids', 'order_line.order_id', 'project_id.tasks.purchase_ids.sale_id',
                 'project_id.tasks.invoice_ids.amount_total')
    def _get_invoice_number(self):
        res = {}
        for sale in self:
            tot = 0.0
            for invoice in sale.invoice_ids:
                if invoice.state not in ('draft', 'cancel'):
                    if sale.invoice_number:
                        if invoice:
                            sale.invoice_number = sale.invoice_number + ', ' + invoice.name
                        else:
                            sale.invoice_number = sale.invoice_number
                    else:
                        sale.invoice_number = invoice.name

    @api.depends('name', 'state', 'order_line', 'invoice_ids', 'project_id.tasks.invoice_ids',
                 'invoice_ids.amount_total',
                 'project_id.tasks.invoice_ids.amount_total', )
    def _get_not_invoiced_amount(self):
        res = {}
        for order in self:
            val = 0.0
            for i in order.invoice_ids:
                if i.state not in ('draft', 'cancel'):
                    val += i.amount_total
            order.not_invoiced = order.amount_total - val

    def export_sale(self):
        datas = {
            'id': self.id,
        }
        return self.env.ref('vox_sale_fields.report_sale_export_xls').sudo().report_action(self, data=datas)

    @api.depends('state','amount_invoice','amount_total', 'invoice_ids')
    def _compute_sale_invoice_status(self):
        for rec in self:
            if rec.state in ('draft', 'cancel'):
                rec.sale_to_invoice_status = 'no'
            elif rec.state in ('sale', 'done'):
                rec.sale_to_invoice_status = 'to_invoice'
            price_subtotal = 0.0
            discount_amount = 0.0
            for i in rec.invoice_ids.mapped('invoice_line_ids').filtered(lambda l: l.move_id.state not in ('cancel')):
                price_subtotal += i.price_subtotal
                discount_amount = i.move_id.discount_amount

            if discount_amount != 0.0:
                if discount_amount < rec.amount_untaxed:
                    rec.sale_to_invoice_status = 'par_inv'
                if discount_amount == rec.amount_untaxed or rec.amount_untaxed == price_subtotal:
                    rec.sale_to_invoice_status = 'full_inv'
            elif discount_amount == 0.0:
                if rec.amount_invoice >= rec.amount_total:
                    rec.sale_to_invoice_status = 'full_inv'
                if rec.amount_invoice < rec.amount_total:
                    rec.sale_to_invoice_status = 'par_inv'
                if rec.amount_invoice == 0.0:
                    rec.sale_to_invoice_status = 'no'

            else:
                rec.sale_to_invoice_status = 'no'

    po_number = fields.Char(compute="_get_po_ref_number", string="Supplier PO Number", store=True)
    untaxed_po_amount = fields.Float(compute="_get_untaxed_po_amount", string="Untaxed PO amount", store=True)
    invoice_number = fields.Char(compute="_get_invoice_number", string="Invoice Number", store=True)
    not_invoiced = fields.Float(compute="_get_not_invoiced_amount", string="Not Invoiced", store=True)
    amount_paid_invoice = fields.Float(compute='_get_invoiced_amount_paid', string='Paid Amount', store=True)
    amount_invoice = fields.Float(compute='_get_invoiced_amount', string='Invoice Amount', store=True)
    amount_balance_due = fields.Float(compute='_get_invoiced_amount_balance_due', string='Balance Due', store=True)
    invoiced_amount = fields.Float(compute='_invoiced_amount', string='Invoiced Amount', store=True)
    pend_invoice_amount = fields.Float(compute='_pend_invoice_amount', string='Pending To Invoice', store=True)
    sale_to_invoice_status = fields.Selection(
        [('no', 'Not yet Invoice'), ('to_invoice', 'To Invoice'), ('par_inv', 'Partially Invoiced'),
         ('full_inv', 'Fully Invoiced')], default='no', compute='_compute_sale_invoice_status',
        string="Invoice Status Sale", store=True)
