# -*- coding: utf-8 -*-
from odoo import fields,models,api,_
from odoo.exceptions import ValidationError,UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    disable_required_fields = fields.Boolean(string="Disable Required Field")

    trn_number = fields.Char(related='partner_id.vat')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        # if any(order.margin < 5 for order in self.order_line):
        #     raise ValidationError(_('It is not allowed to confirm an order when the margin is less than 5%'))
        if self.disable_required_fields != True:
            # if self.partner_id.company_type == 'company':
            if not self.partner_id.vat_certificate:
                raise ValidationError(_("Please attach Vat Certificate for Customer!"))
            if not self.partner_id.passport_copy:
                raise ValidationError(_("Please attach Passport copy for Customer!"))
            if not self.partner_id.trade_license:
                raise ValidationError(_("Please attach Trade License for Customer!"))
            if not self.partner_id.child_ids:
                raise ValidationError(_("Please add at least one contact for Customer!"))

            if not self.partner_id.email:
                raise ValidationError(_("Please Add E-mail for Customer"))
            if not self.partner_id.phone:
                raise ValidationError(_("Please Add Phone for Customer!"))
            if not self.partner_id.vat:
                raise ValidationError(_("Please Add VAT for Customer!"))
            if not self.partner_id.fax:
                raise ValidationError(_("Please add fax for Customer!"))
            if not self.partner_id.website:
                raise ValidationError(_("Please add Website for Customer!"))

            if len(self.vendor_detail_id) < 1:
                raise ValidationError(_('Fill the Vendor Details Before Confirming the Sale order'))
            if any((not order.sale_line_brand.name or not order.distributor or not order.account_manager
                    or not order.deal_id or not order.dead_locking_status) for order in self.vendor_detail_id):
                raise ValidationError(_('Fill the Vendor Details Before Confirming the Sale order'))
            if not (self.lpo_number or self.lpo_email == True):
                raise ValidationError(_('You Need to enter LPO Number/LPO Email Confirmation Before confirming the SO'))
            if self.lpo_number and not (self.lpo_doc):
                raise ValidationError(_('You Need to attach LPO document Before confirming the SO'))
            if self.lpo_email and not (self.lpo_email_attachment):
                raise ValidationError(_('You Need to attach LPO email confirmation document Before confirming the SO'))
            if self.planned_hours == 0.00:
                raise ValidationError(_('You Need to add Planned hours'))
            if len(self.section_line) >= 1:
                if any(not order.expected_time_of_arrival for order in self.section_line):
                    raise ValidationError(_('Fill the Expected Date of Arrival Before Confirming the Sale order'))

            # if not self.vat_certificate:
            #     raise ValidationError(_('You Need to Upload VAT certificate Before confirming the SO'))
            # if not self.passport_copy:
            #     raise ValidationError(_('You Need to Upload Passport copy Before confirming the SO'))
            # if not self.trade_license:
            #     raise ValidationError(_('You Need to Upload Trade license Before confirming the SO'))
            if any((not order.sale_layout_cat_id or not order.line_category_id or not order.line_brand_id
                    or not order.line_technology_id or not order.service_duration or not order.renewal_category
                    or not order.distributor) for order in self.order_line):
                raise ValidationError(_('You cannot confirm SO without Section/Category/'
                                        'Renewal Category/Service Duration Months/Brand/Technology/Distributor'))
            if any((order.sale_layout_cat_id == False or order.line_category_id == False or order.line_brand_id == False
                    or order.line_technology_id == False or order.service_duration == False
                    or order.renewal_category == False or order.distributor == False) for order in self.order_line):
                raise ValidationError(_('You cannot confirm SO without Section/Category/'
                                        'Renewal Category/Service Duration Months/Brand/Technology/Distributor'))
            if not self.trn_number:
                raise ValidationError(_('You cannot confirm SO without TRN Number'))
            for order in self:
                crm_lead = self.env['crm.lead'].browse(order.crm_lead_id.id)
                lead_stage_ids = self.env['crm.stage'].search([('is_sale_order', '=', True)]).ids
                for lead in crm_lead:
                    if lead_stage_ids:
                        lead.stage_id = lead_stage_ids[0]
                        lead.write({'stage_id': lead_stage_ids[0]})
            if (self.partner_contact and self.partner_contact.company_type == 'person') or (self.partner_id and self.partner_id.company_type == 'person'):
                if self.partner_contact:
                    if self.partner_contact.is_financial_contact != True and self.partner_contact.company_type == 'person':
                        raise ValidationError(_('You Need to check the Financial Contact Before confirming the SO'))
                if self.partner_id.is_financial_contact != True and self.partner_id.company_type == 'person':
                    raise ValidationError(_('You Need to check the Financial Contact Before confirming the SO'))
        return res

class ResPartner(models.Model):
    _inherit = "res.partner"

    disable_required_fields = fields.Boolean(string="Disable Required Field")

    @api.model
    def create(self, vals):
        if vals.get('disable_required_fields') != True:
            if not (vals.get('customer') == True or vals.get('supplier') == True or self.env.context.get(
                    'flag_partner') == 1 or vals.get('type') == 'existing_contact'):
                raise ValidationError(_("You have to choose a CheckBox Either Customer/Supplier"))
            # if vals.get('company_type') == 'company' and not vals.get('vat_certificate'):
            #     raise ValidationError(_("Please attach Vat Certificate!"))
            # # if not vals.get('passport_copy'):
            # #     raise ValidationError(_("Please attach Passport copy!"))
            # if vals.get('company_type') == 'company' and not vals.get('trade_license'):
            #     raise ValidationError(_("Please attach Trade License!"))
            # if vals.get('company_type') == 'company' and not vals.get('child_ids'):
            #     raise ValidationError(_("Please add at least one contact!"))
        return super(ResPartner, self).create(vals)


class CRMlead(models.Model):
    _inherit = "crm.lead"

    disable_required_fields = fields.Boolean(string="Disable Required Field")


class ProjectProject(models.Model):
    _inherit = 'project.project'

    disable_required_fields = fields.Boolean(string="Disable Required Field")

#
# class Projecttask(models.Model):
#     _inherit = 'project.task'
#
#     disable_required_fields = fields.Boolean(string="Disable Required Field")



class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    disable_required_fields = fields.Boolean(string="Disable Required Field")

    @api.onchange('disable_required_fields')
    def disable_required_fields_onchange(self):
        for order in self:
            if order.disable_required_fields:
                order.awaiting_eta = True


class AccountMove(models.Model):
    _inherit = "account.move"

    disable_required_fields = fields.Boolean(string="Disable Required Field")

    def move_confirm_wizard_button(self):
        for moves in self:
            if not moves.lpo_number and moves.disable_required_fields==False:
                raise ValidationError(_('LPO Number Is Required'))
        res = super(AccountMove, self).move_confirm_wizard_button()
        return res
