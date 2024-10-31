# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError,RedirectWarning




class PaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    cubit_account_payment_term_id = fields.Integer(string="Cubit ID")


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    cubit_procurement_group_id = fields.Integer(string="Cubit ID")

class PartnerTitle(models.Model):
    _inherit = "res.partner.title"

    cubit_title_id = fields.Integer(string="Cubit ID")


class ResPartner(models.Model):
    _inherit = "res.partner"

    # _sql_constraints = [
    #     ('vat_uniq', 'unique(vat)', "This tax id is assigned to another customer !"),
    # ]

    is_financial_contact = fields.Boolean(string='Financial Contact')
    customer = fields.Boolean(string='Customer', help="Check this box if this contact is a customer.")
    supplier = fields.Boolean(string='Supplier',help="Check this box if this contact is a supplier. If it's not checked, "
                                              "purchase people will not see it when encoding a purchase order.")
    customer_contact = fields.Boolean(string='Customer Contact',compute="child_customer_supplier",recursive=True)
    supplier_contact = fields.Boolean(string='Supplier Contact',compute="child_customer_supplier",recursive=True)
    cubit_partner_id = fields.Integer(string="Cubit ID Value")
    cubit_parent_id = fields.Integer(string="Cubit ID")
    fax = fields.Char('Fax')
    company_size = fields.Integer(string="Size of Company")
    company_type = fields.Selection(string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company')])
    vat_certificate = fields.Binary(string="VAT certificate")
    passport_copy = fields.Binary(string="Passport copy")
    trade_license = fields.Binary(string="Trade license")


    # def write(self, vals):
    #     if not (vals.get('customer')==True or vals.get('supplier')==True):
    #         raise ValidationError(_("You have to choose a CheckBox Either Customer/Supplier"))
    #     if not (self.customer==True or self.supplier==True):
    #         raise ValidationError(_("You have to choose a CheckBox Either Customer/Supplier"))
    #     return super().write(vals)
    @api.depends('child_ids','customer_contact','supplier_contact','customer','supplier','child_ids.customer_contact',
                  'child_ids.supplier_contact','child_ids.supplier','child_ids.customer')
    def child_customer_supplier(self):
        for partner in self:
            partner.customer_contact = partner.customer
            partner.supplier_contact = partner.supplier
            for order in partner.child_ids:
                order.customer_contact = partner.customer
                order.supplier_contact = partner.supplier
                order.customer = partner.customer
                order.supplier = partner.supplier
                if not (order.customer_contact == True or order.supplier_contact == True) and order.type != 'existing_contact':
                    raise ValidationError(_("You have to choose a CheckBox Either Customer/Supplier"))





    # @api.constrains('child_ids','parent_id.customer','parent_id.supplier','customer','customer')
    # def _check_child_ids_customer_supplier(self):
    #     for partner in self:
    #         if not (partner.customer==True or partner.supplier==True):
    #             raise ValidationError(_("You have to choose a CheckBox Either Customer/Supplier"))

# @api.onchange('customer','supplier')
    # def _check_customer_supplier(self):
    #     for partner in self:
    #         if partner.customer==True and partner.supplier==True:
    #             raise ValidationError(_("Select supplier or Customer"))
    #

    # @api.constrains("name",'phone','mobile','website','email','vat')
    # def _check_ref(self):
    #     if not self.env.user.has_group('contact_details_fields.allow_customer_duplication'):
    #         for partner in self.filtered("name"):
    #             if partner.name:
    #                 domain = [("id", "!=", partner.id),("name", "=ilike", partner.name),]
    #                 other = self.search(domain)
    #                 if other :
    #                     raise ValidationError(_("This Name Already Exist For the Customer '%s'")% other[0].display_name)
    #             if partner.phone:
    #                 domain = [("id", "!=", partner.id), ("phone", "=", partner.phone), ]
    #                 other = self.search(domain)
    #                 if other:
    #                     raise ValidationError(_("This Phone Number Already Exist For the Customer '%s'") % other[0].display_name)
    #
    #             if partner.mobile:
    #                 domain = [("id", "!=", partner.id), ("mobile", "=", partner.mobile), ]
    #                 other = self.search(domain)
    #                 if other:
    #                     raise ValidationError(_("This Mobile Number Already Exist For the Customer '%s'") % other[0].display_name)
    #             if partner.email:
    #                 domain = [("id", "!=", partner.id), ("email", "=", partner.email), ]
    #                 other = self.search(domain)
    #                 if other:
    #                     raise ValidationError(_("This E-mail Already Exist For the Customer '%s'") % other[0].display_name)
    #             if partner.website:
    #                 domain = [("id", "!=", partner.id), ("website", "=", partner.website), ]
    #                 other = self.search(domain)
    #                 if other:
    #                     raise ValidationError(_("This Website Already Exist For the Customer '%s'") % other[0].display_name)
    #
    #
                # if partner.vat:
                #     domain = [('id', '!=', partner.id), ('vat', '=', partner.vat)]
                #     other = self.search(domain)
                #     if other:
                #         raise ValidationError(_("This Tax ID Already Exist For another customer"))

    # @api.onchange('vat')
    # def vat_validation(self):
    #     if not self.env.user.has_group('contact_details_fields.allow_customer_duplication'):
    #         if self.vat:
    #             partner_vat = self.env['res.partner'].search([('vat', '=', self.vat)]).ids
    #             if len(partner_vat) > 1:
    #                 raise ValidationError(_('This Tax ID Already Exist For another customer'))

    @api.model
    def default_get(self, fields):
        result = super(ResPartner, self).default_get(fields)
        uid = self.env.user
        # if self.env.ref("contacts.action_contacts"):
        if not self.user_id:
            result.update({
                'user_id': uid.id
            })
        return result


    # def sale_remark_wizard_button(self):
    #     action = self.env["ir.actions.actions"]._for_xml_id('contact_details_fields.action_partner_vat_wizard')
    #     action['context'] = {'default_sale_id': self.id}
    #     return action

    # wizrd_action_id = self.env.ref('contact_details_fields.view_partner_vat_wizard')
    # msg = "Are You sure! "
    # raise RedirectWarning(msg, wizrd_action_id.id, _('Go to the wizard'),
    #                       {'active_id': self._origin.id, })


    @api.model
    def create(self, vals):
        if not self.env.user.has_group('contact_details_fields.allow_customer_duplication') and vals['type'] not in 'existing_contact':
            if vals.get('company_type')=='company':
                partner_name = self.env['res.partner'].search([('name', '=ilike', vals.get('name'))])
                partners_name = [i.name for i in partner_name]
                if partner_name:
                    raise ValidationError(_("This Name Already Exist For the Customer '%s'") % partners_name[0])
            partner_phone = self.env['res.partner'].search([('phone', '=ilike', vals.get('phone'))])
            partners_phone= [i.name for i in partner_phone]
            if partner_phone:
                raise ValidationError(
                        _("This Phone Number Already Exist For the Customer '%s'") % partners_phone[0])
            partner_mobile = self.env['res.partner'].search([('mobile', '=ilike', vals.get('mobile'))])
            partners_mobile = [i.name for i in partner_mobile]
            if partner_mobile:
                raise ValidationError(
                        _("This Mobile Number Already Exist For the Customer '%s'") % partners_mobile[0])
            partner_email = self.env['res.partner'].search([('email', '=ilike', vals.get('email'))])
            partners_email = [i.name for i in partner_email]
            if partner_email:
                raise ValidationError(
                    _("This E-mail Already Exist For the Customer '%s'") % partners_email[0])
            partner_website = self.env['res.partner'].search([('website', '=ilike', vals.get('website'))])
            partners_website = [i.name for i in partner_website]
            if partner_website:
                raise ValidationError(
                    _("This Website Already Exist For the Customer '%s'") % partners_website[0])
        return super(ResPartner, self).create(vals)
        # profile_view = self.env.ref("hr.res_partner_admin_private_address")
        # if self.env.ref("hr.res_partner_admin_private_address"):
        #     part = self.env['res.partner'].browse(self.env.ref("hr.res_partner_admin_private_address").id)
        #     part.unlink()
        # if vals.get('customer'):
        #     vals['customer'] = self._convert_tag_syntax_to_orm(vals['plus_report_line_ids'])
        # self.child_customer_supplier()
#        if not (vals.get('customer')==True or vals.get('supplier')==True or self.env.context.get('flag_partner')==1):
 #           raise ValidationError(_("You have to choose a CheckBox Either Customer/Supplier"))
  #      if vals.get('company_type') == 'company' and not vals.get('vat_certificate'):
   #         raise ValidationError(_("Please attach Vat Certificate!"))
        # if not vals.get('passport_copy'):
        #     raise ValidationError(_("Please attach Passport copy!"))
    #    if vals.get('company_type') == 'company' and not vals.get('trade_license'):
    #        raise ValidationError(_("Please attach Trade License!"))
    #   if vals.get('company_type') == 'company' and not vals.get('child_ids'):
    #       raise ValidationError(_("Please add at least one contact!"))
    #   return super(ResPartner, self).create(vals)
    

    @api.onchange('user_id')
    def onchange_sales_person(self):
        if self.child_ids:
            for rec in self.child_ids:
                rec._origin.user_id = self.user_id.id

#
# class SaleOrder(models.Model):
#     _inherit = "sale.order"
#
#     def action_confirm(self):
#         res = super(SaleOrder, self).action_confirm()
#         if self.partner_id and self.partner_id.company_type=='person':
#             if self.partner_id.is_financial_contact != True:
#                 raise ValidationError(_('You Need to check the Financial Contact Before confirming the SO'))
#         return res
