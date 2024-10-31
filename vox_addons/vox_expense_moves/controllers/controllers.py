# -*- coding: utf-8 -*-
# from odoo import http


# class VoxExpenseMoves(http.Controller):
#     @http.route('/vox_expense_moves/vox_expense_moves', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_expense_moves/vox_expense_moves/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_expense_moves.listing', {
#             'root': '/vox_expense_moves/vox_expense_moves',
#             'objects': http.request.env['vox_expense_moves.vox_expense_moves'].search([]),
#         })

#     @http.route('/vox_expense_moves/vox_expense_moves/objects/<model("vox_expense_moves.vox_expense_moves"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_expense_moves.object', {
#             'object': obj
#         })
