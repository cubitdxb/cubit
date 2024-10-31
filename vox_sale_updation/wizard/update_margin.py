# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class margin_update_wizard(models.TransientModel):
    _name = "margin.update.wizard"

    name = fields.Char(string='Name')
    sale_id = fields.Many2one('sale.order', string='Sale')
    margin_change = fields.Float(string='Change(%)')
    type = fields.Selection([('add', 'Add'), ('subtract', 'Subtract')], string='Operation',default='add')
    # sale_layout_cat_id = fields.Many2one('sale_layout.category', string='Section')


    # @api.onchange('sale_id')
    def onchange_sale_id(self):
        domain = {}
        section_ids = []
        # for orders in self:
        #     if orders.sale_id:
        order = self.env['sale.order'].browse(self._context.get('active_id'))
        sale = self.env['sale.order'].browse(order.id)
        section_ids = []
        for line in sale.order_line:
            if line.sale_layout_cat_id:
                section_ids.append(line.sale_layout_cat_id.id)
        section_ids = list(set(section_ids))
        # domain = {'sale_layout_cat_id': [('id', 'in', section_ids)]}
        return [('id', 'in', section_ids)]
        # return {'domain': domain}

    sale_layout_cat_id = fields.Many2one('sale_layout.category', string='Section',domain=onchange_sale_id)


    def make_margin_change(self):
        # context = context or {}
        # sale_id = context.get('active_id', False)
        sale_id = self._context.get('active_id')
        for obj in self:
            domain = [('order_id', '=', sale_id)]
            type = obj.type
            margin_change = obj.margin_change
            if obj.sale_layout_cat_id:
                domain.append(('sale_layout_cat_id', '=', obj.sale_layout_cat_id.id))
            sale_line_ids = self.env['sale.order.line'].search(domain)
            for line in self.env['sale.order.line'].browse(sale_line_ids.ids):
                margin = line.margin
                if type == 'add':
                    new_margin = margin + margin_change
                if type == 'subtract':
                    new_margin = margin - margin_change
                line.write({'margin': new_margin})
                line._onchange_margin_value()
                # self.env['sale.order.line'].write({'margin': new_margin})
        return True

    @api.model
    def _prepare_default_get(self, order):
        default = {
            'sale_id': order.id,
        }
        return default

    @api.model
    def default_get(self, fields):
        res = super(margin_update_wizard, self).default_get(fields)
        assert self._context.get('active_model') == 'sale.order', \
            'active_model should be sale.order'
        order = self.env['sale.order'].browse(self._context.get('active_id'))
        default = self._prepare_default_get(order)
        res.update(default)
        return res

