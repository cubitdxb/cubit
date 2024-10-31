# -*- coding: utf-8 -*-
# from odoo import http


# class VoxDefaultTaskStages(http.Controller):
#     @http.route('/vox_default_task_stages/vox_default_task_stages', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vox_default_task_stages/vox_default_task_stages/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('vox_default_task_stages.listing', {
#             'root': '/vox_default_task_stages/vox_default_task_stages',
#             'objects': http.request.env['vox_default_task_stages.vox_default_task_stages'].search([]),
#         })

#     @http.route('/vox_default_task_stages/vox_default_task_stages/objects/<model("vox_default_task_stages.vox_default_task_stages"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vox_default_task_stages.object', {
#             'object': obj
#         })
