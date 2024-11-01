# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"


    @api.depends('task_invoice_ids')
    def _get_invoiced(self):
        for order in self:
            invoices = order.task_invoice_ids.filtered(lambda r: r.move_type in ('out_invoice', 'out_refund'))
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

    task_invoice_ids = fields.One2many('account.move', 'sale_task_id', 'Invoice')
    invoice_count = fields.Integer(string='Invoice Count', compute='_get_invoiced')
    add_information = fields.Html(string="Additional Information")

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_line_invoiced = fields.Boolean(string="Line Invoiced")
    done_qty_wizard = fields.Float(string="Done Qty Wizard")
    is_cancel_down_payment = fields.Boolean(string="Cancel Down Payment?")
    sale_task_invoiced = fields.Float(string="Invoiced", compute='_compute_sale_task_invoiced')

    @api.depends('done_qty_wizard')
    def _compute_sale_task_invoiced(self):
        for rec in self:
            rec.sale_task_invoiced = rec.done_qty_wizard

