from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError, Warning, UserError


class CreateDelivery(models.TransientModel):
    _name = 'task.make.delivery'
    _description = 'task delivery wizard'

    partner_id = fields.Many2one('res.partner', string='Customer')
    date = fields.Date('Date')
    customer_ref = fields.Char('Reference/Description')
    sale_number = fields.Char('Sale order number')
    line_ids = fields.One2many('task.make.delivery.line', 'deliverable_id', string='Items')
    task_id = fields.Many2one('project.task', 'Task')
    sale_id = fields.Many2one('sale.order', 'Sale')
    select_all = fields.Boolean('Line Select All')

    @api.model
    def default_get(self, fields):
        result = super(CreateDelivery, self).default_get(fields)

        project_team_users = self.env['crm.team'].search([('team_code', '=', 'project')]).mapped('member_ids').ids
        procurement_team_users = self.env['crm.team'].search([('team_code', '=', 'procurement')]).mapped(
            'member_ids').ids
        finance_team_users = self.env['crm.team'].search([('team_code', '=', 'finance')]).mapped('member_ids').ids
        procurement_finance = procurement_team_users + finance_team_users
        current_user = self.env.uid

        if current_user in project_team_users and current_user not in procurement_finance:
            raise ValidationError(_('You are not able to create delivery'))
        active_ids = self.env.context.get('active_id')
        active_ids = active_ids or False
        delivery_lines = []
        if self.env.context.get('active_id'):
            task = self.env['project.task'].browse(active_ids)
            result['date'] = datetime.now()
            result['partner_id'] = task.partner_id.id
            result['sale_number'] = task.sale_id.name
            result['customer_ref'] = task.sale_id.client_order_ref
            result['task_id'] = task.id
            result['sale_id'] = task.sale_id.id

            sl_number = ''
            sl_number_vals = {}
            custom_sale_str = '__CUSTOMSALEPARTNO__'

            for task in task.project_id.sudo().tasks:
                print(task.purchase_ids, 'purchase idssssssssss')
                if task.purchase_ids:
                    print(22222222222222222222222222222222)
                    for pur in task.purchase_ids:
                        # print(pur.purchase_ids, 'purchase ttttttt')
                        prev_purchase_order_line_id = None
                        for pur_deliv in pur.delivery_ids:
                            if pur_deliv.sl_num:
                                if pur_deliv.purchase_order_line_id.id == prev_purchase_order_line_id:
                                    sl_number = pur_deliv.sl_num + ', ' + sl_number
                                else:
                                    sl_number = pur_deliv.sl_num
                                    prev_purchase_order_line_id = pur_deliv.purchase_order_line_id.id
                                if pur_deliv.purchase_order_line_id.part_number:
                                    sl_number_vals[pur_deliv.purchase_order_line_id.part_number] = sl_number
                                elif pur_deliv.purchase_order_line_id.sale_line_id:
                                    custom_part_number = custom_sale_str + str(
                                        pur_deliv.purchase_order_line_id.sale_line_id.id)
                                    sl_number_vals[custom_part_number] = sl_number
                                else:
                                    sl_number_vals[pur_deliv.purchase_order_line_id.part_number] = sl_number

            for line in task.project_id.sudo().sale_id.order_line:
                sl_number = ''
                custom_sl_index = str(line.id)
                custom_sl_index = custom_sale_str + custom_sl_index
                if line.part_number in sl_number_vals:
                    sl_number = sl_number_vals[line.part_number]
                elif custom_sl_index in sl_number_vals:
                    sl_number = sl_number_vals[custom_sl_index]
                vals = {'name': line.name,
                        'product_qty': line.product_uom_qty,
                        'sale_line_id': line.id,
                        'part_number': line.part_number,
                        'sl_number': sl_number,
                        'hs_code': line.hs_code,
                        'country_of_origin': line.country_of_origin,
                        'th_weight': line.th_weight
                        }
                delivery_lines.append((0, 0, vals))
            result['line_ids'] = delivery_lines

        return result

    def verify_advance_recieved(self):
        active_ids = self.env.context.get('active_id')
        active_ids = active_ids or False
        # for obj in self:
        # task_id = obj.task_id.id
        project_id = self.env['project.task'].browse(active_ids).project_id
        if project_id:
            # task_ids = self.env['project.task'].search([('project_id', '=', project_id.id),
            #                                                           ('advance_collection', '=', True),
            #                                                           ('kanban_state', '!=', 'done'),
            #                                                           ('advance_exception', '=', False)])
            task_ids = self.env['project.task'].search([('project_id', '=', project_id.id),
                                                        ('advance_collection', '=', False),
                                                        ('kanban_state', '!=', 'done'),
                                                        ('task_name', '=', 'Advance'),
                                                        ('advance_exception', '=', False)])
            if task_ids:
                raise ValidationError(_('Advance is not received yet. Manager Approval Required'))
                # raise ValidationError(_('Error!'),
                #     _('Advance is not received yet. Manager Approval Required'))
        return True

    def create_delivery(self):
        template = self.env.ref('vox_task_template.mail_template_create_delivery')

        active_ids = self.env.context.get('active_id')
        active_ids = active_ids or False
        project_project = self.env['project.task'].browse(self._context.get('active_id')).project_id
        sale_ref = self.env['project.task'].browse(self._context.get('active_id')).sale_id
        email_values = {
            'email_to': project_project.user_id.partner_id.email + ',' + project_project.sale_id.user_id.partner_id.email if project_project.sale_id.user_id.partner_id.email else '',
            'recipient_ids': []}
        template.send_mail(self.ids[0], force_send=True, email_values=email_values)
        task_delivery = []
        task_delivery_lines = []
        for obj in self:
            self.verify_advance_recieved()
            sequence = self.env['ir.sequence'].next_by_code('task.delivery')
            main_val = {
                'partner_id': obj.partner_id and obj.partner_id.id or False,
                'date': obj.date,
                'task_id': obj.task_id and obj.task_id.id or False,
                'customer_ref': obj.customer_ref,
                'sale_number': obj.sale_number,
                'deliv_sale_id': obj.sale_id and obj.sale_id.id or False,
                'name': sequence
            }
            # print(main_val, 'mainvall')
            task_delivery.append((0, 0, main_val))
            delivery_id = self.env['task.delivery'].create(main_val)
            for line in obj.line_ids:
                vals = {
                    'product_id': line.product_id and line.product_id.id or False,
                    'name': line.name,
                    'deliv_sale_line_id': line.sale_line_id.id,
                    'qty': line.product_qty,
                    'part_number': line.part_number,
                    'hs_code': line.hs_code,
                    'country_of_origin': line.country_of_origin,
                    'th_weight': line.th_weight,
                    'sl_number': line.sl_number,
                    'delivery_id': delivery_id.id
                }
                task_delivery_lines.append((0, 0, vals))
                self.env['task.delivery.line'].create(vals)
                for rec in sale_ref.order_line:
                    if rec.id == line.sale_line_id.id:
                        rec.update({'qty_delivered': line.product_qty})

        # return {'type': 'ir.actions.act_window_close'}
        self.env.user.notify_success(message='Delivery Successful')

    # @api.onchange('select_all', 'dup_vendors')
    # def onchange_select_all(self, ):
    #
    #     lines = [(5,)]
    #     self.create_delivery()
    #     for obj in self:
    #         for line in obj.line_ids:
    #             data = {
    #                 'deliverable_id': obj.id,
    #                 'product_id': line.product_id and line.product_id.id or False,
    #                 'sl_number': line.sl_number,
    #                 'part_number': line.part_number,
    #                 'name': line.name,
    #                 'product_qty': line.product_qty,
    #                 'sale_line_id': line.sale_line_id and line.sale_line_id.id or False,
    #                 'hs_code': line.hs_code if line.hs_code else False,
    #                 'country_of_origin': line.country_of_origin if line.country_of_origin else False,
    #             }
    #             if obj.select_all:
    #                 data.update({'delivery': True})
    #             else:
    #                 data.update({'delivery': False})
    #             lines.append((0, 0, data))
    #         obj.line_ids = lines
    #     return


class MakeDeliveryLine(models.TransientModel):
    _name = 'task.make.delivery.line'

    deliverable_id = fields.Many2one('task.make.delivery', 'Wizard')
    sale_line_id = fields.Many2one('sale.order.line', 'Sale Line')
    product_id = fields.Many2one('product.product', 'Product')
    name = fields.Char('Name')
    part_number = fields.Char('Part No.')
    sl_number = fields.Char('Sl No.')
    product_qty = fields.Float('Quantity')
    hs_code = fields.Char(string='Hs Code')
    country_of_origin = fields.Char(string='Country Of Origin')
    th_weight = fields.Char(string='Weight')
    delivery = fields.Boolean('Delivery')
