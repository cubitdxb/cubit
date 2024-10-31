# -*- coding: utf-8 -*-
# from odoo import http


# class ContactDetailsFields(http.Controller):
#     @http.route('/contact_details_fields/contact_details_fields', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contact_details_fields/contact_details_fields/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('contact_details_fields.listing', {
#             'root': '/contact_details_fields/contact_details_fields',
#             'objects': http.request.env['contact_details_fields.contact_details_fields'].search([]),
#         })

#     @http.route('/contact_details_fields/contact_details_fields/objects/<model("contact_details_fields.contact_details_fields"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contact_details_fields.object', {
#             'object': obj
#         })
