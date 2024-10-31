from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_created = fields.Boolean('Project Created', copy=False)
    discount_amount = fields.Float('Discount on Products', readonly=True,
                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    service_discount_amount = fields.Float('Discount on Service', readonly=True,
                                           states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    option_discount_amount = fields.Float(string="Discount on Options",compute='_amount_all_wrapper')

    @api.onchange('discount_amount')
    def _onchange_discount_amount(self):
        print("Wwwwwwwwwwwwwwwwwwwwwwwwwaaaaaaaaaaaaaaaaa")
        if self.state != 'draft':
            return {'warning': {
                'title': _("Warning"),
                'message': _(
                    "Verify if Tax has to be added. Check and uncheck 'add tax' "
                    "to add the tax before entering the discount.")
            }}

    @api.depends(
        'order_line',
        'order_line.actual_cost_price',
        'order_line.product_uom_qty',
        'order_line.list_price',
        'order_line.total_cost',
        'order_line.purchase_ids.state',
        'order_line.purchase_ids.order_id.state',
        'project_id.tasks.purchase_ids.order_line',
        'project_id.tasks.purchase_ids.order_line.price_subtotal',
        'project_id.tasks.purchase_ids.order_line.state',
        'project_id.tasks.task_type',
        'project_id.tasks.is_purchase',
        'order_line.purchase_ids.order_id.discount_amount',
        'additional_cost',
        'discount_amount',
        'service_discount_amount',
        'amount_gross'
    )
    def _compute_cost_price(self):
        task_obj = self.env['project.task']
        purchase_line_obj = self.env['purchase.order.line']
        for order in self:
            order_lines = []
            s_order_lines = {}
            line_cost_price_total = cubit_service_cost_price_total = 0.0
            actual_cost_price_total = purchase_price_total = 0.0
            profit = 0.0
            for s_line in order.order_line:
                order_lines.append(s_line)
                s_order_lines[s_line] = s_line
                if s_line.is_cubit_service == True:
                    cubit_service_cost_price_total += s_line.actual_cost_price
                else:
                    line_cost_price_total += s_line.actual_cost_price
                if not s_line.exclude_costprice:
                    actual_cost_price_total += s_line.actual_cost_price
                purchase_price_total += s_line.purchase_price
            # line_cost_price_total -= order.discount_amount
            # cubit_service_cost_price_total -= order.service_discount_amount
            project_id = order.project_id and order.project_id.id or False
            purchase_tasks = False
            if order.project_id:
                for project in order.project_id:
                    purchase_tasks = task_obj.search(
                        [('project_id', '=', project.id), ('project_id', '!=', False),
                         ('task_type', '=', 'is_purchase'),
                         ('purchase_ids', '!=', False)])
            if purchase_tasks:
                for task in purchase_tasks:
                    for purchase in task.purchase_ids:
                        # if purchase.state in ['approved', 'done']:
                        if purchase.state not in ['cancel']:
                            # purchase_total += purchase.amount_total
                            purchase_discount_amount = purchase.discount_amount
                            purchase_order_line = purchase_line_obj.search([('order_id', '=',
                                                                             purchase.id)])  # Check with Manu      , '|', ('active', '=', True), ('active', '=', False)
                            for p_line in purchase_order_line:
                                if p_line.import_purchase == True:
                                    import_price = p_line.price_subtotal
                                    purchase_price_total += import_price
                                    line_cost_price_total += import_price

                                # if p_line.state in ['confirmed', 'done'] and p_line.sale_line_id not in s_order_lines:
                                # if p_line.order_id.state not in ['cancel'] and p_line.sale_line_id not in s_order_lines:
                                if p_line.order_id.state not in ['cancel'] and p_line.sale_line_id == False:
                                    p_line_cost = p_line.price_subtotal
                                    line_cost_price_total += p_line_cost
                                    actual_cost_price_total += p_line_cost
                                    # if p_line.sale_line_id.exclude_costprice == False:
                                    #    actual_cost_price_total +=  p_line_cost
                                    purchase_price_total += p_line_cost
                            line_cost_price_total = line_cost_price_total - purchase_discount_amount
                            # if actual_cost_price_total > 0.0:
                            #    actual_cost_price_total = actual_cost_price_total - purchase_discount_amount
                            actual_cost_price_total = actual_cost_price_total - purchase_discount_amount
                            purchase_price_total = purchase_price_total - purchase_discount_amount
            # amount_total = self.amount_total or 0.0
            amount_untaxed = order.amount_untaxed or 0.0
            discount_amount = order.discount_amount or 0.0
            # print(order.discount_amount ,"2333333333")
            # print(order.amount_gross ,"99999999999")
            # print(line_cost_price_total ,"33333333")
            # print(cubit_service_cost_price_total ,"66666666666")
            amount_total = amount_untaxed - discount_amount
            actual_cost_price_total = actual_cost_price_total
            # actual_cost_price_total = actual_cost_price_total - discount_amount

            # profit = amount_total - actual_cost_price_total
            # profit = amount_total - (line_cost_price_total+cubit_service_cost_price_total)
            profit = order.amount_untaxed - (line_cost_price_total + cubit_service_cost_price_total)
            print(line_cost_price_total, "order.line_cost_price_total")
            print(cubit_service_cost_price_total, "order.cubit_service_cost_price_total")
            print(order.amount_gross, "order.amount_gross")
            # print(profit,"444444444444444")
            if order.additional_cost:
                profit = profit - order.additional_cost

            # print "actual_cost_price_total",actual_cost_price_total
            order.update({
                'purchase_price_total': purchase_price_total,
                'line_cost_price_total': line_cost_price_total,
                'cubit_service_cost_price_total': cubit_service_cost_price_total,
                'actual_cost_price_total': line_cost_price_total + cubit_service_cost_price_total,
                # 'actual_cost_price_total': actual_cost_price_total,
                'profit': profit,
            })

    purchase_price_total = fields.Float(string='Purchase Price Total', store=True, readonly=True,
                                        compute='_compute_cost_price', copy=False)
    line_cost_price_total = fields.Float(string='Sale Cost Price Total', store=True, readonly=True,
                                         compute='_compute_cost_price', copy=False)
    cubit_service_cost_price_total = fields.Float(string='Cubit Service Cost Price Total', store=True, readonly=True,
                                                  compute='_compute_cost_price', copy=False)
    actual_cost_price_total = fields.Float(string='Actual Cost Price Total', store=True, readonly=True,
                                           compute='_compute_cost_price', copy=False)
    profit = fields.Float(string='Profit', store=True, readonly=True, compute='_compute_cost_price', copy=False,
                          groups="vox_task_template.group_gross_profit_user,base.group_system")

    additional_cost = fields.Float(string='Additional Cost', store=True, copy=False)

    @api.depends(
        'discount_amount',
        'service_discount_amount',
        'order_line',
        'order_line.price_unit',
        'order_line.tax_id',
        'order_line.discount',
        'order_line.product_uom_qty',
        'order_line.margin',
        'order_line.actual_cost_price',
        'order_line.list_price',
        'order_line.total_cost',
        'distribution_tax_ids',
        'discount_distribution_type',
        'order_line.option_discount',
    )
    def _amount_all_wrapper(self):
        line_obj = self.env['sale.order.line']
        if self:
            for order in self:
                total_vat_on_net_taxable = total_net_taxable = val = val1 = val3 = global_disc = 0.0
                qty_price_total = 0.0
                tax_wise_total = 0.0
                sum_qty_price_unit = 0.0
                sum_option_discount = 0.0
                for tax_qty_price in order.order_line:
                    if tax_qty_price.tax_id and tax_qty_price.tax_id.ids[0] in order.distribution_tax_ids.ids:
                        tax_wise_total += (tax_qty_price.product_uom_qty * tax_qty_price.unit_price)
                print("tax_wise_total", tax_wise_total)
                for qty_price in order.order_line:
                    qty_price_total += (qty_price.product_uom_qty * qty_price.unit_price)

                if not 0.0 <= (order.discount_amount + order.service_discount_amount) <= qty_price_total:
                    raise ValidationError(_('Enter proper discount'))
                for line in order.order_line:
                    tax_on_net_taxable = tax = 0.0
                    val1 += line.price_included
                    qty = line_obj._calc_line_quantity(line)
                    if line.tax_id:
                        for c in line.tax_id.compute_all(line.unit_price, order.currency_id, qty, False,
                                                         line.order_id.partner_id)['taxes']:
                            tax += c.get('amount', 0.0)
                    val += tax
                    val3 += line.total_cost
                    sum_qty_price_unit += (line.unit_price * line.product_uom_qty)
                    print("tax", line.tax_id.ids)
                    print("des_ids", order.distribution_tax_ids.ids)
                    if order.discount_distribution_type == 'against_item':
                        line.discount_distribution = ((order.service_discount_amount + order.discount_amount) /
                                                      qty_price_total) * (
                                                                 line.product_uom_qty * line.unit_price) + line.option_discount if line.unit_price else 0.0
                    elif order.distribution_tax_ids and line.tax_id and line.tax_id.ids[
                        0] in order.distribution_tax_ids.ids:
                        print("dist", order.distribution_tax_ids.ids)
                        line.discount_distribution = ((order.service_discount_amount + order.discount_amount) /
                                                      tax_wise_total) * (
                                                                 line.product_uom_qty * line.unit_price) + line.option_discount if tax_wise_total else 0.0
                    else:
                        line.discount_distribution = 0.0
                    line.discount = (line.discount_distribution / (
                            line.product_uom_qty * line.unit_price) * 100.0) if line.discount_distribution else 0.0
                    line.net_taxable = (line.product_uom_qty * line.unit_price) - line.discount_distribution
                    line.price_included = (line.product_uom_qty * line.unit_price) - line.discount_distribution
                    if line.tax_id:
                        for c in line.tax_id.compute_all(line.price_included, order.currency_id, 1, False,
                                                         line.order_id.partner_id)['taxes']:
                            tax_on_net_taxable += c.get('amount', 0.0)
                        line.tax_total = tax_on_net_taxable
                    line.price_total_val = line.price_included + line.tax_total
                    total_vat_on_net_taxable += line.tax_total
                    total_net_taxable += line.price_included
                    sum_option_discount += line.option_discount
                order_line = line_obj.search([
                    ('order_id', '=', order.id),
                    ('global_discount_line', '=', True),
                    ('active', '=', False)
                ])

                for line in order_line:
                    if line.global_discount_line:
                        tax = 0.0
                        val1 += line.price_included
                        qty = line_obj._calc_line_quantity(line)
                        if line.tax_id:
                            for c in line.tax_id.compute_all(line.unit_price, order.currency_id, qty, False,
                                                             line.order_id.partner_id)['taxes']:
                                tax += c.get('amount', 0.0)
                        val += tax
                        global_disc += line.price_included

                service_order_line = line_obj.search([
                    ('order_id', '=', order.id),
                    ('service_global_discount_line', '=', True),
                    ('active', '=', False)
                ])
                for line in service_order_line:
                    if line.service_global_discount_line:
                        tax = 0.0
                        val1 += line.price_included
                        qty = line_obj._calc_line_quantity(line)
                        if line.tax_id:
                            for c in line.tax_id.compute_all(line.unit_price, order.currency_id, qty, False,
                                                             line.order_id.partner_id)['taxes']:
                                tax += c.get('amount', 0.0)
                        val += tax
                        global_disc += line.price_included
                amount_gross = round(val1, 6)
                amount_total_cost = round(val3, 6)
                order.update({
                    'amount_untaxed': total_net_taxable,
                    'amount_gross': sum_qty_price_unit,
                    'amount_total': total_net_taxable + total_vat_on_net_taxable,
                    'amount_total_cost': amount_total_cost,
                    'amount_tax': total_vat_on_net_taxable,
                    'option_discount_amount': sum_option_discount,
                })

    @api.depends('order_line', 'order_line.tax_id', 'discount_distribution_type')
    def _compute_line_taxes(self):
        print("compute_line_taxes")
        dis_taxes = []
        for rec in self:
            for line in rec.order_line:
                dis_taxes.append(line.tax_id.ids[0]) if line.tax_id else dis_taxes
            rec.line_taxes_ids = list(set(dis_taxes))

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')],
                                     string='Global Discount type', readonly=True, default='amount')
    amount_untaxed = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True,
                                  string='Untaxed Amount', help="The amount without tax.", track_visibility='always')
    amount_gross = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True, string='Gross Amount',
                                help="The amount after discount without tax.", track_visibility='always')
    amount_total = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True, string='Total',
                                help="The total amount.")
    amount_total_cost = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True, string='Sale Cost (xls)',
                                     help="The total Cost.")
    amount_tax = fields.Float(compute='_amount_all_wrapper', store=True, readonly=True, string='Taxes',
                              help="The tax amount.")
    discount_distribution_type = fields.Selection([('against_item', 'Item Wise'), ('against_tax', 'Tax Wise')],
                                                  default='against_item', string="Discount Type")
    distribution_tax_ids = fields.Many2many('account.tax', string="Tax")
    line_taxes_ids = fields.Many2many('account.tax', string="Line Taxes", compute='_compute_line_taxes')

    @api.model
    def create(self, values):
        order = super(SaleOrder, self).create(values)
        return order

    def write(self, values):
        res = super(SaleOrder, self).write(values)
        return res

    def reset_purchase_qty(self):
        for rec in self:
            lines = self.env['sale.order.line'].search([('order_id', '=', rec.id)])
            for line in lines:
                line._compute_cost_price()

    def update_option_discount_action(self):
        wiz = self.env['update.option.discount'].create({'sale_id': self.id})
        options = list(set(self.order_line.mapped('options')))
        for opt in options:
            if opt:
                self.env['update.option.discount.line'].create({
                    'option_discount_id': wiz.id,
                    'name': opt,
                })
        view = self.env.ref(
            'vox_task_template.view_option_discount_update_wizard')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'update.option.discount',
            'res_id': wiz.id,
            'view_id': view.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new'}


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('unit_price', 'product_uom_qty')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = rec.unit_price * rec.product_uom_qty

    global_discount_line = fields.Boolean(string="Line is a global discount line", default=False)
    service_global_discount_line = fields.Boolean(string="Line is a Service global discount line", default=False)
    active = fields.Boolean(string="Active", default=True)
    task_delivery_line_ids = fields.One2many('task.delivery.line', 'deliv_sale_line_id', 'Delivery Lines')

    virtual_purchased_qty = fields.Float(string='Actual Purchased Qty', store=True, compute='_calculate_purchased_qty')

    virtual_delivered_qty = fields.Float(digits='Product Unit of Measure',
                                         string='Actual Delivered Qty', store=True, compute='_calculate_delivered_qty')
    discount_distribution = fields.Float(string="Discount Distribution")
    net_taxable = fields.Float(string="Net Taxable")
    total_price = fields.Float(string="Total Price", compute='_compute_total_price')
    option_discount = fields.Float(string="Option Discount")

    @api.constrains('is_cubit_service', 'margin')
    def change_cubit_service_margin(self):
        for rec in self:
            if rec._origin:
                if rec.global_discount_line or rec.service_global_discount_line:
                    pass
                else:
                    if (not rec.is_cubit_service and rec.margin == 0.0 and not rec.name == 'Global Discount'
                            and 'Down Payment' not in rec.name):
                        raise ValidationError(_('Margin cannot be Zero'))

    @api.depends('is_cubit_service', 'exclude_purchase',
                 'order_id.project_id.tasks.purchase_ids.order_line',
                 'task_delivery_line_ids',
                 'task_delivery_line_ids.qty'
                 )
    def _calculate_delivered_qty(self):
        for line in self:
            deliv_qty = 0.0
            if not line.is_cubit_service and not line.exclude_purchase:
                for deliv_line in line.task_delivery_line_ids:
                    deliv_qty += deliv_line.qty and deliv_line.qty or 0.0
            line.virtual_delivered_qty = deliv_qty
        return

    @api.depends('is_cubit_service', 'exclude_purchase',
                 'order_id.project_id.tasks.purchase_ids.order_line',
                 'order_id.project_id.tasks.purchase_ids',
                 'order_id.project_id.tasks'
                 )
    def _calculate_purchased_qty(self):

        pur_order_line_obj = self.env['purchase.order.line']
        task_obj = self.env['project.task']
        for line in self:
            pur_qty = 0
            sale_project_id = line.order_id.project_id
            task_ids = task_obj.search([('project_id', '=', sale_project_id.id), ('task_type', '=', 'is_purchase')])
            if not line.is_cubit_service:
                if not line.exclude_purchase:
                    purchase_order_ids = []
                    for task in task_obj.browse(task_ids.ids):
                        if task.purchase_ids:
                            for purchase in task.purchase_ids:
                                purchase_order_ids.append(purchase.id)
                    pur_line_ids_sale_line = pur_order_line_obj.search([('sale_line_id', '=', line.id),
                                                                        ('state', '!=', 'cancel')])

                    if pur_line_ids_sale_line:
                        for pur_line in pur_order_line_obj.browse(pur_line_ids_sale_line.ids):
                            pur_qty += pur_line.product_qty
                    '''elif pur_line_ids_part_num:                     
                        for pur_line in pur_order_line_obj.browse(cr, uid, pur_line_ids_part_num, context=context):
                            pur_qty += pur_line.product_qty
                    elif pur_line_ids_name:                     
                        for pur_line in pur_order_line_obj.browse(cr, uid, pur_line_ids_name, context=context):
                            pur_qty += pur_line.product_qty'''
            purchased_qty = pur_qty
            state = line.state
            if state not in ['draft', 'sent']:
                line.virtual_purchased_qty = purchased_qty
            else:
                line.virtual_purchased_qty = 0
        return

    @api.depends(
        'product_uom_qty',
        'list_price',
        'total_cost',
        'exclude_costprice',
        'is_cubit_service',
        'purchase_ids.state',
        'purchase_ids.order_id.state',
        'order_id.project_id.tasks.purchase_ids.order_line',
        'order_id.project_id.tasks.purchase_ids.order_line.price_subtotal',
        'order_id.project_id.tasks.purchase_ids.order_line.state',
    )
    def _compute_cost_price(self):
        purchase_qty = 0.0
        # purchase_price = 0.0
        line_cost = 0.0
        for line in self:
            purchase_price = 0.0
            if not line.exclude_costprice:
                if not line.is_cubit_service:
                    # s_order_lines[self] = self
                    line_cost = line.total_cost
                    # purchase_qty = 0.0
                    # line_cost = 0.0
                    for p_line in line.purchase_ids:
                        # if p_line.state in ['confirmed', 'done'] and p_line.order_id.state in ['approved', 'done']:

                        if p_line.order_id.state not in ['cancel']:
                            p_line_qty = p_line.product_qty
                            purchase_qty += p_line_qty
                            o_line_qty = line.product_uom_qty
                            if p_line_qty <= o_line_qty:
                                qty = p_line_qty
                            else:
                                qty = o_line_qty
                            cost = line.cost_price
                            total_cost = cost * qty
                            line_cost = line_cost - total_cost
                            p_line_cost = p_line.price_subtotal
                            purchase_price += p_line.price_subtotal
                            line_cost = line_cost + p_line_cost
                        elif p_line.order_id.state == 'cancel':
                            p_line_qty = p_line.product_qty
                            for s_line in p_line.sale_line_id:
                                s_line.write({
                                    'purchased_qty': s_line.purchased_qty - p_line_qty
                                    if s_line.purchased_qty else p_line_qty
                                })

                else:
                    line_cost = line.price_included
                    line_cost = float(line_cost * (50.0 / 100.0))
            line.actual_cost_price = line_cost
            line.purchase_qty = sum(line.purchase_ids.filtered(lambda l: l.state not in 'cancel').mapped(
                'product_qty')) if line.purchase_ids else 0.0
            line.purchase_price = purchase_price
