# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID,_
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class Lead(models.Model):
    _inherit = "crm.lead"

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(Lead, self).fields_view_get(
    #         view_id=view_id, view_type=view_type, toolbar=toolbar,
    #         submenu=submenu)
    #     self._context.get('active_id')
    #     active_id = self.env.context.get('active_id')
    #     if view_type == 'form':
    #         for lead in self.browse(active_id):
    #             lead.presale_id.presale_information()
    #     return res
    #
    # @api.model
    # def default_get(self, fields_list):
    #     # only 'code' state is supported for cron job so set it as default
    #     self.presale_id.presale_information()
    #     return super(Lead, self).default_get(fields_list)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        uid = self.env.user
        # partners = self.env['res.partner'].search(['|',('user_id', '=', uid.id),('sales_team_users', 'in', uid.ids)]).ids
        partners = self.env['res.partner'].search(['|','|','|','|','|',('user_id', '=', uid.id),('sales_team_users', 'in', uid.ids),
                     ('renewal_team_users', 'in', uid.ids),('amc_team_users', 'in', uid.ids),
                     ('msp_team_users', 'in', uid.ids),('cisco_team_users', 'in', uid.ids)]).ids
        if self.partner_id:
            if self.partner_id.id not in partners:
                raise ValidationError(_("Please choose customer assigned to you!"))
        if self.partner_id.child_ids:
            self.contact_person_boolean = True
        else:
            self.contact_person_boolean = False

    def _get_user_doamin(self):
        # lead_group = self.env.ref('sales_team.group_sale_salesman_all_leads')
        lead_group = self.env.ref('vox_user_groups.group_sale_salesman_level_2_user')
        admin_group = self.env.ref('vox_user_groups.group_sale_salesman_level_1_user')
        # admin_group = self.env.ref('sales_team.group_sale_manager')
        if admin_group in self.env.user.groups_id:
            return False
        if admin_group not in self.env.user.groups_id and lead_group in self.env.user.groups_id:
            return str(['|', ('member_ids', '=', self.env.user.id), ('leader_ids', '=', self.env.user.id)])
        else:
            return str([('member_ids', '=', self.env.user.id)])

    user_ids = fields.Many2many('res.users', string="Assigned Users",
                                default=lambda self: self.env.user.ids,
                                domain="['&', ('share', '=', False), ('company_ids', 'in', user_company_ids)]",
                                check_company=True, index=True, track_visibility='always')
    team_ids = fields.Many2many('crm.team', string="Assigned Teams",
                                domain=_get_user_doamin, track_visibility='always')


    def _user_ids_domain(self):
        users=[]
        lead_users = self.env['crm.team'].search(['|',('team_code','=','sales_team'),('team_code','=','sales_coordinator')])
        for team_users in lead_users:
            users+=team_users.leader_ids.ids
            users+=team_users.member_ids.ids
        return [('id', 'in', users)]

    user_id = fields.Many2one( domain=_user_ids_domain)
        # 'res.users', string='Salesperson', default=lambda self: self.env.user,
        # domain=_user_ids_domain,
        # check_company=True, index=True, tracking=True)


    def _cron_lead_users_teams(self):
        leads = self.env['crm.lead'].search([])
        for lead in leads:
            presale_list = []
            team_list = []
            for presale in lead.presale_id:
                if presale.presales_person:
                    presale_list.append(presale.presales_person.id if presale.presales_person else 0)
                if presale.presales_team.id not in team_list:
                    if presale.presales_team:
                        team_list.append(presale.presales_team.id if presale.presales_team else 0)
            lead.user_ids = [(6, 0, lead.user_id.ids + presale_list)]
            lead.team_ids = [(6, 0, lead.team_id.ids + team_list)]


    @api.onchange('user_id', 'presale_id','team_id')
    def _onchange_user_id(self):
        for lead in self:
            presale_list = []
            team_list = []
            for presale in lead.presale_id:
                if presale.presales_person:
                    presale_list.append(presale.presales_person.id if presale.presales_person else 0)
                if presale.presales_team.id not in team_list:
                    if presale.presales_team:
                        team_list.append(presale.presales_team.id if presale.presales_team else 0)
            lead.user_ids = [(6, 0, lead.user_id.ids + presale_list + lead.user_id.sales_team_users.ids)]
            lead.team_ids = [(6, 0, lead.team_id.ids + team_list)]

    # @api.depends('user_ids','presale_id.presales_person')
    @api.onchange('user_ids', 'presale_id')
    def get_assigned_team_ids(self):
        for lead in self:
            if lead.user_ids:
                users = lead.user_ids
                teams = self.env['crm.team']
                leaders = self.env['res.users']
                report_leaders = self.env['res.users']
                team_domain = [('use_leads', '=', True)] if lead.type == 'lead' else [('use_opportunities', '=', True)]
                for presale in lead.presale_id:
                    if presale.presales_team:
                        team = self.env['crm.team'].browse(presale.presales_team.id)
                        if team:
                            teams += team
                for user in users:
                    team = self.env['crm.team']._get_default_team_id_new(user_id=user._origin.id, domain=team_domain)
                    if team:
                        teams += team

                lead.team_ids = teams.ids

            else:
                lead.team_ids = False

    def write(self, vals):

        activity_type_approval_id = self.env.ref('sales_team.team_sales_department').id
        if self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id:
            res = super().write(vals)
            return res
        else:
            if self.env.user.has_group('vox_user_groups.group_presale_users'):
                if vals.get('presale_id'):
                    for sales in vals.get('presale_id'):
                        if sales[2]:
                            if sales[2].get('available_date',False) or sales[2].get('done',False) \
                                    or sales[2].get('presale_status_id',False) or sales[2].get('comments',False):
                                return super().write(vals)
                            else:
                                raise ValidationError("Invalid Sales Team")

                else:
                    raise ValidationError("Invalid Sales Team")
            if 'team_id' in vals:
                teams = self.env['crm.team'].browse(vals.get('team_id'))
                # if vals['team_id'] != activity_type_approval_id:
                # if teams.team_code != 'sales_team':
                if teams.team_code not in ['sales_team','sales_coordinator']:
                    raise ValidationError("Invalid Sales Team")
            # elif self.team_id.id != activity_type_approval_id:
            # elif self.team_id.team_code != 'sales_team':
            elif self.team_id.team_code not in ['sales_team','sales_coordinator']:
                raise ValidationError("Invalid Sales Team")
        # self.access_compute_level_users()
        return super().write(vals)

    def unlink(self):
        activity_type_approval_id = self.env.ref('sales_team.team_sales_department').id
        if self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id:
            return super(Lead, self).unlink()
        else:
            # if self.team_id.id != activity_type_approval_id:
            # if self.team_id.team_code != 'sales_team':
            if self.team_id.team_code not in ['sales_team','sales_coordinator']:
                raise ValidationError("Invalid Sales Team")
        return super(Lead, self).unlink()


class saleOrder(models.Model):
    _inherit = "sale.order"

    can_view_all_orders = fields.Boolean(compute='_compute_can_view_all_orders')

    @api.depends('team_id')
    def _compute_can_view_all_orders(self):
        user = self.env.user
        for order in self:
            if user in self.env['crm.team'].search([('team_code', '=', 'procurement')]).mapped('member_ids'):
                order.can_view_all_orders = True
            else:
                order.can_view_all_orders = False

    @api.onchange('partner_id')
    def change_partner_tax(self):
        res = super(saleOrder,self).change_partner_tax()
        uid = self.env.user
        partners = self.env['res.partner'].search(
            ['|', '|', '|', '|', '|', ('user_id', '=', uid.id), ('sales_team_users', 'in', uid.ids),
             ('renewal_team_users', 'in', uid.ids), ('amc_team_users', 'in', uid.ids),
             ('msp_team_users', 'in', uid.ids), ('cisco_team_users', 'in', uid.ids)]).ids
        for rec in self:
            if rec.partner_id:
                rec.partner_contact = False
                if rec.partner_id.id not in partners:
                    raise ValidationError(_("Please choose customer assigned to you!"))
                if rec.partner_id.vat:
                    rec.trn_number = rec.partner_id.vat
                else:
                    rec.trn_number = False
        return res



    def _cron_lead_users_teams(self):
        sale_order= self.env['sale.order'].search([])
        for sale in sale_order:
            presale_list = []
            team_list = []
            if sale.crm_lead_id:
                for crm_lead in sale.crm_lead_id:
                    for presale in crm_lead.presale_id:
                        if presale.presales_person:
                            presale_list.append(presale.presales_person.id if presale.presales_person else 0)
                        if presale.presales_team.id not in team_list:
                            if presale.presales_team:
                                team_list.append(presale.presales_team.id if presale.presales_team else 0)
            sale.user_ids = [(6, 0, sale.user_id.ids + presale_list + sale.user_id.sales_team_users.ids)]
            sale.team_ids = [(6, 0, sale.team_id.ids + team_list)]


    def _get_user_doamin(self):
        # lead_group = self.env.ref('sales_team.group_sale_salesman_all_leads')
        lead_group = self.env.ref('vox_user_groups.group_sale_salesman_level_2_user')
        admin_group = self.env.ref('vox_user_groups.group_sale_salesman_level_1_user')
        # admin_group = self.env.ref('sales_team.group_sale_manager')
        if admin_group in self.env.user.groups_id:
            return False
        if admin_group not in self.env.user.groups_id and lead_group in self.env.user.groups_id:
            return str(['|', ('member_ids', '=', self.env.user.id), ('leader_ids', '=', self.env.user.id)])
        else:
            return str([('member_ids', '=', self.env.user.id)])

    user_ids = fields.Many2many('res.users', string="Assigned Users",
                                default=lambda self: self.env.user.ids,
                                domain=lambda
                                    self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
                                    self.env.ref("sales_team.group_sale_salesman").id
                                ),
                                check_company=True, index=True, track_visibility='always')
    team_ids = fields.Many2many('crm.team', string="Assigned Teams", store=True, readonly=False,
                                domain=_get_user_doamin, track_visibility='always')


    @api.onchange('user_id', 'presale_id','team_id')
    def _onchange_user_id(self):
        for lead in self:
            presale_list = []
            team_list = []
            for presale in lead.presale_id:
                if presale.presales_person:
                    presale_list.append(presale.presales_person.id if presale.presales_person else 0)
                if presale.presales_team.id not in team_list:
                    if presale.presales_team:
                        team_list.append(presale.presales_team.id if presale.presales_team else 0)
            lead.user_ids = [(6, 0, lead.user_id.ids + presale_list + lead.user_id.sales_team_users.ids)]
            lead.team_ids = [(6, 0, lead.team_id.ids + team_list)]


    def action_confirm(self):
        res = super(saleOrder, self).action_confirm()
        teams = self.env['crm.team']
        uid = self.env.user
        for line in self:
            if any(order.renewal_category=='renewal' for order in self.order_line):
                renewal_team = teams.search([('sale_team_code', '=', 'renewal')])
                for sale_renewals in renewal_team:
                    for sale_renewal in sale_renewals.member_ids:
                        line.write({'user_ids': [(4, sale_renewal.id)]})
                        line.partner_id.write({'renewal_team_users': [(4, sale_renewal.id)]})
            if any(order.line_category_id.category_selection=='amc' for order in self.order_line):
                amc_team = teams.search([('sale_team_code', '=', 'amc')])
                for sale_amc in amc_team:
                    for sale_a in sale_amc.member_ids:
                        line.write({'user_ids': [(4, sale_a.id)]})
                        line.partner_id.write({'amc_team_users': [(4, sale_a.id)]})
            if any(order.line_category_id.category_selection=='msp' for order in self.order_line):
                msp_team = teams.search([('sale_team_code', '=', 'msp')])
                for sale_msp in msp_team:
                    for sale_m in sale_msp.member_ids:
                        line.write({'user_ids': [(4, sale_m.id)]})
                        line.partner_id.write({'msp_team_users': [(4, sale_m.id)]})
            if any(order.line_brand_id.cisco_brand == True for order in self.order_line):
                cisco_team = teams.search([('sale_team_code', '=', 'cisco')])
                for sale_cisco in cisco_team:
                    for sale_c in sale_cisco.member_ids:
                        line.write({'user_ids': [(4, sale_c.id)]})
                        line.partner_id.write({'cisco_team_users': [(4, sale_c.id)]})
        return res

    # @api.depends('user_ids','presale_id.presales_person')
    @api.onchange('user_ids', 'presale_id')
    def get_assigned_team_ids(self):
        for lead in self:
            if lead.user_ids:
                users = lead.user_ids
                teams = self.env['crm.team']
                leaders = self.env['res.users']
                report_leaders = self.env['res.users']
                # team_domain = [('use_leads', '=', True)] if lead.type == 'lead' else [('use_opportunities', '=', True)]
                team_domain = []
                for presale in lead.presale_id:
                    if presale.presales_team:
                        team = self.env['crm.team'].browse(presale.presales_team.id)
                        if team:
                            teams += team
                for user in users:
                    team = self.env['crm.team']._get_default_team_id_new(user_id=user._origin.id, domain=team_domain)
                    if team:
                        teams += team

                lead.team_ids = teams.ids

            else:
                lead.team_ids = False

    def write(self, vals):

        activity_type_approval_id = self.env.ref('sales_team.team_sales_department').id
        if self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id:
            res = super().write(vals)
            return res
        else:
            if self.env.user.has_group('vox_user_groups.group_presale_users'):
                if vals.get('presale_id'):
                    for sales in vals.get('presale_id'):
                        if sales[2]:
                            if sales[2].get('available_date',False) or sales[2].get('done',False) \
                                    or sales[2].get('presale_status_id',False) or sales[2].get('comments',False):
                                return super().write(vals)
                            else:
                                raise ValidationError("Invalid Sales Team")

                else:
                    raise ValidationError("Invalid Sales Team")
                # raise ValidationError("Invalid Sales Team")
            member_ids = []
            member_ids+=self.user_ids.ids
            member_ids += self.team_ids.mapped('member_ids').ids
            member_ids += self.env['crm.team'].search(['|', '|', ('team_code', '=', 'procurement'), ('team_code', '=', 'project'), ('team_code', '=', 'finance')]).member_ids.ids
            member_ids += self.env['crm.team'].search(['|', '|', ('team_code', '=', 'procurement'), ('team_code', '=', 'project'), ('team_code', '=', 'finance')]).leader_ids.ids
            _logger.info('members           %s', member_ids)
            print(member_ids, 11111111111222222222222222222222)
            if self.env.uid not in member_ids:
                raise ValidationError(_("You can't edit sale Order/Quotation, Please contact administrator"))
            if 'team_id' in vals:
                teams = self.env['crm.team'].browse(vals.get('team_id'))
                # if vals['team_id'] != activity_type_approval_id:
                if teams.team_code not in ['sales_team','sales_coordinator']:
                    # if vals['team_id'] != activity_type_approval_id:
                    raise ValidationError("Invalid Sales Team")
            # elif self.team_id.team_code != 'sales_team':
            elif self.team_id.team_code not in ['sales_team','sales_coordinator']:
                raise ValidationError("Invalid Sales Team")
        return super().write(vals)

    def unlink(self):
        activity_type_approval_id = self.env.ref('sales_team.team_sales_department').id
        if self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id:
            return super(saleOrder, self).unlink()
        else:
            # if self.team_id.team_code != 'sales_team':
            if self.team_id.team_code not in ['sales_team','sales_coordinator']:
                raise ValidationError("Invalid Sales Team")
        return super(saleOrder, self).unlink()


class CreateSaleProject(models.TransientModel):
    _inherit = 'project.create.wizard'

    def _get_project_team(self):
        team_count = self.env['crm.team'].search_count([('team_code', '=', 'project')])
        if team_count:
            if team_count > 1:
                return
            else:
                return self.env['crm.team'].search([('team_code', '=', 'project')]).id
        else:
            return

    def _get_procurement_team(self):
        team_count = self.env['crm.team'].search_count([('team_code', '=', 'procurement')])
        if team_count:
            if team_count > 1:
                return
            else:
                return self.env['crm.team'].search([('team_code', '=', 'procurement')]).id
        else:
            return

    def _get_finance_team(self):
        team_count = self.env['crm.team'].search_count([('team_code', '=', 'finance')])
        if team_count:
            if team_count > 1:
                return
            else:
                return self.env['crm.team'].search([('team_code', '=', 'finance')]).id
        else:
            return

    project_team_id = fields.Many2one('crm.team', 'Project Team', ondelete="cascade",
                                      domain="[('team_code', '=', 'project')]", default=_get_project_team)
    procurement_team_id = fields.Many2one('crm.team', 'Procurement Team', ondelete="cascade",
                                          domain="[('team_code', '=', 'procurement')]", default=_get_procurement_team)
    finance_team_id = fields.Many2one('crm.team', 'Finance Team', ondelete="cascade",
                                      domain="[('team_code', '=', 'finance')]", default=_get_finance_team)

    # self.write({'duplicate_beneficiaries_ids': [(4, bid) for bid in benf_ids]})

    # user_rel_id = (4, [course_ids])

    # write({'many2many_ids': [user_rel_id]})

    def create_project(self):

        if self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id:
            sale_id = self.env.context.get('active_id', False)
            sale_order_rec = self.env['sale.order'].browse(sale_id)

            for obj in self:
                project_obj = self.env['project.project'].browse(obj.project_id.id)
                project_id = self.env['project.project'].sudo().create({
                    'name': sale_order_rec.name,
                    'sale_id': sale_id,
                    'description': sale_order_rec.name,
                    'partner_id': sale_order_rec.partner_id and sale_order_rec.partner_id.id or False,
                    'state': 'draft',
                    'project_template': obj.project_id.id,
                    'planned_hours_for_l1': sale_order_rec.planned_hours_for_l1,
                    'planned_hours_for_l2': sale_order_rec.planned_hours_for_l2,
                    'planned_hours': sale_order_rec.planned_hours,
                    # 'planned_hours_for_l2': sale_order_rec.planned_hours_for_l2

                })
                line = []
                presale_lines = []
                sale_line = self.env['sale.order.line'].search([('order_id', '=', sale_order_rec.id)])
                for lines in sale_line:
                # for lines in sale_order_rec.order_line:
                    data = {
                        'sl_no': lines.sl_no,
                        'part_number': lines.part_number,
                        'project_id': project_id.id,
                        'product_uom_qty': lines.product_uom_qty,
                        'name': lines.name
                    }
                    line.append((0, 0, data))
                project_id.boq_ids = line

                for presale_line in sale_order_rec.presale_id:
                    data = {
                        'presales_team':  presale_line.presales_team.id or False,
                        'project_id': project_id.id,
                        'presale_department_id': presale_line.presale_department_id.id or False,
                        'presales_person': presale_line.presales_person.id or False
                    }
                    presale_lines.append((0,0,data))
                project_id.presale_information_ids = presale_lines
                task_boq_lines = []
                task_presale_informations = []
                for task in project_obj.task_ids:
                    user_rel_id = False
                    if task.name == 'Advance' or task.task_name == 'Advance':
                        advance_team = []
                        advance_team.append(obj.procurement_team_id.id if obj.procurement_team_id else 0)
                        advance_team.append(obj.finance_team_id.id if obj.finance_team_id else 0)
                        user_rel_id = [(4, bid) for bid in advance_team]

                    if task.name == 'PO to supplier' or task.task_name == 'Purchase':
                        advance_team = []
                        advance_team.append(obj.procurement_team_id.id if obj.procurement_team_id else 0)
                        user_rel_id = [(4, bid) for bid in advance_team]

                    if task.name == 'Technical team assignment' or task.task_name == 'Technical Team assignment':
                        advance_team = []
                        advance_team.append(obj.project_team_id.id if obj.project_team_id else 0)
                        user_rel_id = [(4, bid) for bid in advance_team]

                    if task.name == 'Internal kick off' or task.task_name == 'Internal Kickoff':
                        advance_team = []
                        advance_team.append(obj.project_team_id.id if obj.project_team_id else 0)
                        user_rel_id = [(4, bid) for bid in advance_team]

                    if task.name == 'External kickoff' or task.task_name == 'External Kickoff':
                        advance_team = []
                        advance_team.append(obj.project_team_id.id if obj.project_team_id else 0)
                        user_rel_id = [(4, bid) for bid in advance_team]

                    if task.name == 'Delivery to customer' or task.task_name == 'Delivery to customer':
                        advance_team = []
                        advance_team.append(obj.procurement_team_id.id if obj.procurement_team_id else 0)
                        advance_team.append(obj.finance_team_id.id if obj.finance_team_id else 0)
                        advance_team.append(obj.project_team_id.id if obj.project_team_id else 0)
                        user_rel_id = [(4, bid) for bid in advance_team]

                    if task.name == 'Training' or task.task_name == 'Training':
                        advance_team = []
                        advance_team.append(obj.project_team_id.id if obj.project_team_id else 0)
                        user_rel_id = [(4, bid) for bid in advance_team]

                    if task.name == 'Documentation' or task.task_name == 'Documentation':
                        advance_team = []
                        advance_team.append(obj.project_team_id.id if obj.project_team_id else 0)
                        user_rel_id = [(4, bid) for bid in advance_team]
                    if task.name == 'Project Signoff' or task.task_name == 'pso':
                        advance_team = []
                        advance_team.append(obj.project_team_id.id if obj.project_team_id else 0)
                        user_rel_id = [(4, bid) for bid in advance_team]
                    if task.name == 'RMA &amp; Repair form' or task.task_name == 'RMA and Repair':
                        advance_team = []
                        advance_team.append(obj.procurement_team_id.id if obj.procurement_team_id else 0)
                        user_rel_id = [(4, bid) for bid in advance_team]

                    for lines in sale_order_rec.order_line:
                        data = {
                            'sl_no': lines.sl_no,
                            'part_number': lines.part_number,
                            'product_uom_qty': lines.product_uom_qty,
                            'name': lines.name
                        }
                        if (0,0,data) not in task_boq_lines:
                            task_boq_lines.append((0, 0, data))

                    for presale_line in sale_order_rec.presale_id:
                        data = {
                            'presales_team': presale_line.presales_team.id or False,
                            'presale_department_id': presale_line.presale_department_id.id or False,
                            'presales_person': presale_line.presales_person.id or False
                        }
                        if (0,0,data) not in task_presale_informations:
                            task_presale_informations.append((0, 0, data))
                    self.env['project.task'].sudo().create({
                        'name': task.name,
                        'project_id': project_id.id,
                        'display_project_id': task.display_project_id.id,
                        'task_name': task.task_name,
                        'task_type': task.task_type,
                        'team_id': user_rel_id,
                        'planned_hours_for_l1': sale_order_rec.planned_hours_for_l1,
                        'planned_hours_for_l2': sale_order_rec.planned_hours_for_l2,
                        'boq_line_ids': task_boq_lines,
                        'presale_information_ids': task_presale_informations

                    })
                sale_order_rec.sudo().write({'project_created': True, 'project_id': project_id})
            return
            # return super(CreateSaleProject).create_project()
        else:
            teams = self.env['crm.team'].search([('team_code', '=', 'procurement'), '|',
                                                 ('leader_ids', 'in', [self.env.uid]),
                                                 ('member_ids', 'in', [self.env.uid]),
                                                 ])
            # ('level_one_employee_ids', 'in', [self.env.uid]),
            # ('level_two_employee_ids', 'in', [self.env.uid]),
            # ('level_three_employee_ids', 'in', [self.env.uid]),
            # ('level_four_employee_ids', 'in', [self.env.uid]),
            # ('level_five_employee_ids', 'in', [self.env.uid]),
            # ])
            # if self.env.uid not in procurement_users:
            if not teams:
                raise ValidationError("Invalid Sales Team")
        sale_id = self.env.context.get('active_id', False)
        sale_order_rec = self.env['sale.order'].browse(sale_id)

        for obj in self:
            project_obj = self.env['project.project'].browse(obj.project_id.id)
            project_id = self.env['project.project'].sudo().create({
                'name': sale_order_rec.name,
                'sale_id': sale_id,
                'description': sale_order_rec.name,
                'partner_id': sale_order_rec.partner_id and sale_order_rec.partner_id.id or False,
                'state': 'draft',
                'project_template': obj.project_id.id,
                'planned_hours_for_l1': sale_order_rec.planned_hours_for_l1,
                'planned_hours_for_l2': sale_order_rec.planned_hours_for_l2,
                'planned_hours': sale_order_rec.planned_hours,

            })
            user_rel_id = False
            line = []
            presale_lines = []
            for lines in sale_order_rec.order_line:
                data = {
                    'sl_no': lines.sl_no,
                    'part_number': lines.part_number,
                    'project_id': project_id.id,
                    'product_uom_qty': lines.product_uom_qty,
                    'name': lines.name
                }
                line.append((0, 0, data))
            project_id.boq_ids = line

            for presale_line in sale_order_rec.presale_id:
                data = {
                    'presales_team': presale_line.presales_team.id or False,
                    'project_id': project_id.id,
                    'presale_department_id': presale_line.presale_department_id.id or False,
                    'presales_person': presale_line.presales_person.id or False
                }
                presale_lines.append((0, 0, data))
            project_id.presale_information_ids = presale_lines
            task_boq_lines = []
            task_presale_informations = []
            for task in project_obj.task_ids:

                if task.name == 'Advance' or task.task_name == 'Advance':
                    advance_team = []
                    advance_team.append(obj.procurement_team_id.id if obj.procurement_team_id else 0)
                    advance_team.append(obj.finance_team_id.id if obj.finance_team_id else 0)
                    user_rel_id = [(4, bid) for bid in advance_team]

                if task.name == 'PO to supplier' or task.task_name == 'Purchase':
                    advance_team = []
                    advance_team.append(obj.procurement_team_id.id if obj.procurement_team_id else 0)
                    user_rel_id = [(4, bid) for bid in advance_team]

                if task.name == 'Technical team assignment' or task.task_name == 'Technical Team assignment':
                    advance_team = []
                    advance_team.append(obj.project_team_id.id if obj.project_team_id else 0)
                    user_rel_id = [(4, bid) for bid in advance_team]

                if task.name == 'Internal kick off' or task.task_name == 'Internal Kickoff':
                    advance_team = []
                    advance_team.append(obj.project_team_id.id if obj.project_team_id else 0)
                    user_rel_id = [(4, bid) for bid in advance_team]

                if task.name == 'External kickoff' or task.task_name == 'External Kickoff':
                    advance_team = []
                    advance_team.append(obj.project_team_id.id if obj.project_team_id else 0)
                    user_rel_id = [(4, bid) for bid in advance_team]

                if task.name == 'Delivery to customer' or task.task_name == 'Delivery to customer':
                    advance_team = []
                    advance_team.append(obj.procurement_team_id.id if obj.procurement_team_id else 0)
                    advance_team.append(obj.finance_team_id.id if obj.finance_team_id else 0)
                    advance_team.append(obj.project_team_id.id if obj.project_team_id else 0)
                    user_rel_id = [(4, bid) for bid in advance_team]

                if task.name == 'Training' or task.task_name == 'Training':
                    advance_team = []
                    advance_team.append(obj.project_team_id.id if obj.project_team_id else 0)
                    user_rel_id = [(4, bid) for bid in advance_team]

                if task.name == 'Documentation' or task.task_name == 'Documentation':
                    advance_team = []
                    advance_team.append(obj.project_team_id.id if obj.project_team_id else 0)
                    user_rel_id = [(4, bid) for bid in advance_team]
                if task.name == 'Project Signoff' or task.task_name == 'pso':
                    advance_team = []
                    advance_team.append(obj.project_team_id.id if obj.project_team_id else 0)
                    user_rel_id = [(4, bid) for bid in advance_team]
                if task.name == 'RMA &amp; Repair form' or task.task_name == 'RMA and Repair':
                    advance_team = []
                    advance_team.append(obj.procurement_team_id.id if obj.procurement_team_id else 0)
                    user_rel_id = [(4, bid) for bid in advance_team]
                for lines in sale_order_rec.order_line:
                    data = {
                        'sl_no': lines.sl_no,
                        'part_number': lines.part_number,
                        'product_uom_qty': lines.product_uom_qty,
                        'name': lines.name
                    }
                    if (0, 0, data) not in task_boq_lines:
                        task_boq_lines.append((0, 0, data))

                for presale_line in sale_order_rec.presale_id:
                    data = {
                        'presales_team': presale_line.presales_team.id or False,
                        'presale_department_id': presale_line.presale_department_id.id or False,
                        'presales_person': presale_line.presales_person.id or False
                    }
                    if (0, 0, data) not in task_presale_informations:
                        task_presale_informations.append((0, 0, data))
                self.env['project.task'].sudo().create({
                    'name': task.name,
                    'project_id': project_id.id,
                    'display_project_id': task.display_project_id.id,
                    'task_name': task.task_name,
                    'task_type': task.task_type,
                    'team_id': user_rel_id,
                    'planned_hours_for_l1': sale_order_rec.planned_hours_for_l1,
                    'planned_hours_for_l2': sale_order_rec.planned_hours_for_l2,
                    'boq_line_ids': task_boq_lines,
                    'presale_information_ids': task_presale_informations

                })
            sale_order_rec.sudo().write({'project_created': True, 'project_id': project_id})
        return


class SaleOrderImport(models.Model):
    _inherit = "sale.order.import"

    team_id = fields.Many2one('crm.team', 'Sales Team', ondelete="cascade")

    @api.model
    def _prepare_default_get(self, order):
        res = super()._prepare_default_get(order)
        res['team_id'] = order.team_id.id
        return res

    def make_sale_requset(self):
        activity_type_approval_id = self.env.ref('sales_team.team_sales_department').id
        if self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id:
            return super().make_sale_requset()
        else:

            # if self.team_id.team_code != 'sales_team':
            if self.team_id.team_code not in ['sales_team','sales_coordinator']:
                raise ValidationError("Invalid Sales Team")

            # if self.team_id.id != activity_type_approval_id:
            #     raise ValidationError("Invalid Sales Team")
        return super().make_sale_requset()


class ProjectTask(models.Model):
    _inherit = 'project.task'

    team_id = fields.Many2many('crm.team', string='Sales Team')

    def write(self, vals):

        # teams = self.env['crm.team'].search(
        #     ['|', '|', '|', '|', ('level_one_employee_ids', 'in', [self.env.uid, ]),
        #      ('level_two_employee_ids', 'in', [self.env.uid, ]),
        #      ('level_three_employee_ids', 'in', [self.env.uid, ]),
        #      ('level_four_employee_ids', 'in', [self.env.uid, ]),
        #      ('level_five_employee_ids', 'in', [self.env.uid])
        #      ])
        teams = self.env['crm.team'].search(
            ['|', ('leader_ids', 'in', [self.env.uid]), ('member_ids', 'in', [self.env.uid]), ])

        if self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id:
            return super().write(vals)
        else:
            if self.name == 'Advance' or self.task_name == 'Advance':
                teams.search([('team_code', 'in', ('procurement', 'finance'))])

                # if self.env.uid not in procurement_sales_users or self.env.uid not in finance_sales_users:
                if not teams.search([('team_code', 'in', ('procurement', 'finance'))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'PO to supplier' or self.task_name == 'Purchase':

                # if self.env.uid not in procurement_sales_users:
                if not teams.search([('team_code', 'in', ('procurement',))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'Technical team assignment' or self.task_name == 'Technical Team assignment':

                # if self.env.uid not in project_users:
                if not teams.search([('team_code', 'in', ('project',))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'Internal kick off' or self.task_name == 'Internal Kickoff':

                if not teams.search([('team_code', 'in', ('project',))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'External kickoff' or self.task_name == 'External Kickoff':

                if not teams.search([('team_code', 'in', ('project',))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'Delivery to customer' or self.task_name == 'Delivery to customer':

                # if self.env.uid not in procurement_sales_users:
                if not teams.search([('team_code', 'in', ('procurement','finance'))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'Training' or self.task_name == 'Training':

                if not teams.search([('team_code', 'in', ('project',))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'Documentation' or self.task_name == 'Documentation':

                if not teams.search([('team_code', 'in', ('project',))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'Project Signoff' or self.task_name == 'pso':

                if not teams.search([('team_code', 'in', ('project',))]):
                    raise ValidationError("Invalid Sales Team")
            if self.name == 'RMA &amp; Repair form' or self.task_name == 'RMA and Repair':

                if not teams.search([('team_code', 'in', ('procurement',))]):
                    raise ValidationError("Invalid Sales Team")
        return super().write(vals)

    def unlink(self):

        teams = self.env['crm.team'].search(
            ['|', ('leader_ids', 'in', [self.env.uid]), ('member_ids', 'in', [self.env.uid])
             ])
        if self.env.uid == self.env.ref('base.user_admin').id or self.env.uid == self.env.ref('base.user_root').id:
            return super(ProjectTask, self).unlink()
        else:

            if self.name == 'Advance' or self.task_name == 'Advance':

                if not teams.search([('team_code', 'in', ('procurement', 'finance'))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'PO to supplier' or self.task_name == 'Purchase':

                if not teams.search([('team_code', 'in', ('procurement',))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'Technical team assignment' or self.task_name == 'Technical Team assignment':

                if not teams.search([('team_code', 'in', ('project',))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'Internal kick off' or self.task_name == 'Internal Kickoff':

                if not teams.search([('team_code', 'in', ('project',))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'External kickoff' or self.task_name == 'External Kickoff':

                if not teams.search([('team_code', 'in', ('project',))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'Delivery to customer' or self.task_name == 'Delivery to customer':

                if not teams.search([('team_code', 'in', ('procurement','finance'))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'Training' or self.task_name == 'Training':

                if not teams.search([('team_code', 'in', ('project',))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'Documentation' or self.task_name == 'Documentation':

                if not teams.search([('team_code', 'in', ('project',))]):
                    raise ValidationError("Invalid Sales Team")

            if self.name == 'Project Signoff' or self.task_name == 'pso':

                if not teams.search([('team_code', 'in', ('project',))]):
                    raise ValidationError("Invalid Sales Team")
            if self.name == 'RMA &amp; Repair form' or self.task_name == 'RMA and Repair':

                if not teams.search([('team_code', 'in', ('procurement',))]):
                    raise ValidationError("Invalid Sales Team")
        return super(ProjectTask, self).unlink()
