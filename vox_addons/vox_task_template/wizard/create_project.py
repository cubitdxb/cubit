from odoo import models, fields, api, _


class CreateSaleProject(models.TransientModel):
    _name = 'project.create.wizard'
    _description = 'Create project from sale order'

    project_id = fields.Many2one('project.project')
    name = fields.Char('Name')

    def create_project(self):
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
                'planned_hours_for_l2': sale_order_rec.planned_hours_for_l2

            })
            for task in project_obj.task_ids:
                self.env['project.task'].sudo().create({
                    'name': task.name,
                    'project_id': project_id.id,
                    'display_project_id': task.display_project_id.id,
                    'task_name': task.task_name,
                    'task_type': task.task_type,
                    'planned_hours_for_l1': sale_order_rec.planned_hours_for_l1,
                    'planned_hours_for_l2': sale_order_rec.planned_hours_for_l2

                })
            sale_order_rec.write({'project_created': True, 'project_id': project_id})
