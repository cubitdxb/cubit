# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from collections import defaultdict, Counter
import datetime
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    approved_margin = fields.Boolean(string='Margin Approved', copy=False)
    margin_visibility = fields.Boolean(string='Margin Approved Button', compute='visibility_margin_approve', store=True,
                                       copy=False)
    margin_visibility_one_two = fields.Boolean(string='First and second level visibility',
                                               compute='visibility_margin_approve', store=True, copy=False)
    margin_approve_one_two = fields.Boolean(string='Margin First and second level is approved.',
                                            compute='action_approve_margin', store=True, copy=False, tracking=True)
    margin_visibility_one = fields.Boolean(string='First level visibility', compute='visibility_margin_approve',
                                           store=True, copy=False)
    margin_approve_one = fields.Boolean(string='Margin First level is approved.', compute='action_approve_margin',
                                        store=True, copy=False, tracking=True)
    margin_visibility_two = fields.Boolean(string='Second Level visibility', compute='visibility_margin_approve',
                                           store=True, copy=False)
    margin_approve_two = fields.Boolean(string='Margin Second Level is Approved.', compute='action_approve_margin',
                                        store=True, copy=False, tracking=True)
    email_request = fields.Boolean(string='email Request', default=False, copy=False)
    cubit_service = fields.Boolean('cubit service', store=True)
    email_approve_one_two = fields.Boolean(string='Email First and second level is approved.',
                                           compute='email_approval_request', store=True, copy=False, tracking=True)
    email_approve_one = fields.Boolean(string='Email First level is approved.', compute='email_approval_request',
                                       store=True, copy=False, tracking=True)
    email_approve_two = fields.Boolean(string='Email second level is approved.', compute='email_approval_request',
                                       store=True, copy=False, tracking=True)
    state = fields.Selection(selection_add=[
        ('send_for_margin_approval', 'Send For margin Approval'),
        ('first_level_margin_approval', 'First Level Margin Approval'),
        ('second_level_margin_approval', 'Second Level Margin Approval'),
        ('send_for_email_approval', 'Send For E-Mail Approval'),
        ('first_level_email_approval', 'First Level E-Mail Approval'),
        ('second_level_email_approval', 'Second Level E-Mail Approval'),
        ('send_for_lpo_email_margin_approval', 'Send For LPO E-Mail/Margin Approval'),
    ])

    # @api.depends('email_request','lpo_email','lpo_email_attachment')
    # def email_request_approve(self):
    #     # level_user = []
    #     # context = self._context
    #     # current_uid = context.get('uid')
    #     # user = self.env['res.users'].browse(current_uid)
    #     for order in self:
    #         # if order.team_id:
    #         #     level_three = order.team_id.level_three_employee_ids.ids
    #         #     level_four = order.team_id.level_four_employee_ids.ids
    #         #     level_user = level_three + level_four
    #         if order.lpo_email==True:
    #             if (self.env.user.has_group('vox_user_groups.group_sale_salesman_level_3_user') or self.env.user.has_group('vox_user_groups.group_sale_salesman_level_4_user')) and self.env.user.has_group('vox_user_groups.email_approval_user') and order.email_request == False:
    #                 order.email_request_visibility = True
    #             elif (self.env.user.has_group('vox_user_groups.group_sale_salesman_level_3_user') or self.env.user.has_group('vox_user_groups.group_sale_salesman_level_4_user')) and self.env.user.has_group('vox_user_groups.email_approval_user') and order.email_request == True:
    #                 order.email_request_visibility = False
    #             else:
    #                 order.email_request_visibility = False
    #         else:
    #             order.email_request_visibility = False

    def email_approval_request(self):
        for order in self:
            if self.env.user.has_group('vox_user_groups.email_approval_user_one') and self.env.user.has_group(
                    'vox_user_groups.email_approval_user_two'):
                order.email_approve_one_two = True
                order.email_request = True
                order.state = 'second_level_email_approval'
                self.env.user.notify_success(message='Email is  approved for Both Level one and level two users')
            elif self.env.user.has_group('vox_user_groups.email_approval_user_one') and not self.env.user.has_group(
                    'vox_user_groups.email_approval_user_two') and not order.email_approve_one:
                order.email_approve_one = True
                order.state = 'first_level_email_approval'
                self.env.user.notify_success(message='First level email is approved, Send for second approval')
            elif self.env.user.has_group('vox_user_groups.email_approval_user_two') and not self.env.user.has_group(
                    'vox_user_groups.email_approval_user_one') and order.email_approve_one:
                order.email_approve_two = True
                order.email_request = True
                order.state = 'second_level_email_approval'
                self.env.user.notify_success(message='Second level email is approved')
            elif self.env.user.has_group('vox_user_groups.email_approval_user_two') and not self.env.user.has_group(
                    'vox_user_groups.email_approval_user_one') and not order.email_approve_one:
                self.env.user.notify_warning(message='First level email is not approved')
            else:
                self.env.user.notify_danger(message='You are not eligible to approve email!')

        return

    @api.onchange('order_line')
    def onchange_order_line(self):
        for rec in self:
            if any(line.is_cubit_service == True for line in self.order_line):
                rec.cubit_service = True
            else:
                rec.cubit_service = False

    @api.depends('order_line.margin', 'order_line.is_cubit_service')
    def visibility_margin_approve(self):
        for order in self:
            if any(line.margin < 5 for line in self.order_line) and self.env.user.has_group(
                    'vox_user_groups.margin_approval_user_one') and self.env.user.has_group(
                'vox_user_groups.margin_approval_user_two'):
                order.margin_visibility = True
                order.margin_visibility_one_two = True
            elif any(line.margin < 5 for line in self.order_line) and self.env.user.has_group(
                    'vox_user_groups.margin_approval_user_one') and not self.env.user.has_group(
                'vox_user_groups.margin_approval_user_two'):
                order.margin_visibility = True
                order.margin_visibility_one = True
            elif any(line.margin < 5 for line in self.order_line) and not self.env.user.has_group(
                    'vox_user_groups.margin_approval_user_one') and self.env.user.has_group(
                'vox_user_groups.margin_approval_user_two'):
                order.margin_visibility = True
                order.margin_visibility_two = True
            else:
                order.margin_visibility = False

    def action_approve_margin(self):
        for order in self:
            if self.env.user.has_group('vox_user_groups.margin_approval_user_one') and self.env.user.has_group(
                    'vox_user_groups.margin_approval_user_two'):
                order.margin_approve_one_two = True
                order.approved_margin = True
                order.state = 'second_level_margin_approval'
                self.env.user.notify_success(message='Both Margin is  approved')
            elif self.env.user.has_group('vox_user_groups.margin_approval_user_one') and not self.env.user.has_group(
                    'vox_user_groups.margin_approval_user_two') and not order.margin_approve_one:
                order.margin_approve_one = True
                order.state = 'first_level_margin_approval'
                self.env.user.notify_success(message='First level margin is approved, Send for second approval')
            elif self.env.user.has_group('vox_user_groups.margin_approval_user_two') and not self.env.user.has_group(
                    'vox_user_groups.margin_approval_user_one') and order.margin_approve_one:
                order.margin_approve_two = True
                order.approved_margin = True
                order.state = 'second_level_margin_approval'
                self.env.user.notify_success(message='Second level margin is approved')
            elif self.env.user.has_group('vox_user_groups.margin_approval_user_two') and not self.env.user.has_group(
                    'vox_user_groups.margin_approval_user_one') and not order.margin_approve_one:
                self.env.user.notify_warning(message='First level margin is not approved')
            else:
                self.env.user.notify_danger(message='You are not eligible to approve margin!')

        return

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for line in self.order_line:

            if self.state not in ['second_level_margin_approval', 'second_level_email_approval']:
                # if line.margin < 5 and self.lpo_email == False:
                #     self.state = 'send_for_margin_approval'
                # if line.margin > 5 and self.lpo_email == True:
                #     self.state = 'send_for_email_approval'
                if (line.margin < 5 and self.approved_margin == False) and (
                        self.lpo_email == True and self.email_request == False):
                    action = self.env.ref(
                        'vox_approve_margin.wizard_margin_email_message_action').sudo().read()[0]
                    return action
                if line.margin < 5 and self.approved_margin == False:
                    if not line.is_cubit_service:
                        # self.state = 'send_for_margin_approval'
                        action = self.env.ref(
                            'vox_approve_margin.wizard_message_action').sudo().read()[0]
                        return action

                        # return {
                        #     'type': 'ir.actions.act_window',
                        #     'res_model': 'approval.message',
                        #     'res_id': self.id,
                        #     'view_id': view.id,
                        #     'views': [[self.env.ref('vox_approve_margin.id_wizard_margin_message_form').id, 'form']],
                        #     'view_mode': 'form',
                        #     # 'view_type': 'form',
                        #     # 'target': 'new'
                        # }

                        # raise ValidationError(_('It is not allowed to confirm an order when the margin is less than 5%'))
                # if self.state not in ['second_level_email_approval']:
                if self.lpo_email == True and self.email_request == False:
                    # self.state = 'send_for_email_approval'
                    action = self.env.ref(
                        'vox_approve_margin.wizard_email_message_action').sudo().read()[0]
                    return action
                # raise ValidationError(_('You cannot confirm SO without E-mail Approval'))
        return res


    def action_draft(self):
        res = super(SaleOrder, self).action_draft()
        for order in self:
            if order.state in ('cancel', 'draft') or order._origin.state in ('cancel', 'draft'):
                order._origin.write({
                    'email_approve_one_two': False,
                    'email_request': False,
                    'email_approve_two': False,
                    'email_approve_one': False,
                    'margin_approve_one_two': False,
                    'approved_margin': False,
                    'margin_approve_two': False,
                    'margin_approve_one': False,
                    # 'state': 'draft',
                })
        return res

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for order in self:
            if order.state in ('cancel', 'draft') or order._origin.state in ('cancel', 'draft'):
                order._origin.write({
                    'email_approve_one_two': False,
                    'email_request': False,
                    'email_approve_two': False,
                    'email_approve_one': False,
                    'margin_approve_one_two': False,
                    'approved_margin': False,
                    'margin_approve_two': False,
                    'margin_approve_one': False,
                    # 'state': 'draft',
                })
        return res

    # @api.onchange('state')
    # def _onchange_sale_state(self):
    #     for order in self:
    #         if order.state in ('cancel','draft') or order._origin.state in ('cancel','draft'):
    #             order._origin.write({
    #                 'email_approve_one_two': False,
    #                 'email_request': False,
    #                 'email_approve_two': False,
    #                 'email_approve_one': False,
    #                 'margin_approve_one_two': False,
    #                 'approved_margin': False,
    #                 'margin_approve_two': False,
    #                 'margin_approve_one': False,
    #                 # 'state': 'draft',
    #             })

    @api.onchange('lpo_email', 'lpo_email_attachment')
    def _onchange_email_value(self):
        for order in self:
            if (order.state in ('send_for_email_approval')):
                order._origin.write({
                    'state': 'draft',
                })
            if (order.state in ('first_level_email_approval')):
                order._origin.write({
                    'email_approve_one': False,
                    'state': 'draft',
                })
            elif (order.state in ('second_level_email_approval')):
                order._origin.write({
                    'email_approve_one_two': False,
                    'email_request': False,
                    'email_approve_two': False,
                    'state': 'draft',
                })


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('margin')
    def _onchange_margin_value(self):
        for order in self:
            if order._origin.order_id.state != False:
                if (order.order_id.state in ('send_for_margin_approval') or order._origin.order_id.state in (
                'send_for_margin_approval')):
                    order._origin.order_id.write({
                        'state': 'draft',
                    })
                if (order.order_id.state in ('first_level_margin_approval') or order._origin.order_id.state in (
                'first_level_margin_approval')):
                    order._origin.order_id.write({
                        'margin_approve_one': False,
                        'state': 'draft',
                    })
                    # order.order_id.margin_approve_one = False
                    # order.order_id.state = 'draft'
                    # order.order_id.action_approve_margin()
                elif (order.order_id.state in ('second_level_margin_approval') or order._origin.order_id.state in (
                'second_level_margin_approval')):
                    order._origin.order_id.write({
                        'margin_approve_one_two': False,
                        'approved_margin': False,
                        'margin_approve_two': False,
                        'state': 'draft',
                    })
                # order.order_id.margin_approve_one_two = False
                # order.order_id.approved_margin = False
                # order.order_id.margin_approve_two = False
                # order.order_id.state = 'draft'
                # order.order_id.action_approve_margin()
