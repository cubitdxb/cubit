# -*- coding: utf-8 -*-
# from odoo import http


# class VoxSaleFields(http.Controller):
#     @http.route('/vox_sale_fields/vox_sale_fields', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_sale_fields/vox_sale_fields/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_sale_fields.listing', {
#             'root': '/vox_sale_fields/vox_sale_fields',
#             'objects': http.request.env['vox_sale_fields.vox_sale_fields'].search([]),
#         })

#     @http.route('/vox_sale_fields/vox_sale_fields/objects/<model("vox_sale_fields.vox_sale_fields"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_sale_fields.object', {
#             'object': obj
#         })
