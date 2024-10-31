# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from collections import defaultdict, Counter
import datetime
from datetime import datetime
import string
from dateutil.relativedelta import relativedelta
import logging
import decimal

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    vendor_detail_id = fields.One2many('vendor.details', 'sale_order_id', 'Vendor Details', copy=True)
    presale_id = fields.One2many('presale.information', 'sale_order_id', 'Presales Information', copy=True)
    cubit_id = fields.Integer(string="Cubit ID")
    po_number = fields.Char(string="PO number")

    vat_certificate = fields.Binary(string="VAT certificate")
    passport_copy = fields.Binary(string="Passport copy")
    trade_license = fields.Binary(string="Trade license")
    lpo_number = fields.Char(string="LPO Number")
    lpo_email = fields.Boolean(string="LPO by Email Confirmation")
    lpo_email_attachment = fields.Binary(string="LPO by Email Confirmation attachment.")
    trn_number = fields.Char(string="TRN number")
    planned_hours = fields.Float(string="Initial planned hours")
    end_user_name = fields.Char(string="Name")
    end_user_mail = fields.Char(string="Email")
    end_user_address = fields.Char(string="Address")
    end_user_mobile = fields.Char(string="Mobile")
    end_user_fax = fields.Char(string="FAX")
    end_user_website = fields.Char(string="Website")
    end_user_company = fields.Many2one('res.company', string="End User Company")
    end_user_company_value = fields.Char(string="Company")
    end_user_vat = fields.Char(string="VAT")
    sale_note = fields.Char(string='Note')
    partner_contact = fields.Many2one('res.partner', string='Customer Contact', domain="[('customer', '=', True)]")
    quotation_validity = fields.Many2one('quotation.validity', string='Quotation Validity')
    delivery_terms = fields.Many2one('delivery.terms', string='Delivery Terms')
    add_tax = fields.Boolean(string='Add Tax',
                             help='By checking this boolean will add TAX automatically in all the line items',
                             readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, )
    tax_inclusive = fields.Char(string='Prices')
    # payment_terms = fields.Char(string="Payment Terms")

    # proposal fields in sale

    proposal_heading = fields.Char('Proposal heading')
    introduction_letter_date = fields.Date('Letter Date')
    introduction_letter_to = fields.Text('To Address')
    introduction_letter_subject = fields.Text('Subject')
    introduction_letter = fields.Text('Introduction Letter')
    items_header = fields.Char('Proposal Items Header')
    terms_and_condition_index = fields.Integer('General Terms and condition index')

    total_qty = fields.Monetary(string='Total Qty')
    total_delivered_qty = fields.Monetary(string='Total Delivered Qty')
    total_purchased_qty = fields.Monetary(string='Total Purchased Qty')
    revision_ids = fields.Many2many('sale.order', 'sale_revision_rel', 'sale_id', 'rev_id', 'Revisions', )
    revision = fields.Boolean('Revision')
    section_line = fields.One2many('sale.order.section.summary', 's_order_id', string='Section',
                                   copy=True,
                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                   )
    # project_reference = fields.Char(string="Project Reference")
    lpo_doc = fields.Binary(string="LPO Document")
    lpo_doc_required = fields.Boolean(string="Doc Required")
    # active = fields.Boolean(default=True, groups='sales_team.group_sale_manager')
    active = fields.Boolean(default=True)
    planned_hours_for_l1 = fields.Float('Planned Hours for L1')
    planned_hours_for_l2 = fields.Float('Planned Hours for L2')

    project_payment_terms = fields.One2many('project.payment.terms', 'sale_id', string='Payment Term – projects  ')
    msp_amc_payment_terms = fields.One2many('msp.amc.payment.terms', 'sale_id', string='Payment Term MSP/AMC ')
    # @api.onchange('lpo_number')
    # def onchange_attachments(self):
    #     print(self.env['mail.message'].search([('res')]))

    attachment_ids = fields.Many2many('ir.attachment', string="Attachments", compute="_compute_attachment_ids")

    def _compute_attachment_ids(self):
        for order in self:
            order.attachment_ids = self.env['ir.attachment'].search(
                [('res_model', '=', 'sale.order'), ('res_id', '=', order.id)])

    @api.onchange('planned_hours')
    def planned_hour_checking(self):
        for rec in self:
            if rec.planned_hours != rec.planned_hours_for_l1 + rec.planned_hours_for_l2:
                raise ValidationError(_('Planned hours must be equal to sum of Planned hours for L1 and L2'))

    def toggle_active(self):
        if self.filtered(lambda so: so.state not in ["done", "cancel"] and so.active):
            raise UserError(_("Only 'Locked' or 'Canceled' orders can be archived"))
        return super().toggle_active()

    @api.onchange('partner_id')
    def change_partner_tax(self):
        for rec in self:
            # if rec.env.uid != rec.user_id.id or not self.env.user.has_group('base.admin_user') and rec.partner_id:
            #     raise ValidationError(_("You can't edit This field"))
            if rec.partner_id:
                rec.partner_contact = False
                if rec.partner_id.vat:
                    rec.trn_number = rec.partner_id.vat
                else:
                    rec.trn_number = False

    @api.onchange('lpo_number')
    def change_lpo_number(self):
        for rec in self:
            if rec.lpo_number:
                rec.lpo_doc_required = True
            else:
                rec.lpo_doc_required = False

    @api.onchange('add_tax')
    def onchange_add_tax(self):
        tax = self.env['account.tax'].sudo().search([('sale_add_tax', '=', True), ('type_tax_use', '=', 'sale')])
        for order in self:
            if order.add_tax == True:
                for line in order.order_line:
                    line.write({'tax_id': [(4, t.id) for t in tax if t]})
                    # line.write({'tax_id': [(4, t.id) for t in tax]})
                    # line.write({'tax_id': [x.id for x in tax]})
            else:
                for line in order.order_line:
                    line.write({'tax_id': False})

    # @api.depends('add_tax')
    # def compute_add_tax(self):
    #     tax = self.env['account.tax'].sudo().search([('sale_add_tax', '=', True), ('type_tax_use', '=', 'sale')])
    #     for order in self:
    #         if order.add_tax == True:
    #             for line in order.order_line:
    #                 line.write({'tax_id': [(4, t.id) for t in tax if t]})
    #         else:
    #             for line in order.order_line:
    #                 line.write({'tax_id': False})

    def solve(self, dataset, group_by_key, sum_value_keys):
        # dic = defaultdict(dict)
        dic = defaultdict(Counter)
        for item in dataset:
            key = item[group_by_key]
            vals = {k: item[k] for k in sum_value_keys}
            dic[key].update(vals)
            # dic = vals
        return dic

    def update_session(self):
        context = self._context.copy() or {}
        context.update({'update_session': True})
        self.section_line.with_context(context).unlink()
        section = []

        for line in self.order_line.filtered(lambda x: (x.sale_layout_cat_id and x.sale_layout_cat_id.id or False)):
            vals = {'sale_layout_cat_id': line.sale_layout_cat_id.id,
                    'total_cost': line.total_cost,
                    'unit_price': line.unit_price,
                    'price_included': line.price_included,
                    'gross_profit': line.price_included - line.total_cost,
                    }
            section.append(vals)
        grouped_value = self.solve(section, 'sale_layout_cat_id', ['total_cost', 'unit_price', 'price_included',
                                                                   'gross_profit'])
        j_value = dict((k, dict(v)) for k, v in grouped_value.items())
        res = []
        negative = []
        for j in j_value:
            section_name = self.env['sale_layout.category'].search([('id', '=', j)]).name
            k = {'sale_layout_cat_id': j,
                 'name': section_name
                 }
            j_value[j].update(k)
            # res.append(j_value[j])
            neg3 = (0, 0, j_value[j])
            negative.append(neg3)
        for n in negative:
            n[2].update({'gross_profit_perc':(n[2].get('gross_profit')/n[2].get('price_included')*100.0) if n[2].get('price_included') else 0.0})
        self.update({

            'section_line': negative
        })
        # self.section_line = res

    @api.model
    def run_l3_l4_email_reminder(self):
        l1_users = self.env.ref('vox_user_groups.group_sale_salesman_level_1_user').users.partner_id.ids
        l2_users = self.env.ref('vox_user_groups.group_sale_salesman_level_2_user').users.partner_id.ids
        l3_users = self.env.ref('vox_user_groups.group_sale_salesman_level_3_user').users.partner_id.ids
        l4_users = self.env.ref('vox_user_groups.group_sale_salesman_level_4_user').users.partner_id.ids
        if l3_users and l4_users:
            users = l3_users + l4_users
        elif l3_users and not l4_users:
            users = l3_users
        elif l4_users and not l3_users:
            users = l4_users
        else:
            users = []
        sales_team_users = self.env['crm.team'].search(
            [('team_code', '=', 'sales_team'), ('sale_team_code', '=', False)]).mapped('member_ids').partner_id.ids
        total_users = list(
            (set(users).intersection(set(sales_team_users))).difference(set(l1_users).union(set(l2_users))))
        today = fields.Date.context_today(self)
        template = self.env.ref('crm_lead_fields.mail_template_to_lvl_three_and_four')
        orders = self.env['sale.order'].search([])
        for rec in orders:
            if rec.presale_id:
                for info in rec.presale_id:
                    if info.next_action_date:
                        if not info.done and today == info.next_action_date + relativedelta(days=1):
                            email_values = {'email_to': rec.user_id.email, 'recipient_ids': total_users}
                            if template:
                                template.send_mail(rec.id, force_send=True, email_values=email_values)

    @api.onchange('lpo_email_attachment')
    def _onchange_lpo_attchment(self):
        for sale in self:
            if sale.lpo_email_attachment:
                sale.lpo_email = True

    # def action_create_revision_old(self):
    #     for obj in self:
    #         name = obj.name
    #         if '/REV/' in name:
    #             raise osv.except_osv(_('Error!'),
    #                                  _('Please create the revision from base version of quotation'))
    #         copy = self.copy(cr, uid, obj.id)
    #         revision_ids = obj.revision_ids
    #         new_name = name + '/REV/' + str(len(revision_ids) + 1)
    #         revision_values = [(4, sale.id) for sale in revision_ids]
    #         revision_values += [(4, copy)]
    #         self.write(cr, uid, copy, {'name': new_name, 'revision': True})
    #         self.write(cr, uid, obj.id, {'revision_ids': revision_values})
    #     return True

    def action_create_revision(self):

        self._create_revision()
        action = self.env["ir.actions.actions"]._for_xml_id('crm_lead_fields.opp_action_sale_order_import')
        action['context'] = {'default_sale_id': self.id}
        return action

    def _create_revision(self):
        for obj in self:
            name = obj.name
            copy = self.copy().id
            revision_ids = obj.revision_ids
            today = fields.Date.today()
            today = today.strftime('%d-%m-%y')
            if '/REV/' in name:
                rev_name = name.split('/REV/', 1)[0]
                new_name = rev_name + '/REV/' + str(len(revision_ids) + 1)
            else:
                new_name = name + '/REV/' + str(len(revision_ids) + 1)
            revision_values = [(4, sale.id) for sale in revision_ids]
            old_revision_values = [(4, sale.id) for sale in revision_ids]
            revision_values += [(4, copy)]
            revision_sale = self.env['sale.order'].browse(copy)
            revision_sale_name = revision_sale.write({
                'name': obj.name,
                'date_order': obj.date_order,
            })
            self.write({'revision_ids': revision_values,
                        'name': new_name,
                        'date_order':fields.datetime.now(),})
        return True

    project_created = fields.Boolean('Project Created')
    # discount_amount = fields.float('Discount', readonly=True,
    #                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    project_id = fields.Many2one('project.project', 'Project', copy=False)

    # project_id = fields.Many2one(
    #     'project.project', 'Project', readonly=True,
    #     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
    #     help='Select a non billable project on which tasks can be created.')

    def copy(self, default=None):
        res = super().copy(default)
        if res.project_id:
            res.project_id = False
        if res.project_ids:
            res.project_ids = False
        default = dict(default or {})
        # if self.get('project_id'):
        # if self.project_id:
        #     self.project_id = False
        # if self.project_ids:
        #     self.project_ids =False
        # default.update({'project_id': False , })
        return res

    crm_lead_id = fields.Many2one('crm.lead', 'Opportunity')
    crm_vendor_id = fields.Many2one('crm.lead', 'Vendor Details')
    cubit_sale_id = fields.Integer(string="Cubit ID")
    state = fields.Selection(selection_add=[
        ('waiting_date', 'Waiting Schedule'),
        ('manual', 'Sale to Invoice'),
        ('shipping_except', 'Shipping Exception'),
        ('invoice_except', 'Invoice Exception'),
    ])
    end_user_req_condition = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="End user required conditions")


    def action_confirm(self):
        for rec in self:
            if rec.crm_lead_id:
                rec.crm_lead_id.expected_revenue = rec.amount_total
            if all((rec.end_user_name, rec.end_user_address, rec.end_user_fax,
                    rec.end_user_company_value, rec.end_user_mail,
                    rec.end_user_mobile, rec.end_user_website,
                    rec.end_user_vat)):
                super().action_confirm()
            elif rec.end_user_req_condition == 'yes':
                super().action_confirm()
            else:
                end_user_req_conditions_wiz = self.env['end.user.req.conditions']
                return {
                    'name': 'End User Required Conditions',
                    'type': 'ir.actions.act_window',
                    'res_model': 'end.user.req.conditions',
                    'view_mode': 'form',
                    'res_id': end_user_req_conditions_wiz.id,
                    'target': 'new',
                }

    payment_term = fields.Char(string="Payment Terms")


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    _sql_constraints = [
        ('accountable_required_fields',
         'check(1=1)',
         "Missing required fields on accountable sale order line."),

    ]
    cubit_sale_line_id = fields.Integer(string="Cubit ID")

    @api.depends('part_number')
    def _compute_sl_no(self):
        for order in self.mapped('order_id'):
            number = 1
            for line in order.order_line:
                line.sl_no = number
                number += 1

    # @api.depends('order_id','order_id.add_tax')
    # def compute_add_tax(self):
    #     print(999999999999999999999999999999999999999999999999)
    #     _logger.debug('Compte function executesssss')
    #     tax = self.env['account.tax'].sudo().search([('sale_add_tax', '=', True), ('type_tax_use', '=', 'sale')])
    #     for order in self:
    #         if order.order_id.add_tax == True and order.order_id.amount_tax == 0:
    #             _logger.debug('Insde 0000 condition')
    #             order.tax_id = [(4, t.id) for t in tax if t]
    #             #order.write({'tax_id': [(4, t.id) for t in tax if t]})
    #         else:
    #             order.tax_id = False
    # order.write({'tax_id': False})

    # @api.depends('part_number')
    # def _compute_sl_no(self):
    #     sl_no = [x.id for x in self.order_id.order_line].index(self.id)
    #     self.sl_no = int(sl_no) + 1
    # tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)], compute='compute_add_tax', store=True)
    sl_no = fields.Integer('Sl#', compute='_compute_sl_no', readonly=True)

    part_number = fields.Char(string='Part Number')
    list_price = fields.Float(string='List Price')
    supplier_discount = fields.Float(string='Vendor Disc(%)')
    currency_rate = fields.Float(string='Currency Rate')
    tax = fields.Float(string='Tax(%)')
    margin = fields.Float(string='Margin', digits='Margin Product Price', store=True)
    # margin = fields.Float(string='Margin', digits='Product Price',store=True)
    vendor_id = fields.Many2one('res.partner', 'Vendor', domain="[('supplier', '=', True)]")
    sale_layout_cat_id = fields.Many2one('sale_layout.category', string='Section')
    line_category_id = fields.Many2one('sale.line.category', string='Category')
    line_brand_id = fields.Many2one('sale.line.brand', string='Brand')
    line_technology_id = fields.Many2one('sale.line.technology', string='Technology')
    remarks = fields.Char(string='Remarks')
    serial_num = fields.Char(string='Serial Number')
    service_suk = fields.Char(string='Service SUK')
    begin_date = fields.Date(string='Begin Date')
    end_date = fields.Date(string='End Date')
    exclude_purchase = fields.Boolean('Exclude PO', default=False)
    exclude_costprice = fields.Boolean('Exclude Cost', )
    th_weight = fields.Char(string='Weight', readonly=True)
    # section_ids = fields.Many2many('sale_layout.category', 'order_line_section_parent_childs_rel', "parent_id",
    #                                "child_id", "Clubbing Sections")

    unit_price = fields.Monetary(compute='_amount_price_unit', string='Unit Price', store=True)
    cost_price = fields.Monetary(compute='_amount_cost_price', string='Cost Price', store=True)
    total_cost = fields.Monetary(compute='_amount_total_cost', string='Total Cost', store=True)

    price_included = fields.Monetary(compute='_amount_line_included', string='Subtotal', store=True)
    price_total_val = fields.Monetary(compute='_amount_line_included_tax', string='Total', store=True)
    # compute = '_amount_line_included_tax',
    tax_total = fields.Monetary(compute='_amount_line_tax', string='Tax', store=True)
    # compute = '_amount_line_tax',

    actual_cost_price = fields.Float(string='Actual Cost Price', compute='_compute_cost_price', store=True,
                                     readonly=True, copy=False)
    #
    purchase_qty = fields.Float(string='Purchase Qty', store=True, compute='_compute_cost_price', readonly=True,
                                copy=False)
    # compute = '_compute_cost_price',
    purchase_price = fields.Float(string='Purchase Price', store=True, compute='_compute_cost_price', readonly=True,
                                  copy=False)
    # compute = '_compute_cost_price',
    cubit_service = fields.Boolean(string='Is a cubit service?', compute='_get_cubit_service',
                                   inverse='_set_cubit_service', readonly=False, store=True, copy=False)
    # cubit_service = fields.Boolean(string='Is a cubit service?', compute='_get_cubit_service', store=True, readonly=False, copy=False)
    is_cubit_service = fields.Boolean(string='Is a cubit service?', readonly=False, copy=False, default=False)

    virtual_purchased_qty = fields.Float(string='Actual Purchased Qty', store=True)
    # compute = '_calculate_purchased_qty',
    virtual_delivered_qty = fields.Float(digits='Product Unit of Measure',
                                         string='Actual Delivered Qty', store=True, )
    # compute='_calculate_delivered_qty',
    purchased_qty = fields.Float(string='Purchase Qty', store=True, readonly=True, compute='_compute_cost_price')

    customer_discount = fields.Float(string='Cust Disc')
    product_uos_qty = fields.Float('Quantity (UoS)', digits='Product Unit of Measure', readonly=True,
                                   states={'draft': [('readonly', False)]}),
    product_uos = fields.Many2one('uom.uom', 'Product UoS')
    options = fields.Char(string='Options')
    service_duration = fields.Char(string='Service Duration')
    # renewal_category = fields.Char(string='Renewal Category')
    renewal_category = fields.Selection([('renewal', 'Renewal'),
                                         ('non_renewal', 'Non Renewal')], string='Renewal Category')
    month = fields.Char(string='Month')
    distributor = fields.Char(string='Distributor')
    presales_person = fields.Char(string='Presales Person')
    hs_code = fields.Char(string='Hs Code')
    country_of_origin = fields.Char(string='Country Of Origin')

    round_discount = fields.Float(string='Rounding Disc')

    purchase_ids = fields.One2many('purchase.order.line', 'sale_line_id', 'Purchases')

    c_red = fields.Char(compute='_determine_red', string='Red')
    c_orange = fields.Char(compute='_determine_orange', string='Orange')
    c_blue = fields.Char(compute='_determine_blue', string='Blue')

    global_discount_line = fields.Boolean(string="Line is a global discount line", default=False)
    partially_purchased = fields.Boolean('Partially Purchased')
    # not_purchased = fields.Boolean('Not Purchased')
    is_purchase_confirmed = fields.Boolean('Purchase Confirmed')

    @api.onchange('renewal_category', 'service_duration')
    def change_renewal(self):
        for rec in self:
            if rec.renewal_category == 'renewal' and rec.service_duration in ("0.0", "0", "0.00", False):
                raise ValidationError(_('Service Duration cannot be Zero'))

    # @api.onchange('is_cubit_service', 'margin')
    # def change_cubit_service_margin(self):
    #     for rec in self.order_id.order_line:
    #         if rec._origin:
    #             if not rec.is_cubit_service and rec.margin == 0.0:
    #                 raise ValidationError(_('Margin cannot be Zero'))

    # def write(self,vals):
    #     if not vals.get('is_cubit_service') and vals.get('margin',False)==0.0:
    #         raise ValidationError(_('Margin cannot be Zero'))
    #     else:
    #         return super().write(vals)

    def _determine_blue(self):
        res = {}

        for line in self:
            purchased_qty = line.purchased_qty
            purchased_qty = line.virtual_purchased_qty
            product_uom_qty = line.product_uom_qty
            state = line.state
            if line.is_cubit_service == True or line.exclude_purchase == True:
                purchased_qty = 0
                product_uom_qty = 0
            if state not in ['draft',
                             'sent'] and purchased_qty != 0.0 and (
                    purchased_qty < product_uom_qty or purchased_qty > product_uom_qty) and line.exclude_purchase == False and line.is_cubit_service == False:
                line.c_blue = 1
                # res[line.id] = 1
            else:
                line.c_blue = 0
                # res[line.id] = 0
        return

    def _determine_orange(self):
        res = {}

        for line in self:
            purchased_qty = line.purchased_qty
            purchased_qty = line.virtual_purchased_qty
            product_uom_qty = line.product_uom_qty
            if line.is_cubit_service == True or line.exclude_purchase == True:
                purchased_qty = 1
            state = line.state
            if state not in ['draft',
                             'sent'] and purchased_qty == 0.0 and line.exclude_purchase == False and line.is_cubit_service == False:
                line.c_orange = 1
                # res[line.id] = 1
            else:
                line.c_orange = 0
                # res[line.id] = 0
        return

    def _determine_red(self):
        res = {}
        for line in self:
            purchased_qty = line.purchased_qty
            purchased_qty = line.virtual_purchased_qty
            product_uom_qty = line.product_uom_qty
            if line.is_cubit_service == True or line.exclude_purchase == True:
                purchased_qty = 0
                product_uom_qty = 0
            state = line.state
            if state not in ['draft',
                             'sent'] and purchased_qty > product_uom_qty and line.exclude_purchase == False and line.is_cubit_service == False:
                line.c_red = 1
            else:
                line.c_red = 0
                # res[line.id] = 0
        return res

    @api.depends(
        'product_uom_qty',
        'list_price',
        'total_cost',
        'exclude_costprice',
        # 'is_cubit_service',
        'purchase_ids.state',
        'purchase_ids.order_id.state',
        # 'order_id.project_id.tasks.purchase_ids.order_line',
        # 'order_id.project_id.tasks.purchase_ids.order_line.price_subtotal',
        # 'order_id.project_id.tasks.purchase_ids.order_line.state',
    )
    def _compute_cost_price(self):
        return
        # purchase_qty = 0.0
        # purchase_price = 0.0
        # line_cost = 0.0
        # for line in self:
        #     if not line.exclude_costprice:
        #         if not line.is_cubit_service:
        #             # s_order_lines[self] = self
        #             line_cost = line.total_cost
        #             for p_line in line.purchase_ids:
        #                 # if p_line.state in ['confirmed', 'done'] and p_line.order_id.state in ['approved', 'done']:
        #                 if p_line.order_id.state not in ['cancel']:
        #                     p_line_qty = p_line.product_qty
        #                     purchase_qty += p_line_qty
        #                     o_line_qty = line.product_uom_qty
        #                     if p_line_qty <= o_line_qty:
        #                         qty = p_line_qty
        #                     else:
        #                         qty = o_line_qty
        #                     cost = line.cost_price
        #                     total_cost = cost * qty
        #                     line_cost = line_cost - total_cost
        #                     # purchase_currency_id = p_line.order_id.pricelist_id.currency_id
        #                     p_line_cost = p_line.price_subtotal
        #                     purchase_price += p_line.price_subtotal
        #                     line_cost = line_cost + p_line_cost
        #         else:
        #             line_cost = line.price_included
        #             line_cost = float(line_cost * (50.0 / 100.0))
        #     # print "line_cost",line_cost
        #     line.actual_cost_price = line_cost
        #     line.purchase_qty = purchase_qty
        #     line.purchase_price = purchase_price

    # 'tax_included': fields.function(_amount_tax_included, string='Subtotal',
    #                                 digits_compute=dp.get_precision('Account')),
    #
    @api.depends(
        'sale_layout_cat_id'
    )
    def _get_cubit_service(self):
        for order in self:
            order.cubit_service = order.sale_layout_cat_id and order.sale_layout_cat_id.cubit_service or False

    def _set_cubit_service(self):
        pass

    #
    # @api.depends(
    #     'product_uom_qty',
    #     'list_price',
    #     'total_cost',
    #     'exclude_costprice',
    #     'is_cubit_service',
    #     # 'purchase_ids.state',
    #     # 'purchase_ids.order_id.state',
    #     # 'order_id.project_id.tasks.purchase_ids.order_line',
    #     # 'order_id.project_id.tasks.purchase_ids.order_line.price_subtotal',
    #     # 'order_id.project_id.tasks.purchase_ids.order_line.state',
    # )
    # def _compute_cost_price(self):
    #     purchase_qty = 0.0
    #     purchase_price = 0.0
    #     line_cost = 0.0
    #     if not self.exclude_costprice:
    #         if not self.is_cubit_service:
    #             line_cost = self.total_cost
    #             for p_line in self.purchase_ids:
    #                 if p_line.order_id.state not in ['cancel']:
    #                     p_line_qty = p_line.product_qty
    #                     purchase_qty += p_line_qty
    #                     o_line_qty = self.product_uom_qty
    #                     if p_line_qty <= o_line_qty:
    #                         qty = p_line_qty
    #                     else:
    #                         qty = o_line_qty
    #                     cost = self.cost_price
    #                     total_cost = cost * qty
    #                     line_cost = line_cost - total_cost
    #                     p_line_cost = p_line.price_subtotal
    #                     purchase_price += p_line.price_subtotal
    #                     line_cost = line_cost + p_line_cost
    #         else:
    #             line_cost = self.price_included
    #             line_cost = float(line_cost * (50.0 / 100.0))
    #     self.actual_cost_price = line_cost
    #     self.purchase_qty = purchase_qty
    #     self.purchase_price = purchase_price
    #
    # def _product_margin(self):
    #
    #     for line in self:
    #         if line.product_id:
    #             tmp_margin = line.price_subtotal - (
    #                         (line.purchase_price or line.product_id.standard_price) * line.product_uos_qty)
    #             line.margin = tmp_margin
    #     return
    #
    # # 'purchase_ids': fields.one2many('purchase.order.line', 'sale_line_id', 'Purchases'),
    # # 'task_delivery_line_ids': fields.one2many('task.delivery.line', 'deliv_sale_line_id', 'Delivery Lines'),
    #
    # # 'c_deliv_red': fields.function(_determine_deliv_blue, string='Delivery Red'),
    # # 'c_deliv_orange': fields.function(_determine_deliv_orange, string='Delivery Orange'),
    # # 'c_deliv_blue': fields.function(_determine_deliv_blue, string='Delivery Blue'),
    #
    @api.depends('list_price', 'supplier_discount', 'tax', 'margin', 'currency_rate', 'customer_discount')
    def _amount_price_unit(self):

        for line in self:
            list_price = line.list_price
            supplier_discount = line.supplier_discount
            tax = line.tax
            margin = line.margin
            currency_rate = line.currency_rate
            customer_discount = line.customer_discount
            price = (((list_price - (list_price * supplier_discount / 100)) + (
                    list_price - (list_price * supplier_discount / 100)) * tax / 100) * currency_rate) / (
                            (100 - margin) / 100)
            price = price - customer_discount
            decimal.getcontext().rounding = decimal.ROUND_HALF_UP
            rounded_value = int(decimal.Decimal(price).to_integral_value())
            line.unit_price = rounded_value
            # line.unit_price = round(price, 0)
            # res[line.id] = round(price, 0)
            # res[line.id] = price
        return

    @api.depends('list_price', 'supplier_discount', 'tax', 'margin', 'currency_rate', 'customer_discount')
    def _amount_cost_price(self):
        for line in self:
            list_price = line.list_price
            supplier_discount = line.supplier_discount
            tax = line.tax
            margin = line.margin
            currency_rate = line.currency_rate
            customer_discount = line.customer_discount
            price = (((list_price - (list_price * supplier_discount / 100)) + (
                    list_price - (list_price * supplier_discount / 100)) * tax / 100) * currency_rate)
            line.cost_price = round(price, 6)
        return

    @api.depends('list_price', 'product_uom_qty', 'supplier_discount', 'tax', 'margin', 'currency_rate',
                 'customer_discount', 'tax_id','cost_price')
    def _amount_total_cost(self):
        for line in self:
            product_uom_qty = line.product_uom_qty
            list_price = line.list_price
            supplier_discount = line.supplier_discount
            tax = line.tax
            margin = line.margin
            currency_rate = line.currency_rate
            customer_discount = line.customer_discount
            # price = (((list_price - (list_price * supplier_discount / 100)) + (
            #         list_price - (list_price * supplier_discount / 100)) * tax / 100) * currency_rate)
            total_cost = line.cost_price * product_uom_qty
            # decimal.getcontext().rounding = decimal.ROUND_HALF_UP
            # rounded_value = int(decimal.Decimal(total_cost).to_integral_value())
            # total_cost = rounded_value
            # line.total_cost = round(total_cost, 6)
            line.total_cost = total_cost
        return

    def _calc_line_quantity(self, line):
        return line.product_uom_qty

    @api.depends('tax_id', 'unit_price', 'product_uom_qty', 'order_id.currency_id', 'tax_id')
    def _amount_line_tax_cub(self, line):
        tax = 0.0
        qty = self._calc_line_quantity(line)
        price = line.unit_price
        order = line.order_id
        if line.tax_id:
            for c in \
            line.tax_id.compute_all(price, order.currency_id, line.product_uom_qty, False, line.order_id.partner_id)[
                'taxes']:
                tax += c.get('amount', 0.0)
        # if line.tax_id:
        # # res = self.taxes_id.compute_all(price, product=self, partner=self.env['res.partner'])
        #     taxes = line.tax_id._origin.compute_all(price, order.currency_id, line.product_uom_qty,
        #                                              False, partner=order.partner_shipping_id)
        #     tax = taxes['total_included']

        # for c in self.env['account.tax'].compute_all(line.tax_id, line.unit_price, qty, False,line.order_id.partner_id)['taxes']:
        #     tax += c.get('amount', 0.0)
        return tax

    #

    @api.depends('list_price', 'product_uom_qty', 'round_discount', 'supplier_discount', 'tax', 'margin',
                 'currency_rate', 'customer_discount')
    def _amount_line_included(self):
        for line in self:
            list_price = line.list_price
            supplier_discount = line.supplier_discount
            tax = line.tax
            margin = line.margin
            currency_rate = line.currency_rate
            product_uom_qty = line.product_uom_qty
            customer_discount = line.customer_discount
            round_discount = line.round_discount
            price = (((list_price - (list_price * supplier_discount / 100)) + (
                    list_price - (list_price * supplier_discount / 100)) * tax / 100) * currency_rate) / (
                            (100 - margin) / 100)
            price = price - customer_discount

            decimal.getcontext().rounding = decimal.ROUND_HALF_UP
            rounded_value = int(decimal.Decimal(price).to_integral_value())
            price = rounded_value

            # price = round(price, 0)
            total = price * product_uom_qty
            total = total - round_discount
            line.price_included = round(total, 6)
        return

    @api.depends('list_price', 'product_uom_qty', 'round_discount', 'supplier_discount', 'tax', 'margin', 'tax_id',
                 'currency_rate', 'customer_discount')
    def _amount_line_included_tax(self):
        for line in self:
            list_price = line.list_price
            supplier_discount = line.supplier_discount
            tax = line.tax
            margin = line.margin
            currency_rate = line.currency_rate
            product_uom_qty = line.product_uom_qty
            customer_discount = line.customer_discount
            round_discount = line.round_discount
            price = (((list_price - (list_price * supplier_discount / 100)) + (
                    list_price - (list_price * supplier_discount / 100)) * tax / 100) * currency_rate) / (
                            (100 - margin) / 100)
            price = price - customer_discount

            decimal.getcontext().rounding = decimal.ROUND_HALF_UP
            rounded_value = int(decimal.Decimal(price).to_integral_value())
            price = rounded_value

            # price = round(price, 0)
            total = price * product_uom_qty
            total = total - round_discount
            tax = self._amount_line_tax_cub(line)
            price_total_val = total + tax
            line.price_total_val = round(price_total_val, 6)
        return

    @api.depends('tax_id', 'unit_price', 'order_id.currency_id')
    # @api.depends('list_price', 'product_uom_qty', 'round_discount', 'supplier_discount', 'tax', 'margin', 'tax_id',
    #              'currency_rate', 'customer_discount')
    def _amount_line_tax(self):
        for line in self:
            tax = self._amount_line_tax_cub(line)
            line.tax_total = round(tax, 6)
        return

    # @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'order_id.add_tax')
    # def _compute_amount(self):
    #    res = super()._compute_amount()
    #    print(res, 3333333333333333333333333333333333333)
    #    res.order_id.onchange_add_tax()
    #    return res
