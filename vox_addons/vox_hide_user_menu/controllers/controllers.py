# -*- coding: utf-8 -*-
# from odoo import http


# class VoxHideUserMenu(http.Controller):
#     @http.route('/vox_hide_user_menu/vox_hide_user_menu', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_hide_user_menu/vox_hide_user_menu/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_hide_user_menu.listing', {
#             'root': '/vox_hide_user_menu/vox_hide_user_menu',
#             'objects': http.request.env['vox_hide_user_menu.vox_hide_user_menu'].search([]),
#         })

#     @http.route('/vox_hide_user_menu/vox_hide_user_menu/objects/<model("vox_hide_user_menu.vox_hide_user_menu"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_hide_user_menu.object', {
#             'object': obj
#         })
