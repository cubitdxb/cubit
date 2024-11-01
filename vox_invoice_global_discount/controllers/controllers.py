# -*- coding: utf-8 -*-
# from odoo import http


# class VoxInvoiceGlobalDiscount(http.Controller):
#     @http.route('/vox_invoice_global_discount/vox_invoice_global_discount', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_invoice_global_discount/vox_invoice_global_discount/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_invoice_global_discount.listing', {
#             'root': '/vox_invoice_global_discount/vox_invoice_global_discount',
#             'objects': http.request.env['vox_invoice_global_discount.vox_invoice_global_discount'].search([]),
#         })

#     @http.route('/vox_invoice_global_discount/vox_invoice_global_discount/objects/<model("vox_invoice_global_discount.vox_invoice_global_discount"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_invoice_global_discount.object', {
#             'object': obj
#         })
