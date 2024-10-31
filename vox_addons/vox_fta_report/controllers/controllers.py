# -*- coding: utf-8 -*-
# from odoo import http


# class VoxFtaReport(http.Controller):
#     @http.route('/vox_fta_report/vox_fta_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_fta_report/vox_fta_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_fta_report.listing', {
#             'root': '/vox_fta_report/vox_fta_report',
#             'objects': http.request.env['vox_fta_report.vox_fta_report'].search([]),
#         })

#     @http.route('/vox_fta_report/vox_fta_report/objects/<model("vox_fta_report.vox_fta_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_fta_report.object', {
#             'object': obj
#         })
