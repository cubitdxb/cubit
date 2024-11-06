# -*- coding: utf-8 -*-
# from odoo import http


# class VoxRenewalCategory(http.Controller):
#     @http.route('/vox_renewal_category/vox_renewal_category', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_renewal_category/vox_renewal_category/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_renewal_category.listing', {
#             'root': '/vox_renewal_category/vox_renewal_category',
#             'objects': http.request.env['vox_renewal_category.vox_renewal_category'].search([]),
#         })

#     @http.route('/vox_renewal_category/vox_renewal_category/objects/<model("vox_renewal_category.vox_renewal_category"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_renewal_category.object', {
#             'object': obj
#         })
