# -*- coding: utf-8 -*-
# from odoo import http


# class VoxVendorBill(http.Controller):
#     @http.route('/vox_vendor_bill/vox_vendor_bill', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_vendor_bill/vox_vendor_bill/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_vendor_bill.listing', {
#             'root': '/vox_vendor_bill/vox_vendor_bill',
#             'objects': http.request.env['vox_vendor_bill.vox_vendor_bill'].search([]),
#         })

#     @http.route('/vox_vendor_bill/vox_vendor_bill/objects/<model("vox_vendor_bill.vox_vendor_bill"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_vendor_bill.object', {
#             'object': obj
#         })
