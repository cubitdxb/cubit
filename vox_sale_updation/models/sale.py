# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    quote_cancel_remark = fields.Text(string="Remark")
    exclude_purchase = fields.Boolean(string='Exclude PO',default=False)

    def sale_remark_wizard_button(self):
        action = self.env["ir.actions.actions"]._for_xml_id('vox_sale_updation.sale_cancel_remarks_action')
        action['context'] = {'default_sale_id': self.id}
        return action

    def exclude_purchases(self):
        # sale_order_line_obj = self.env['sale.order.line']
        for sale in self:
            for line in sale.order_line:
                if line.is_cubit_service == False and line.exclude_purchase == False:
                    line.write({'exclude_purchase': True})
            sale.write({'exclude_purchase': True})
        return True

    def reset_exclude_purchase(self):
        # sale_order_line_obj = self.pool.get('sale.order.line')
        for sale in self:
            for line in sale.order_line:
                if line.is_cubit_service == False and line.exclude_purchase == True:
                    line.write({'exclude_purchase': False})
            sale.write({'exclude_purchase': False})
        return True


    def action_view_deliveries(self):
        deliv_ids = []
        s_task_ids = []
        delivery_ids = []
        task_obj = self.env['project.task']
        for so in self:
            if so.project_id and so.project_id.sudo().task_ids:
                s_task_ids += [tsk.id for tsk in so.project_id.sudo().task_ids]
                deliv_task_ids = task_obj.search([('id', 'in', s_task_ids), ('project_id', '=', so.project_id.id),
                                                  ('customer_delivery_ids', '!=', False)])
                for task_deliv in task_obj.browse(deliv_task_ids.ids):
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




