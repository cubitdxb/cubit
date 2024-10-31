# -*- coding: utf-8 -*-
# from odoo import http


# class VoxAgeingReportByInvoiceDate(http.Controller):
#     @http.route('/vox_ageing_report_by_invoice_date/vox_ageing_report_by_invoice_date', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_ageing_report_by_invoice_date/vox_ageing_report_by_invoice_date/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_ageing_report_by_invoice_date.listing', {
#             'root': '/vox_ageing_report_by_invoice_date/vox_ageing_report_by_invoice_date',
#             'objects': http.request.env['vox_ageing_report_by_invoice_date.vox_ageing_report_by_invoice_date'].search([]),
#         })

#     @http.route('/vox_ageing_report_by_invoice_date/vox_ageing_report_by_invoice_date/objects/<model("vox_ageing_report_by_invoice_date.vox_ageing_report_by_invoice_date"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_ageing_report_by_invoice_date.object', {
#             'object': obj
#         })
