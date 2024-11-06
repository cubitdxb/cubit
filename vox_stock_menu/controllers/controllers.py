# -*- coding: utf-8 -*-
# from odoo import http


# class VoxStockMenu(http.Controller):
#     @http.route('/vox_stock_menu/vox_stock_menu', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_stock_menu/vox_stock_menu/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_stock_menu.listing', {
#             'root': '/vox_stock_menu/vox_stock_menu',
#             'objects': http.request.env['vox_stock_menu.vox_stock_menu'].search([]),
#         })

#     @http.route('/vox_stock_menu/vox_stock_menu/objects/<model("vox_stock_menu.vox_stock_menu"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_stock_menu.object', {
#             'object': obj
#         })
