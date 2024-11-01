# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    invoice_ids = fields.One2many('account.move', 'task_id', 'Invoice')
    is_regular_invoice = fields.Boolean(string="Regular Invoice")

    def action_view_invoice(self):
        invoices_ids = []
        # sale_invoice = False
        for task_inv in self:
            # sale_invoice = task_inv.sale_id if task_inv.sale_id else False
            sale_invoice = self.search([('project_id', '=', task_inv.project_id.id), ('invoice_ids', '!=', False)])
            if sale_invoice:
                for task_pur in self.browse(sale_invoice.ids):
                    invoices_ids += task_pur.invoice_ids
        if sale_invoice:
            mod_obj = self.env['ir.model.data']
            act_obj = self.env['ir.actions.act_window']
            result = mod_obj._xmlid_lookup('vox_task_invoice.action_invoice_tree1')
            id = result or result[2] if result else False
            result = act_obj._for_xml_id('vox_task_invoice.action_invoice_tree1')
            inv_ids = []
            inv_ids += [invoice.id for invoice in invoices_ids]
            result['domain'] = "[('move_type','in',('out_invoice', 'out_refund'))]"
            if len(inv_ids) > 1:
                result['domain'] = "[('move_type','in',('out_invoice', 'out_refund')),('id','in',[" + ','.join(map(str, inv_ids)) + "])]"
            else:
                res = mod_obj._xmlid_lookup('account.view_move_form')
                result['views'] = [(res[2] if res else False, 'form')]
                result['res_id'] = inv_ids and inv_ids[0] or False
            return result
        else:
            return True

