##############################################################################

from odoo import models,fields,api,_
from odoo.exceptions import AccessError, UserError, ValidationError

class project_make_invoice(models.TransientModel):
    _name = "project.make.invoice"
    _description = "Make Invoice"

    date = fields.Date('Date')
    partner_id = fields.Many2one('res.partner', 'Customer')
    stage_id = fields.Many2one('project.task.type', 'Stage')
    percentage = fields.Float('Percentage')
    amount = fields.Float('Amount')
    project_id = fields.Many2one('project.project', 'Project')
    sale_id = fields.Many2one('sale.order', 'Sale')

    @api.model
    def default_get(self, fields):
        result = super(project_make_invoice, self).default_get(fields)
        active_ids = self.env.context.get('active_id')
        active_ids = active_ids or False
        if self.env.context.get('active_id'):
            task = self.env['project.task'].browse(active_ids)
            result['partner_id'] = task.partner_id.id
            result['project_id'] = task.project_id.id
            result['sale_id'] = task.sale_id.id
        return result


    def make_invoice(self):

        for obj in self:
            customer = obj.partner_id and obj.partner_id.id
            invoice_pool = self.env['account.move']
            percentage = obj.percentage
            amount = obj.amount
            default_fields = invoice_pool.fields_get()
            invoice_default = invoice_pool.default_get(default_fields)
            # onchange_partner = invoice_pool.onchange_partner_id('out_invoice', customer)
            # invoice_default.update(onchange_partner['value'])
            journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
            if not journal:
                raise UserError(
                    _('Please define an accounting sales journal for the company %s (%s).', self.company_id.name,
                      self.company_id.id))

            invoice_default.update({'partner_id': customer,
                                    # 'payment_term': obj.partner_id.property_payment_term.id or False,
                                    'project_id': obj.project_id.id,
                                    'task_id': self.env.context.get('active_id'),
                                    'invoice_date': obj.date,
                                    'move_type': 'out_invoice',
                                    'journal_id': journal.id,
                                    'invoice_payment_term_id': obj.sale_id.payment_term_id.id,
                                    # 'origin': obj.project_id.name
                                    })
            invoice_id = invoice_pool.create(invoice_default)
            # account_id = self.env['ir.property']._get('property_account_expense_categ_id', 'product.category')
            account_id = self.env['ir.property']._get('property_account_income_categ_id','product.category').id
            line_vals = {
                'name': obj.stage_id.name + ' - ' + str(obj.percentage) + '% Payment.',
                'account_id': account_id,
                'quantity': 1,
                'price_unit': amount,
                'move_id': invoice_id.id
            }
            self.env['account.move.line'].create(line_vals)
            # self.write({'invoice_id': invoice_id.id})
        return True


    # @api.onchange('stage_id')
    # def onchange_stage_id(self):
    #     task_id = self._context.get('active_id', False)
    #     value = {}
    #     if task_id:
    #         project = self.env['project.task'].browse(task_id)
    #         stage_ids = self.pool.get('project.payment.line').search(cr, uid, [('project_id', '=', project_id),
    #                                                                            ('stage_id', '=', stage_id)])
    #         amount = 0.0
    #         if stage_ids:
    #             stage = self.pool.get('project.payment.line').browse(cr, uid, stage_ids[0])
    #             if project.sale_id:
    #                 total = project.sale_id.amount_total
    #                 percent = stage.percentage
    #                 amount = (total / 100) * percent
    #             value = {'value': {'percentage': stage.percentage,
    #                                'amount': amount}}
    #     return value


