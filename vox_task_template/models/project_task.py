from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from lxml import etree
import time
from datetime import datetime
from odoo import tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # @api.model
    # def create(self, vals):
    #     res = super(ProjectTask, self).create(vals)
    #     print(vals)
    #     return res

    sale_id = fields.Many2one('sale.order', string="Project's sale order", compute='compute_sale_id', store=True)
    user_id = fields.Many2one('res.users')
    reviewer_id = fields.Many2one('res.users', string='Reviewer')
    manager_id = fields.Many2one('res.users', string='Project Manager')
    sales_account_manger = fields.Many2one('res.users', 'Sales Account Manager', related='sale_id.user_id')
    planned_hours = fields.Float('Initial Planned Hours', related='sale_id.planned_hours', store=True)
    delivery_date = fields.Datetime('Delivery Date', related='sale_id.commitment_date')
    company_name = fields.Char('To Company', related='company_id.name')
    by_company_name = fields.Char('By Company', related='sale_id.company_id.name')
    supplier_invoice_no = fields.Char('Supplier Invoice Number')
    date_of_collection = fields.Datetime('Date of collection')
    date_of_return = fields.Datetime('Date of Return')
    issue_reported = fields.Datetime('Issue Reported')
    product_description = fields.Text('Product Description')
    serial_no = fields.Char('Serial Number')
    remarks = fields.Char('Remarks')
    documents_required = fields.Many2one('sale.order', string="Document Required", compute='compute_sale_id',
                                         store=True)
    presale_id = fields.One2many('presale.task.information', 'task_id')
    task_name = fields.Char('Task Name', copy=True)
    reference = fields.Char('Description/Reference', related='sale_id.client_order_ref')
    project_deliverable_ids = fields.One2many('project.deliverable', 'task_id', string='Project Deliverables')
    purchase_delivery_line = fields.One2many('purchase.task.delivery.line', 'task_id', string='Purchase Delivery')
    sale_partner_id = fields.Many2one('res.partner', compute='compute_sale_id', store=True)

    # New fields from Hilsha module

    sale_invoice_exists = fields.Boolean(string="Invoiced")
    purchase_ids = fields.One2many('purchase.order', 'task_id', 'Purchases')
    days_left = fields.Integer(compute='get_days_left', inverse='_set_days_left', string='Days Remaining', store=True)
    task_type = fields.Selection([('is_pm_assign', 'PM Assignment'),
                                  ('is_purchase', 'Purchase Order'),
                                  ('is_internal', 'Internal Kick Off'),
                                  ('is_external', 'External Kick Off'),
                                  ('is_site', 'Site Assessment & Readiness'),
                                  ('is_workshop', 'Workshop'),
                                  ('is_lld', 'LLD & Scope Of Work'),
                                  ('is_good_recepit', 'Good Receipt'),
                                  ('is_delivery', 'Delivery To Customer'),
                                  ('is_payment', 'Payment Receipt'),
                                  ('is_mounting', 'Mounting'),
                                  ('is_config', 'Configurations'),
                                  ('is_document', 'Documentation'),
                                  ('is_train', 'Training'),
                                  ('is_sign_off', 'Sign off'),
                                  ('is_signed_do', 'Upload Signed DO'),
                                  ('is_adv', 'Advance'),
                                  ('is_cust_inv', 'Customer Invoice'),
                                  ('is_test', 'Testing'),
                                  ], 'Task Type', copy=True)
    no_delete = fields.Boolean('No Delete')
    is_delivery = fields.Boolean('Delivery')
    is_purchase = fields.Boolean('Purchase')
    is_technical = fields.Boolean('Documents Required')
    advance_collection = fields.Boolean('Payment Collection')
    advance_exception = fields.Boolean('Mark as Delivery Exception')
    advance_amount = fields.Char('Advance amount')
    combined_sale_ids = fields.Many2many('sale.order', 'task_comb_sale_rel', \
                                         "task_id", "sale_id", "Combined Sales")
    sale_template_id = fields.Many2one('project.project', string="Template ID")
    customer_delivery_ids = fields.One2many('task.delivery', 'task_id', 'Deliveries')

    cubit_id = fields.Integer('cubit id')
    planned_hours_for_l1 = fields.Float('Planned Hours for L1')
    planned_hours_for_l2 = fields.Float('Planned Hours for L2')
    boq_line_ids = fields.One2many('sale.order.materials', 'task_id', 'BOQ Details')
    l_one_user_ids = fields.Many2many('res.users', 'l_one_user_rel', related='project_id.level_one_user_ids',
                                      readonly=False, string='L1 Assignees')
    l_two_user_ids = fields.Many2many('res.users', 'l_two_user_rel', related='project_id.level_two_user_ids',
                                      readonly=False, string='L2 Assignees')
    user_ids = fields.Many2many('res.users',compute='compute_level_one_two_user_ids',
                                string='Assignees', readonly=False, tracking=True, store=True)
    presale_information_ids = fields.One2many('project.presale.information', 'task_id', string='Presale Information')

    # description_name = fields.Char("description")

    def load_products(self):

        line_obj = self.env['purchase.task.delivery.line']
        self.purchase_delivery_line = [(5, _, _)]
        for line in self:
            draft1 = []
            # --pd.purchase_date as purchase_date,
            # --pd.exp_date as exp_date,
            if line.sale_id and line.project_id:
                query44 = """select pd.sequence as sequence,
                        pd.name as name,
                        pd.part_number as part_number,
                        pd.sale_layout_cat_id as sale_layout_cat_id,
                        pd.purchase_date as purchase_date,
                        pd.exp_date as exp_date,
                        --to_char(date_trunc('day',pd.purchase_date),'YYYY-MM-DD') as purchase_date,
                        --to_char(date_trunc('day',pd.exp_date),'YYYY-MM-DD') as exp_date,

                        pd.received as received,
                        pd.type as type,pd.price as price,

                        pd.purchase_partner_id as purchase_partner_id,
                        pd.sale_order_id as sale_order_id
                        from project_task as pt
                        --left join sale_order as s on pt.sale_id=s.id
                        left join purchase_order as p on p.sale_id = pt.sale_id
                        left join purchase_delivery_line as pd on pd.purchase_id = p.id
                        where pt.sale_id = %s and pt.project_id = %s and pt.task_name='Purchase'

                                   """

                self.env.cr.execute(query44, (line.sale_id.id, line.project_id.id))
                s = 0

                for row44 in self.env.cr.dictfetchall():
                    sale = 0
                    possale = 0
                    purtotal = 0
                    sequence = row44['sequence'] if row44['sequence'] else ""
                    name = row44['name'] if row44['name'] else ""
                    part_number = row44['part_number'] if row44['part_number'] else ""
                    sale_layout_cat_id = row44['sale_layout_cat_id'] if row44['sale_layout_cat_id'] else ""
                    if row44['purchase_date']:
                        purchase_date = datetime.strptime(str(row44['purchase_date']), '%Y-%m-%d').date()
                        # date_object = datetime.strptime(str(row44['purchase_date']), '%Y-%m-%d').date()
                        # purchase_date = date_object.strftime('%d-%m-%Y')
                    else:
                        purchase_date = False
                    if row44['exp_date']:
                        exp_date = datetime.strptime(str(row44['exp_date']), '%Y-%m-%d').date()
                        # exp_date_object = datetime.strptime(str(row44['exp_date']), '%Y-%m-%d').date()
                        # exp_date = exp_date_object.strftime('%d-%m-%Y')
                    else:
                        exp_date = False
                    # purchase_date = row44['purchase_date'] if row44['purchase_date'] else ""
                    # exp_date = row44['exp_date'] if row44['exp_date'] else ""
                    received = row44['received'] if row44['received'] else ""
                    type = row44['type'] if row44['type'] else ""
                    price = row44['price'] if row44['price'] else ""
                    # price = row44['price'] if row44['price'] else ""

                    res7 = {
                        'sequence': sequence,
                        'name': name,
                        'sl_num': s + 1,
                        'part_number': part_number,
                        'sale_layout_cat_id': sale_layout_cat_id,
                        'purchase_date': purchase_date,
                        'exp_date': exp_date,
                        'received': received,
                        'type': type,
                        'price': price,
                        # 'purchase_partner_id': draft_amount_total,
                        # 'task_id': draft_amount_total,
                        # 'sale_order_id': draft_amount_total,
                    }

                    draft3 = (0, 0, res7)
                    draft1.append(draft3)
            self.update({

                'purchase_delivery_line': draft1
            })

    @api.depends('project_id')
    def compute_sale_id(self):
        for rec in self:
            rec.sale_id = rec.project_id.sale_id.id
            rec.documents_required = rec.project_id.sale_id.id
            rec.sale_partner_id = rec.project_id.sale_id.partner_id.id
            # rec.planned_hours = rec.project_id.sale_id.planned_hours
            # rec.delivery_date = rec.project_id.sale_id.commitment_date
            # rec.task_name = rec.project_id.taks_id.task_name

    @api.depends('l_one_user_ids', 'l_two_user_ids')
    def compute_level_one_two_user_ids(self):
        print(33333333333333333333333333333333333333333333)
        users = []
        for rec in self.l_one_user_ids:
            users.append(rec.id)
        for l2 in self.l_two_user_ids:
            users.append(l2.id)
        print(users, 11111111111111111111111111111)
        self.user_ids = users

    def print_sign_off_document(self):
        return self.env.ref('vox_task_template.action_report_project_sign_off').report_action(self)

    def print_repair_and_form_document(self):
        return self.env.ref('vox_task_template.action_report_repair_template').report_action(self)

    @api.depends('sale_id')
    def compute_presale_lines(self):
        presale_lines = []
        if self.sale_id.presale_id:
            presale_id = self.env['presale.information'].search([('sale_order_id', '=', self.sale_id.id)])
            for record in presale_id:
                data = {
                    'id': record.id,
                    'name': record.name,
                    'presales_person': record.presales_person.id,
                }
                if data:
                    presale_lines.append((0, 0, data))
        if presale_lines:
            self.presale_id = presale_lines

    @api.onchange('delivery_date')
    def onchange_delivery_date(self):
        for rec in self:
            if rec.sale_id.commitment_date:
                rec.delivery_date = rec.sale_id.commitment_date
            else:
                raise ValidationError(_('Delivery not completed'))
                rec.delivery_date = False

    def get_days_left(self):
        for record in self:
            if record.date_deadline:
                today = datetime.strptime(time.strftime(tools.DEFAULT_SERVER_DATE_FORMAT),
                                          tools.DEFAULT_SERVER_DATE_FORMAT).date()
                date_deadline = record.date_deadline
                diff_time = (date_deadline - today).days
                color = 0
                if diff_time > 2:
                    color = 5
                elif diff_time > 0:
                    color = 3
                elif diff_time == 0:
                    color = 2
                record.days_left = diff_time > 0 and diff_time or 0
            else:
                record.days_left = -1
        return

    def _set_days_left(self, field_value):
        for record in self:
            if record.days_left != field_value:
                self.env.cr.execute(
                    'UPDATE project_task '
                    'SET days_left=%s '
                    'WHERE id=%s', (field_value, id)
                )
                color = 0
                if field_value > 2:
                    color = 5
                elif field_value > 0:
                    color = 3
                elif field_value == 0:
                    color = 2
                    # ret = super(task, self).write(cr, SUPERUSER_ID, record.id, {'color': color}, context=context)
                ret = super(ProjectTask, self).write({'days_left': field_value}, )
            else:
                pass
                # It is a new record
                # (or the value of the field was not modified)

        return True

    def action_view_purchases(self):
        purchase_ids = []
        pur_ids = False
        for task_inv in self:
            if task_inv.project_id:
                pur_task_ids = self.search([('project_id', '=', task_inv.project_id.id), ('purchase_ids', '!=', False)])
                if pur_task_ids:
                    for task_pur in self.browse(pur_task_ids.ids):
                        purchase_ids += task_pur.purchase_ids
                # if purchase_ids:
                #    pur_ids += purchase_ids
                mod_obj = self.env['ir.model.data']
                act_obj = self.env['ir.actions.act_window']

                result = mod_obj._xmlid_lookup('vox_task_template.purchase_form_task_action')
                id = result or result[2] if result else False
                result = act_obj._for_xml_id('vox_task_template.purchase_form_task_action')
                po_ids = []
                po_ids += [po.id for po in purchase_ids]
                if po_ids:
                    # choose the view_mode accordingly
                    if len(purchase_ids) > 1:
                        result['domain'] = "[('id','in',[" + ','.join(map(str, po_ids)) + "])]"
                    else:
                        res = mod_obj._xmlid_lookup('purchase.purchase_order_form')
                        result['views'] = [(res[2] if res else False, 'form')]
                        result['res_id'] = po_ids and po_ids[0] or False
                    return result
        if len(purchase_ids) == 0:
            raise ValidationError(_("No Purchase Order"))
            # return {'warning': {
            #     'title': 'Warning!',
            #     'message': 'No Purchase Order'}}
        return True

    def action_view_sale_order(self):
        for task_inv in self:
            if task_inv.sale_id:
                view = self.env.ref('sale.view_order_form')
                return {
                    'name': _('Sales Order'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': view.id,
                    'res_model': 'sale.order',
                    'res_id': task_inv.sale_id.id,
                    'domain': [('id', '=', task_inv.sale_id.id)],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                }
        return True

    def action_view_deliveries(self):
        deliv_ids = []
        s_task_ids = []
        delivery_ids = []
        for so in self:
            if so.project_id and so.project_id.sudo().task_ids:
                # for so in self.browse(cr, uid, ids, context=context):
                #     if so.project_id and so.project_id.task_ids:
                s_task_ids += [tsk.id for tsk in so.project_id.sudo().task_ids]
                deliv_task_ids = self.search([('id', 'in', s_task_ids), ('project_id', '=', so.project_id.id),
                                              ('customer_delivery_ids', '!=', False)])
                for task_deliv in self.browse(deliv_task_ids.ids):
                    delivery_ids += task_deliv.customer_delivery_ids
            mod_obj = self.env['ir.model.data']
            act_obj = self.env['ir.actions.act_window']

            result = mod_obj._xmlid_lookup('vox_task_template.task_delivery_action')
            id = result or result[2] if result else False
            result = act_obj._for_xml_id('vox_task_template.task_delivery_action')
            deliv_ids = []
            deliv_ids += [deliv.id for deliv in delivery_ids]
            if deliv_ids:
                # choose the view_mode accordingly
                if len(deliv_ids) > 1:
                    result['domain'] = "[('id','in',[" + ','.join(map(str, deliv_ids)) + "])]"
                else:
                    res = mod_obj._xmlid_lookup('vox_task_template.view_task_delivery_rate')
                    result['views'] = [(res[2] if res else False, 'form')]
                    result['res_id'] = deliv_ids and deliv_ids[0] or False
                return result
        if len(deliv_ids) == 0:
            raise ValidationError(_("No Delivery"))
        return True


class PresaleTaskInformation(models.Model):
    _name = 'presale.task.information'

    presale_department_id = fields.Char(string="Presales Department")
    presales_person = fields.Many2one('res.users', string="Presales Person")
    task_id = fields.Many2one('project.task')


class ProjectDeliverableInformation(models.Model):
    _name = 'project.deliverable'

    task_id = fields.Many2one('project.task')
    name = fields.Char(string="Description")
    status = fields.Boolean(string="Status")
    remarks = fields.Char('Remarks')




