# -*- coding: utf-8 -*-
# from odoo import http


# class VoxApproveMargin(http.Controller):
#     @http.route('/vox_approve_margin/vox_approve_margin', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_approve_margin/vox_approve_margin/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_approve_margin.listing', {
#             'root': '/vox_approve_margin/vox_approve_margin',
#             'objects': http.request.env['vox_approve_margin.vox_approve_margin'].search([]),
#         })

#     @http.route('/vox_approve_margin/vox_approve_margin/objects/<model("vox_approve_margin.vox_approve_margin"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_approve_margin.object', {
#             'object': obj
#         })
