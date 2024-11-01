# -*- coding: utf-8 -*-
# from odoo import http


# class VoxAgeingReportInterval(http.Controller):
#     @http.route('/vox_ageing_report_interval/vox_ageing_report_interval', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_ageing_report_interval/vox_ageing_report_interval/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_ageing_report_interval.listing', {
#             'root': '/vox_ageing_report_interval/vox_ageing_report_interval',
#             'objects': http.request.env['vox_ageing_report_interval.vox_ageing_report_interval'].search([]),
#         })

#     @http.route('/vox_ageing_report_interval/vox_ageing_report_interval/objects/<model("vox_ageing_report_interval.vox_ageing_report_interval"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_ageing_report_interval.object', {
#             'object': obj
#         })
