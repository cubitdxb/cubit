# -*- coding: utf-8 -*-
# from odoo import http


# class CrmLeadFields(http.Controller):
#     @http.route('/crm_lead_fields/crm_lead_fields', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_lead_fields/crm_lead_fields/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_lead_fields.listing', {
#             'root': '/crm_lead_fields/crm_lead_fields',
#             'objects': http.request.env['crm_lead_fields.crm_lead_fields'].search([]),
#         })

#     @http.route('/crm_lead_fields/crm_lead_fields/objects/<model("crm_lead_fields.crm_lead_fields"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_lead_fields.object', {
#             'object': obj
#         })
