from odoo import fields, models, api, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    state = fields.Selection([
                               ('draft', 'New'),
                               ('open', 'In Progress'),
                               ('cancelled', 'Cancelled'),
                                ('template', 'Template'),
                               ('pending', 'Pending'),
                               ('close', 'Closed')],
                              'Status', required=True,copy=False,default='draft')
    sale_id = fields.Many2one('sale.order', "Project's sale order")
    sale_ref = fields.Char("Project's sale order", related='sale_id.name')
    cubit_id = fields.Integer(string="Cubit ID")
    project_template = fields.Many2one('project.project', "Project Template")
    planned_hours_for_l1 = fields.Float('Planned Hours for L1')
    planned_hours_for_l2 = fields.Float('Planned Hours for L2')
    planned_hours = fields.Float('Planned Hours')
    planned_hour_readonly = fields.Boolean('Planned Hour Read only', compute='planned_hours_readonly')
    boq_ids = fields.One2many('sale.order.materials', 'project_id', 'BOQ')
    boq_readonly = fields.Boolean('Boq Visibility', compute='planned_hours_readonly')
    level_one_user_ids = fields.Many2many('res.users', 'level_one_assignees_rel', string='L1 Assignees')
    level_two_user_ids = fields.Many2many('res.users', 'level_two_assignees_rel', string='L2 Assignees')
    user_ids = fields.Many2many('res.users', 'assignees_rel','user_id','prj_id', compute='onchange_level_one_two_user_ids', readonly=False, string='Assignees',store=True)
    presale_information_ids = fields.One2many('project.presale.information', 'project_id', string='Presale Information')
    project_team_only = fields.Boolean('Project Team Only', compute='compute_project_team_only')
    attachment_ids = fields.Many2many('ir.attachment', string="Attachments", related='sale_id.attachment_ids')

    def write(self, vals):
        if 'stage_id' in vals:
            template = self.env.ref('vox_task_template.mail_template_project_closure')
            procurement_team_users = self.env['crm.team'].search([('team_code', '=', 'procurement')]).mapped('member_ids').partner_id.ids
            finance_team_users = self.env['crm.team'].search([('team_code', '=', 'finance')]).mapped('member_ids').partner_id.ids
            users = procurement_team_users + finance_team_users
            sign_off_template = self.env.ref('vox_task_template.mail_template_sign_off')
            sign_off_stage = self.env.ref('vox_task_template.stage_sign_off').id
            closed_stage = self.env.ref('vox_task_template.stage_closed').id
            for rec in self:
                if sign_off_stage == vals['stage_id']:
                    if sign_off_template:
                        email_values = {'email_to': rec.sale_id.partner_contact.email, 'recipient_ids': []}
                        sign_off_template.send_mail(rec.ids[0], force_send=True, email_values=email_values)
                if closed_stage == vals['stage_id']:
                    email_values = {'email_to': rec.sale_id.user_id.partner_id.email, 'recipient_ids': users}
                    if template:
                        template.send_mail(rec.ids[0], force_send=True, email_values=email_values)

        return super(ProjectProject, self).write(vals)

    @api.onchange('level_one_user_ids', 'level_two_user_ids')
    def onchange_level_one_two_user_ids(self):
        users = []
        for rec in self.level_one_user_ids:
            users.append(rec.id)
        for l2 in self.level_two_user_ids:
            users.append(l2.id)
        self.user_ids = users

    @api.onchange('user_ids')
    def compute_assignees(self):
        users = []
        for rec in self.user_ids:
            users.append(rec.id)
        project_task = self.env['project.task'].search([('project_id', '=', self.id)])
        for task in project_task:
            task.user_ids = []
            task.user_ids = users

    def compute_project_team_only(self):
        other_team_users = self.env['crm.team'].search([('team_code', '!=', 'project')]).mapped('member_ids').ids
        project_team_users = self.env['crm.team'].search([('team_code', '=', 'project')]).mapped('member_ids').ids
        for rec in self:
            if self.env.uid in project_team_users and self.env.uid not in other_team_users:
                rec.project_team_only = True
            else:
                rec.project_team_only = False
    def planned_hours_readonly(self):
        project_team_users = self.env['crm.team'].search([('team_code', '=', 'project')]).mapped('member_ids').ids
        for rec in self:
            if self.env.uid in project_team_users:
                rec.planned_hour_readonly = True
                rec.boq_readonly = True
            else:
                rec.planned_hour_readonly = False
                rec.boq_readonly = False


class SaleOrderLineMaterials(models.Model):
    _name = 'sale.order.materials'

    project_id = fields.Many2one('project.project', 'Project Reference')
    task_id = fields.Many2one('project.task', 'Project Task Reference')
    sl_no = fields.Integer('Serial Number')
    part_number = fields.Char('Part Number')
    name = fields.Text('Description')
    product_uom_qty = fields.Float('Quantity')


class ProjectPresaleInformation(models.Model):
    _name = 'project.presale.information'

    presales_team = fields.Many2one('crm.team', string="Presales Team")
    project_id = fields.Many2one('project.project', string='Project Reference')
    task_id = fields.Many2one('project.task', string='Task Reference')
    presale_department_id = fields.Many2one('presale.department', string="Presales Department")
    presales_person = fields.Many2one('res.users', string="Presales Person")
