# -*- coding: utf-8 -*-
# from odoo import http


# class VoxStatementReport(http.Controller):
#     @http.route('/vox_statement_report/vox_statement_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_statement_report/vox_statement_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_statement_report.listing', {
#             'root': '/vox_statement_report/vox_statement_report',
#             'objects': http.request.env['vox_statement_report.vox_statement_report'].search([]),
#         })

#     @http.route('/vox_statement_report/vox_statement_report/objects/<model("vox_statement_report.vox_statement_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_statement_report.object', {
#             'object': obj
#         })
