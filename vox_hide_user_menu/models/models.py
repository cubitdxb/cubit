# -*- coding: utf-8 -*-
from odoo import models, fields, api,tools

class HideMenuUser(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        self.clear_caches()
        return super(HideMenuUser, self).create(vals)

    def write(self, vals):
        res = super(HideMenuUser, self).write(vals)
        for menu in self.hide_menu_ids:
            menu.write({
                'restrict_user_ids': [(4, self.id)]
            })
        self.clear_caches()
        return res

    def _get_is_admin(self):
        for rec in self:
            rec.is_admin = False
            if rec.id == self.env.ref('base.user_admin').id:
                rec.is_admin = True

    hide_menu_ids = fields.Many2many('ir.ui.menu', string="Menu", store=True)
    is_admin = fields.Boolean(compute=_get_is_admin)


class RestrictMenu(models.Model):
    _inherit = 'ir.ui.menu'
    restrict_user_ids = fields.Many2many('res.users')


# class Menu(models.Model):
#     _inherit = 'ir.ui.menu'
#
#     @api.model
#     @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
#     def _visible_menu_ids(self, debug=False):
#         menus = super(Menu, self)._visible_menu_ids(debug)
#         if self.env.user.hide_menu_access_ids and not self.env.user.has_group('base.group_system'):
#             for rec in self.env.user.hide_menu_access_ids:
#                 menus.discard(rec.id)
#             return menus
#         return menus



# class ResUsers(models.Model):
#     _inherit = 'res.users'
#
#     hide_menu_access_ids = fields.Many2many('ir.ui.menu', 'ir_ui_hide_menu_rel', 'uid', 'menu_id',
#                                             string='Hide Access Menu')
#
