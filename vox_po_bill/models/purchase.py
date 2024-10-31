# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # def _create_invoices_vals(self):
    #     invoice_lines = []
    #     for line in self.order_line:
    #         vals = {
    #             'name': line.name,
    #             'price_unit': line.price_unit,
    #             'quantity': line.product_qty,
    #             'product_uom_id': line.product_uom.id,
    #             'tax_ids': [(6, 0, line.taxes_id.ids)],
    #             'sale_layout_cat_id': line.sale_layout_cat_id.id,
    #             'part_number': line.part_number,
    #             'purchase_line_id':line.id,
    #         }
    #         invoice_lines.append((0, 0, vals))
    #     if invoice_lines:
    #         for order in self:
    #             self.env['account.move'].create({
    #                 'project_id': order.project_id.id,
    #                 'task_id': order.task_id.id,
    #                 'move_type': 'in_invoice',
    #                 'invoice_origin': order.name,
    #                 'invoice_user_id': order.user_id.id,
    #                 'partner_id': order.partner_id.id,
    #                 # 'currency_id': order.pricelist_id.currency_id.id,
    #                 'invoice_line_ids': invoice_lines,
    #             })
    #     return

    def send_mail_sales_person(self):
        template = self.env.ref('vox_po_bill.po_confirmation_mail_to_sale_person')
        if template:
            for order in self:
                email_values = {'email_to': order.sale_id.user_id.email, 'recipient_ids': []}
                if template:
                    template.send_mail(order.id, force_send=True, email_values=email_values)
        return

    def button_confirm(self):
        print(33333333333333333333333333333333333333333)
        res = super().button_confirm()
        # self._create_invoices_vals()
        for rec in self.order_line:
            sale_line_id = self.env['sale.order.line'].browse(rec.sale_line_id.id)
            sale_line_id.is_purchase_confirmed = True
            # if rec.product_qty == sale_line_id.product_uom_qty:
            #     print('purchase count is same')
            #     sale_line_id.fully_purchased = True
            if 0 < rec.product_qty < sale_line_id.product_uom_qty:
                print('partially confirmed')
                sale_line_id.partially_purchased = True
            # if rec.product_qty == 0:
            #     print('not purchased')
            #     sale_line_id.not_purchased = True
            print(rec.sale_line_id, 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeddddddddddddddddddddddddddd')

        self.send_mail_sales_person()
        return res