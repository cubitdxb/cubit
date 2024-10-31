from odoo import models, fields, api, _


class CreateSaleProject(models.TransientModel):
    _name = 'task.invoice.addition'
    _description = 'Add Invoice Task'

    # project_id = fields.Many2one('project.project')
    # name = fields.Char('Name')

    start_date = fields.Date('Start Period', required=True)
    end_date = fields.Date('End Period', required=True)

    # update_invoice_lines = fields.Boolean(string="Update the Customer Invoice Task",help="This will help to update the invoice lines in customer invoice task")

    def update_customer_invoice_task(self):
        search_condition = [('sale_id.date_order', '>=', self.start_date),
                            ('sale_id.date_order', '<=', self.end_date),
                            ('tasks.name', '=', 'Customer Invoice'),
                            ]
# search_condition = [('create_date', '>=', self.start_date),
#                             ('create_date', '<=', self.end_date),
#                             ('tasks.name', '=', 'Customer Invoice'),
#                             ]

        projects = self.env['project.project'].search(search_condition)
        for project in projects:
            task_value = project.tasks.sudo().search(
                [('name', '=', 'Customer Invoice'), ('project_id', '=', project.id)])
            for task_updation in task_value:
            # if not task_count:
                task_updation.sudo().write({
                    'name': 'Invoice to customer',
                    # 'project_id': project.id,
                    # 'display_project_id': project.id,
                    'task_name': 'Invoice',
                    'task_type': 'is_cust_inv',
                    # 'planned_hours_for_l1': project.sale_id.planned_hours_for_l1,
                    # 'planned_hours_for_l2': project.sale_id.planned_hours_for_l2,
                    'invoice_ids':project.sale_id.task_invoice_ids if project.sale_id.task_invoice_ids else False

                })


    def create_task(self):
        task_boq_lines = []
        task_presale_informations = []
        search_condition = [('sale_id.date_order', '>=', self.start_date),
                            ('sale_id.date_order', '<=', self.end_date)]

        # if data['form'][0]['task_ids']:
        #     search_condition.append(('task_ids', 'in', data['form'][0]['task_ids']))
        projects = self.env['project.project'].search(search_condition)
        # ('location_dest_id.usage', '=', 'production'),
        for project in projects:
            # for lines in project.sale_id.order_line:
            #     data = {
            #         'sl_no': lines.sl_no,
            #         'part_number': lines.part_number,
            #         'product_uom_qty': lines.product_uom_qty,
            #         'name': lines.name
            #     }
            #     if (0, 0, data) not in task_boq_lines:
            #         task_boq_lines.append((0, 0, data))
            #
            # for presale_line in project.sale_id.presale_id:
            #     data = {
            #         'presales_team': presale_line.presales_team.id or False,
            #         'presale_department_id': presale_line.presale_department_id.id or False,
            #         'presales_person': presale_line.presales_person.id or False
            #     }
            #     if (0, 0, data) not in task_presale_informations:
            #         task_presale_informations.append((0, 0, data))
            task_count = project.tasks.sudo().search_count(
                [('name', '=', 'Invoice to customer'), ('project_id', '=', project.id)])

            # for task in project.tasks:
                # if any((not tasks.name == 'Invoice to customer') for tasks in project.task_ids):
                # if any((not tasks.name == 'Invoice to customer') for tasks in project.tasks):
            if not task_count:
                self.env['project.task'].sudo().create({
                    'name': 'Invoice to customer',
                    'project_id': project.id,
                    'display_project_id': project.id,
                    'task_name': 'Invoice',
                    'task_type': 'is_cust_inv',
                    'planned_hours_for_l1': project.sale_id.planned_hours_for_l1,
                    'planned_hours_for_l2': project.sale_id.planned_hours_for_l2,
                    'invoice_ids':project.sale_id.task_invoice_ids if project.sale_id.task_invoice_ids else False
                    # 'team_id': user_rel_id,
                    # 'boq_line_ids': task_boq_lines,
                    # 'presale_information_ids': task_presale_informations,

                })
