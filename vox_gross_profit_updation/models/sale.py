from odoo import models, fields, api, _


class Updategrossprofit(models.TransientModel):
    _name = 'update.gross.profit'
    _description = 'Update Gross Profit'


    start_date = fields.Date('Start Period', required=True)
    end_date = fields.Date('End Period', required=True)


    def update_vendor_bills(self):
        res = {}
        search_condition = [('date_order', '>=', self.start_date), ('date_order', '<=', self.end_date)]
        purchase_orders = self.env['purchase.order'].search(search_condition)
        move = False
        move_count = 0
        move_list = []

        for order in purchase_orders:
            purchase_moves = self.env['account.move'].sudo().search(
                [('purchase_bill_id', '=', order.id)])

            purchase_invoice = [(4, move_line.id) for move_line in purchase_moves]
            exist_moves = [(4, existing_orders.id) for existing_orders in order.invoice_ids]
            all_invoices = list(set(exist_moves + purchase_invoice))
            order.invoice_ids = all_invoices
            order.invoice_count = len(order.invoice_ids)




    def update_invoice_quantity(self):
        res = {}
        search_condition = [('date_order', '>=', self.start_date), ('date_order', '<=', self.end_date),('id','=',12538)]
        sale_orders = self.env['sale.order'].search(search_condition)
        for sale in sale_orders:
            for line in sale.order_line:
                qty_invoiced = 0.0
                for invoice in sale.invoice_ids:
                    for invoice_line in invoice.invoice_line_ids:
                        if invoice_line.move_id.state != 'cancel' or invoice_line.move_id.payment_state == 'invoicing_legacy':
                            if invoice_line.move_id.move_type == 'out_invoice' and line.name==invoice_line.name:
                                qty_invoiced += invoice_line.product_uom_id._compute_quantity(invoice_line.quantity,
                                                                                              line.product_uom)
                            elif invoice_line.move_id.move_type == 'out_refund' and line.name==invoice_line.name:
                                qty_invoiced -= invoice_line.product_uom_id._compute_quantity(invoice_line.quantity,
                                                                                          line.product_uom)
                    line.qty_invoiced = qty_invoiced
        # for sale in sale_orders.order_line:
        #     sale._compute_qty_invoiced()


    # @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity', 'untaxed_amount_to_invoice')
    # def _compute_qty_invoiced(self):
    #     """
    #     Compute the quantity invoiced. If case of a refund, the quantity invoiced is decreased. Note
    #     that this is the case only if the refund is generated from the SO and that is intentional: if
    #     a refund made would automatically decrease the invoiced quantity, then there is a risk of reinvoicing
    #     it automatically, which may not be wanted at all. That's why the refund has to be created from the SO
    #     """
    #     for line in self:
    #         qty_invoiced = 0.0
    #         for invoice_line in line._get_invoice_lines():
    #             if invoice_line.move_id.state != 'cancel' or invoice_line.move_id.payment_state == 'invoicing_legacy':
    #                 if invoice_line.move_id.move_type == 'out_invoice':
    #                     qty_invoiced += invoice_line.product_uom_id._compute_quantity(invoice_line.quantity,
    #                                                                                   line.product_uom)
    #                 elif invoice_line.move_id.move_type == 'out_refund':
    #                     qty_invoiced -= invoice_line.product_uom_id._compute_quantity(invoice_line.quantity,
    #                                                                                   line.product_uom)
    #         line.qty_invoiced = qty_invoiced


    def update_gross_profit(self):
        search_condition = [('date_order', '>=', self.start_date),('date_order', '<=', self.end_date)]
        sale_orders = self.env['sale.order'].search(search_condition)
        task_obj = self.env['project.task']
        for order in sale_orders:
            purchase_tasks = False
            if order.project_id:
                for project in order.project_id:
                    purchase_tasks = task_obj.search(
                        [('project_id', '=', project.id), ('project_id', '!=', False), ('task_type', '=', 'is_purchase'),
                         ('purchase_ids', '!=', False)])
            if purchase_tasks:
                for task in purchase_tasks:
                    for purchase in task.purchase_ids:
                        if purchase.discount_amount:
                            order._compute_cost_price()


    def update_invoice_number(self):
        res = {}
        search_condition = [('date_order', '>=', self.start_date), ('date_order', '<=', self.end_date)]
        sale_orders = self.env['sale.order'].search(search_condition)
        for sale in sale_orders:
            if not sale.invoice_number:
                tot = 0.0
                not_invoiced = 0.0
                residual_amount = 0.0
                paid_invoice = 0.0
                invoice_amount = 0.0
                for invoice in sale.invoice_ids:
                    if invoice.state not in ('draft', 'cancel'):
                        if sale.invoice_number:
                            if invoice:
                                sale.invoice_number = sale.invoice_number + ', ' + invoice.name
                            else:
                                sale.invoice_number = sale.invoice_number
                        else:
                            sale.invoice_number = invoice.name

                        tot += invoice.amount_total
                        not_invoiced += invoice.amount_total
                        residual_amount += invoice.amount_residual
                        paid_invoice += invoice.amount_paid
                        invoice_amount += invoice.amount_total
                    sale.invoiced_amount = tot
                    sale.not_invoiced = sale.amount_total - not_invoiced
                    sale.amount_balance_due = residual_amount
                    sale.amount_paid_invoice = paid_invoice
                    sale.amount_invoice = invoice_amount

    # def update_total_amount(self):
    #         search_condition = [('date', '>=', self.start_date),('date', '<=', self.end_date),('payment_id.is_recociled','!=',True)]
    #         account = self.env['account.move'].search(search_condition)
    #         for order in account:
    #             if not order.amount_total_signed:
    #                 # order.line_ids.remove_move_reconcile()
    #                 # order.line_ids.remove_move_reconcile()
    #                 # order.line_ids.reconcile()
    #                 order._compute_amount()

