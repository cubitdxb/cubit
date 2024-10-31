# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import datetime
from datetime import datetime,date
from odoo.exceptions import ValidationError,UserError
# odoo8

# AVAILABLE_PRIORITIES = [
#     ('0', 'Very Low'),
#     ('1', 'Low'),
#     ('2', 'Normal'),
#     ('3', 'High'),
#     ('4', 'Very High'),
# ]

# odoo15

AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]
from datetime import timedelta


class Lead(models.Model):
    _inherit = "crm.lead"

    is_lost = fields.Boolean(string="Is Lost?",default=False)

    partner_id = fields.Many2one(
        'res.partner', string='Customer', check_company=True, index=True, tracking=10,
        domain="[('customer','=',True),'|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")

    cubit_crm_id = fields.Integer(string="Cubit ID")

    type = fields.Selection(selection_add=[('both', 'Both')],ondelete={'both': 'cascade'})

    sel_probability = fields.Selection([('100', '100'), ('80', '80'), ('50', '50'), ], 'Success Rate (%)')
    fax = fields.Char('Fax')
    priority = fields.Selection(AVAILABLE_PRIORITIES, 'Priority')

    competitor = fields.Char(string="Competitor")
    # category = fields.Char(string="Category")
    category = fields.Many2one('sale.line.category', string='Category')
    presales_required = fields.Boolean(string="Presales Required")
    imported_stage = fields.Boolean(string="Import File")
# connection link for the tables
    presale_id = fields.One2many('presale.information', 'crm_lead_id', 'Presales Information')
    vendor_detail_id = fields.One2many('vendor.details', 'crm_vendor_id', 'Vendor Details')
# opportunity fields
    contact_id = fields.Many2one('res.partner', string='Partner Contact', ondelete='set null')
    product_details = fields.Char(string='Product Details')
    vendor_details = fields.Many2one('opp.prod.details', 'Vendor/Product Details', ondelete='set null')
    date_action = fields.Date('Next Action Date')
    title_action = fields.Char(string='Next Action')
    expected_week_of_closing = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4')],string='Expected Week of closing')
    expected_month_of_closing = fields.Selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
            ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December')], string='Expected Month of closing')
    crm_vendor_id = fields.Many2one('crm.lead',string='Lead')
    order_ids = fields.One2many('sale.order', 'crm_lead_id', 'Orders')
    contact_person_id = fields.Many2one('res.partner', string='Contact Person')
    contact_person_boolean = fields.Boolean('contact person boolean')


    def action_new_quotation(self):
        res = super().action_new_quotation()
        res['context'].update({
            'search_default_crm_lead_id': self.id,
            'default_crm_lead_id': self.id,
        })
        return res
    # def action_new_quotation(self):
    #     action = self.env["ir.actions.actions"]._for_xml_id("sale_crm.sale_action_quotations_new")
    #     action['context'] = {
    #         'search_default_opportunity_id': self.id,
    #         'search_default_crm_lead_id': self.id,
    #         'default_opportunity_id': self.id,
    #         'default_crm_lead_id': self.id,
    #         'search_default_partner_id': self.partner_id.id,
    #         'default_partner_id': self.partner_id.id,
    #         'default_campaign_id': self.campaign_id.id,
    #         'default_medium_id': self.medium_id.id,
    #         'default_origin': self.name,
    #         'default_source_id': self.source_id.id,
    #         'default_company_id': self.company_id.id or self.env.company.id,
    #         'default_tag_ids': [(6, 0, self.tag_ids.ids)]
    #     }
    #     if self.team_id:
    #         action['context']['default_team_id'] = self.team_id.id,
    #     if self.user_id:
    #         action['context']['default_user_id'] = self.user_id.id
    #     return action

    # stages_readonly = fields.Boolean(string="Conditional Stages",compute='_stage_readonly_stages',store=True)
    #
    #
    # @api.depends('stage_id')
    # def _stage_readonly_stages(self):
    #     for lead in self:
    #         if lead.stage_id.name in ('Won','Lead','Quotation','Quotation Submitted'):
    #             lead.stages_readonly == True
    #         else:
    #             lead.stages_readonly == False

    @api.onchange('contact_person_id')
    @api.depends('contact_person_id')
    def _compute_email_from(self):
        for lead in self:
            if lead.contact_person_id.email:
                lead.email_from = lead.contact_person_id.email
            else:
                lead.email_from = False

    def _inverse_email_from(self):
        for lead in self:
            # if lead._get_partner_email_update():
            lead.contact_person_id.email = lead.email_from

    #

    @api.onchange('priority')
    def _onchange_priority(self):
        date = False
        for lead in self:
            no_of_days = [week.dayofweek for week in lead.company_id.resource_calendar_id.attendance_ids]
            actual_days = list(set(no_of_days))
            week_days = ['0','1','2','3','4','5','6']
            difference = [x for x in week_days if x not in actual_days]
            # difference =week_days - actual_days
            today = fields.Date.today()
            dd = [today + timedelta(days=x) for x in range(14) if (today + timedelta(days=x)).weekday() not in difference]
            # dd= dd.sort(reverse=True)
            if dd:
                if lead.priority == '0':
                    # date = today + timedelta(days=1)
                    date = dd[1]
                if lead.priority == '1':
                    date = dd[3]
                if lead.priority == '2':
                    date = dd[5]
                if lead.priority == '3':
                    date = dd[7]
            for presale in lead.presale_id:
                presale.next_action_date = date









    def action_set_lost(self, **additional_values):
        res = super().action_set_lost(**additional_values)
        lead_stage_ids = self.env['crm.stage'].search([('is_lost', '=', True)]).ids
        for lead in self:
            if lead_stage_ids:
                lead.stage_id = lead_stage_ids[0]
                lead.write({'stage_id': lead_stage_ids[0]})
        return res

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #
    #     domain += [('stage_id.name', 'in', ('Won','Lead','Quotation','Quotation Submitted'))]
    #
    #     res = super(Lead, self).search_read(domain, fields, offset, limit, order)
    #
    #     return res


    @api.model
    def default_get(self, fields):
        result = super(Lead, self).default_get(fields)
        active_ids = self.env.context.get('active_id')
        active_ids = active_ids or False
        if self.env.context.get('active_id'):
            crm_lead = self.env['crm.lead'].browse(active_ids)
            lead_stage_ids = self.env['crm.stage'].search([('is_lead', '=', True)]).ids
            for lead in crm_lead:
                if lead_stage_ids:
                    lead.stage_id = lead_stage_ids[0]
                    result['stage_id'] = lead_stage_ids[0]
        return result

    @api.model_create_multi
    def create(self, vals_list):
        leads = super(Lead, self).create(vals_list)
        lead_stage_ids = self.env['crm.stage'].search([('is_lead', '=', True)]).ids
        for lead in leads:
            if lead_stage_ids:
                lead.stage_id = lead_stage_ids[0]
        return leads


    def _get_year_selection(self):
        current_year = date.today()
        year = current_year.year
        extended_year = year + 10
        y = []
        for i in range(year, extended_year):
            y.append((str(i), str(i)))
        return y

    expected_year_of_closing = fields.Selection(selection=_get_year_selection,string='Expected year of closing')

    def action_view_sale_quotation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['context'] = {
            'search_default_draft': 1,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_opportunity_id': self.id
        }
        action['domain'] = ['|',('opportunity_id', '=', self.id),('crm_lead_id', '=', self.id), ('state', 'in', ['draft', 'sent'])]
        quotations = self.mapped('order_ids').filtered(lambda l: l.state in ('draft', 'sent'))
        if len(quotations) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = quotations.id
        return action

    def action_view_sale_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action['context'] = {
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_opportunity_id': self.id,
        }
        action['domain'] = ['|',('opportunity_id', '=', self.id),('crm_lead_id', '=', self.id),('state', 'not in', ('draft', 'sent', 'cancel'))]
        orders = self.mapped('order_ids').filtered(lambda l: l.state not in ('draft', 'sent', 'cancel'))
        if len(orders) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = orders.id
        return action


    def convert_to_opportunity(self):
        lead_stage_ids = self.env['crm.stage'].search([('is_opportunity', '=', True)]).ids
        for lead in self:
            lead.convert_opportunity(lead.partner_id.id, user_ids=False, team_id=False)
            if lead_stage_ids:
                lead.stage_id = lead_stage_ids[0]
            return lead.redirect_lead_opportunity_view()

        # return


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        uid = self.env.user
        partners = self.env['res.partner'].search([('user_id', '=', uid.id)]).ids
        if self.partner_id:
            if self.partner_id.id not in partners:
                raise ValidationError(_("Please choose customer assigned to you!"))
        if self.partner_id.child_ids:
            self.contact_person_boolean = True
        else:
            self.contact_person_boolean = False





class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'


    def action_apply(self):
        res = super().action_apply()
        lead_stage_ids = self.env['crm.stage'].search([('is_opportunity', '=', True)]).ids
        for lead in self.lead_id:
            if lead_stage_ids:
                lead.stage_id = lead_stage_ids[0]
        return res










