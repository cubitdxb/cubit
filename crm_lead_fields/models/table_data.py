# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime,date
from odoo.osv import expression


class OpportunityProductDetails(models.Model):
    _name = "opp.prod.details"
    _description = "Product Details"

    name = fields.Char(string='Name',required=True)
    cubit_prod_detail_id = fields.Integer(string="Cubit ID")
    active = fields.Boolean(default=True)


class QuotationValiduty(models.Model):
    _name = "quotation.validity"
    _description = "quotation Validity"

    name = fields.Char(string='Name')
    cubit_quotation_id = fields.Integer(string="Cubit ID")
    active = fields.Boolean(default=True)


class Delivery_terms(models.Model):
    _name = "delivery.terms"
    _description = "Delivery Terms"

    name = fields.Char(string='Name')
    cubit_delivery_id = fields.Integer(string="Cubit ID")
    active = fields.Boolean(default=True)


class PresaleInformation(models.Model):
    _name = "presale.information"
    _description = "Presale Information"

    # name = fields.Char(string='Name',required=True)
    presales_team = fields.Many2one('crm.team', string="Presales Team")
    presale_department_id = fields.Many2one('presale.department', string="Presales Department")
    presales_person = fields.Many2one('res.users', string="Presales Person")
    next_action_date = fields.Date(string="Next Action Date")
    available_date = fields.Date(string="Available Date")
    action_description = fields.Char(string="Action Description")
    comments = fields.Char(string="Comments")
    done = fields.Boolean(string="Done")
    crm_lead_id = fields.Many2one('crm.lead',string='Lead')
    sale_order_id = fields.Many2one('sale.order',string= 'Order')
    cubit_id = fields.Integer(string="Cubit ID")
    presale_boolean = fields.Boolean(string='Presale Visibility')
    sales_boolean = fields.Boolean(string='Sale Visibility')
    presale_status_id = fields.Many2one('presale.status',string='Presale Status')
    active = fields.Boolean(default=True)


    def action_salesperson_approval(self):
        for lead in self:
            # if lead.user_has_groups('crm_lead_fields.saleperson_approval'):
                # if lead.available_date:
            lead.next_action_date = lead.available_date
            lead.available_date = False


class VendorDetails(models.Model):
    _name = "vendor.details"
    _description = "Vendor Details"

    name = fields.Many2one('res.partner',domain="[('supplier', '=', True)]",string="Vendor")
    sale_line_brand = fields.Many2one('sale.line.brand', string="Vendor")
    distributor = fields.Many2one('res.partner',domain="[('supplier', '=', True)]",string="Distributor")
    account_manager = fields.Char(string="Vendor Account Manager")
    deal_id = fields.Char(string="Deal ID")
    dead_locking_status = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Deal Locking Status")
    crm_vendor_id = fields.Many2one('crm.lead',string='Lead')
    sale_order_id = fields.Many2one('sale.order',string= 'Order')
    cubit_id = fields.Integer(string="Cubit ID")
    active = fields.Boolean(default=True)



class sale_order_session_summary(models.Model):
    _name = "sale.order.section.summary"
    _description = "Sale order Summary"

    s_order_id = fields.Many2one('sale.order', string="Sale Order", ondelete="cascade")
    name = fields.Char('______Name______', size=25)
    sale_layout_cat_id = fields.Many2one('sale_layout.category', string='Section')
    total_cost = fields.Float('Total Cost')
    price_included = fields.Float('Subtotal')
    unit_price = fields.Float('Unit Price')
    vendor_id = fields.Many2one('res.partner', string='Vendor', domain="[('supplier', '=', True)]")

    cubit_sale_section_id = fields.Integer(string="Cubit ID")
    expected_time_of_arrival = fields.Date(string="Expected Date of Arrival")
    active = fields.Boolean(default=True)
    gross_profit = fields.Float(string="Gross Profit")
    gross_profit_perc = fields.Float(string="Gross Profit (%)")

    def _get_year_selection(self):
        current_year = date.today()
        year = current_year.year
        extended_year = year + 10
        y = []
        for i in range(year, extended_year):
            y.append((str(i), str(i)))
        return y

    expected_year_of_arrival = fields.Selection(selection=_get_year_selection,string="Expected year of Arrival")
    expected_week_of_arrival = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')],
                                                string='Expected Week of Arrival')
    expected_month_of_arrival = fields.Selection(
        [('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
         ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
         ('10', 'October'), ('11', 'November'), ('12', 'December')], string='Expected Month of Arrival')

    @api.onchange('expected_time_of_arrival',
                  'expected_year_of_arrival',
                  'expected_week_of_arrival',
                  'expected_month_of_arrival')
    def onchange_eta(self):
        template = self.env.ref('crm_lead_fields.mail_template_to_sales_person')
        for rec in self:
            # if rec.s_order_id.order_line.mapped('purchase_ids'):
            email_values = {'email_to': rec.s_order_id.user_id.email, 'recipient_ids':[]}
            if template:
                template.send_mail(rec.s_order_id.ids[0], force_send=True, email_values=email_values)



    # def unlink(self):
    #     update_session = self.env.context.get('update_session', False)
    #     if update_session == False:
    #         for order_session in self:
    #             sale_layout_cat_id = order_session.sale_layout_cat_id
    #             s_order_id = order_session.s_order_id
    #             self.env['sale.order.line'].search(
    #                 [('sale_layout_cat_id', '=', sale_layout_cat_id.id), ('order_id', '=', s_order_id.id), ]).unlink()
    #     return super(sale_order_session_summary, self).unlink()


class Sale_line_category(models.Model):
    _name = "sale.line.category"
    _description = "Sale line category"

    name = fields.Char(string='Name')
    cubit_line_category_id = fields.Integer(string="Cubit ID")
    active = fields.Boolean(default=True)

class Sale_line_brand(models.Model):
    _name = "sale.line.brand"
    _description = "Line brand"

    name = fields.Char(string='Name')
    cubit_line_brand_id = fields.Integer(string="Cubit ID")
    active = fields.Boolean(default=True)

class Sale_line_technology(models.Model):
    _name = "sale.line.technology"
    _description = "line Category"

    name = fields.Char(string='Name')
    cubit_line_technology_id = fields.Integer(string="Cubit ID")
    active = fields.Boolean(default=True)


class SaleLayoutCategory(models.Model):
    _name = 'sale_layout.category'
    _description = "Line category"
    _order = 'sequence, id'

    name = fields.Char('Name', required=True)
    sequence = fields.Integer('Sequence')
    subtotal = fields.Boolean('Add subtotal')
    separator = fields.Boolean('Add separator')
    pagebreak = fields.Boolean('Add pagebreak')
    cubit_service = fields.Boolean(string='Is a cubit service?',default=False)
    cubit_id = fields.Integer(string="Cubit ID")
    active = fields.Boolean(default=True)


class PresalesDepartment(models.Model):
    _name = 'presale.department'
    _description = "Presale Department"

    name = fields.Char('Name', required=True)
    sales_team_users = fields.Many2many('res.users', 'department_rel', 'presale_id', 'user_id', string='Users')

    @api.onchange('sales_team_users')
    def _domain_sale_team_users(self):
        pre_sales_users = self.env['crm.team'].search([('team_code', '=', 'pre_sales')]).mapped('member_ids').ids
        return {'domain': {'sales_team_users': [('id', 'in', pre_sales_users)]}}

    active = fields.Boolean(default=True)


class PresalesStataus(models.Model):
    _name = 'presale.status'
    _description = "Presale Status"

    name = fields.Char('Name', required=True)
    active = fields.Boolean(default=True)


class ProjectTerms(models.Model):
    _name = 'project.terms'

    name = fields.Char(string='Payment Term Products')
    active = fields.Boolean(default=True)


class ProjectPaymentTerms(models.Model):
    _name = 'project.payment.terms'

    # name = fields.Char(string='Payment Term Products')
    name = fields.Many2one( 'project.terms',string='Payment Term Products')
    percentage = fields.Float('Percentage')
    amount = fields.Float('Amount')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')
    sale_id = fields.Many2one('sale.order', string='Sale order')
    active = fields.Boolean(default=True)


class MSPTerms(models.Model):
    _name = 'msp.amc.terms'

    name = fields.Char(string='Payment Term MSP/AMC')
    active = fields.Boolean(default=True)

class MSPPaymentTerms(models.Model):
    _name = 'msp.amc.payment.terms'

    # name = fields.Char(string='Payment Term MSP/AMC')
    name = fields.Many2one('msp.amc.terms',string='Payment Term MSP/AMC')
    percentage = fields.Float('Percentage')
    amount = fields.Float('Amount')
    sale_id = fields.Many2one('sale.order', string='Sale order')
    active = fields.Boolean(default=True)












