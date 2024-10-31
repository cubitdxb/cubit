##############################################################################

from odoo import models,fields,api,_

class Cheque_tracker(models.Model):
    _name = "check.tracker"
    _description = "Check Tracker"

    cubit_id = fields.Integer(string="Cubit ID")
    name = fields.Char(string="name")
    serial_number = fields.Integer(string="Serial Number")
    issued_date = fields.Date(string="Issue Date")
    cheque_date = fields.Date(string="Cheque Date")
    # party_name = fields.Char(string="Party Name")
    party_name = fields.Many2one('res.partner',string="Party Name",domain="[('supplier', '=', True)]")
    cheque_amount = fields.Integer(string="Cheque Amount")
    cheque_number = fields.Char(string="Cheque Number")
    # supplier_po_number = fields.Char(string="Supplier PO Number")
    supplier_po_number = fields.Many2one('purchase.order',string="Supplier PO Number")
    # sale_order_number = fields.Char(string="Sale Order No")
    sale_order_number = fields.Many2one('sale.order',string="Sale Order No")
    customer_name = fields.Many2one('res.partner',string="Customer name",domain="[('customer', '=', True)]")
    remark = fields.Char(string="Remarks")
    bank = fields.Many2one('res.bank',string="Bank")
    status = fields.Many2one('cheque.tracker.selection',string="Status")


class Cheque_tracker_selection(models.Model):
    _name = "cheque.tracker.selection"
    _description = "Check Tracker Selection"

    cubit_id = fields.Integer(string="Cubit ID")
    name = fields.Char(string="Name")


