# -*- coding: utf-8 -*-
# from odoo import http


# class VoxUserGroups(http.Controller):
#     @http.route('/vox_user_groups/vox_user_groups', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_user_groups/vox_user_groups/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_user_groups.listing', {
#             'root': '/vox_user_groups/vox_user_groups',
#             'objects': http.request.env['vox_user_groups.vox_user_groups'].search([]),
#         })

#     @http.route('/vox_user_groups/vox_user_groups/objects/<model("vox_user_groups.vox_user_groups"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_user_groups.object', {
#             'object': obj
#         })
