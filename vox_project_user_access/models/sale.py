# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
import simplejson
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_order_count = fields.Integer(
        "Number of Purchase Order Generated",
        compute='_compute_purchase_order_count',
        groups='purchase.group_purchase_user,vox_user_groups.group_access_for_purchase_order')


    def _get_purchase_orders(self):
        res= super()._get_purchase_orders()
        purchase_ids = []
        s_task_ids = []
        po_ids = [i.id for i in res]
        task_obj = self.env['project.task']
        for so in self:
            if so.project_id and so.project_id.sudo().task_ids.sudo():
                s_task_ids += [tsk.id for tsk in so.project_id.task_ids]
                pur_task_ids = task_obj.search([('id', 'in', s_task_ids), ('project_id', '=', so.project_id.id),
                                                ('purchase_ids', '!=', False)])
                for task_pur in task_obj.browse(pur_task_ids.ids):
                    for purchases in task_pur.purchase_ids:
                        if purchases.id not in po_ids:
                            res += purchases
                            # res += task_pur.purchase_ids
        return res
        # return self.order_line.purchase_line_ids.order_id

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        context = self._context
        res = super(PurchaseOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                          submenu=submenu)
        if self.env.user.has_group('vox_user_groups.group_access_for_purchase_order'):
            doc = etree.XML(res['arch'])
            if view_type == 'form':  # Applies only for form view
                for node in doc.xpath("//field"):  # All the view fields to readonly
                    node.set('readonly', '1')
                    node.set('modifiers', simplejson.dumps({"readonly": True}))
                res['arch'] = etree.tostring(doc)
        return res
