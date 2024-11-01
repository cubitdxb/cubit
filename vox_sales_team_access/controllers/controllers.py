# -*- coding: utf-8 -*-
# from odoo import http


# class VoxSalesTeamAccess(http.Controller):
#     @http.route('/vox_sales_team_access/vox_sales_team_access', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_sales_team_access/vox_sales_team_access/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_sales_team_access.listing', {
#             'root': '/vox_sales_team_access/vox_sales_team_access',
#             'objects': http.request.env['vox_sales_team_access.vox_sales_team_access'].search([]),
#         })

#     @http.route('/vox_sales_team_access/vox_sales_team_access/objects/<model("vox_sales_team_access.vox_sales_team_access"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_sales_team_access.object', {
#             'object': obj
#         })
