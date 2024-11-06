# -*- coding: utf-8 -*-
# from odoo import http


# class VoxTaskInvoice(http.Controller):
#     @http.route('/vox_task_invoice/vox_task_invoice', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_task_invoice/vox_task_invoice/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_task_invoice.listing', {
#             'root': '/vox_task_invoice/vox_task_invoice',
#             'objects': http.request.env['vox_task_invoice.vox_task_invoice'].search([]),
#         })

#     @http.route('/vox_task_invoice/vox_task_invoice/objects/<model("vox_task_invoice.vox_task_invoice"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_task_invoice.object', {
#             'object': obj
#         })
