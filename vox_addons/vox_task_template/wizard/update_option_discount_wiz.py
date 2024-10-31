from odoo import models, fields, _
from odoo.exceptions import ValidationError


class UpdateOptionDiscount(models.TransientModel):
    _name = 'update.option.discount'

    def make_option_discount_update(self):
        for opt in self.option_wise_discount_ids:
            for line in opt.option_discount_id.sale_id.order_line.filtered(lambda a: a.options == opt.name):
                if not 0 <= (opt.discount+line.discount) <= 100.0:
                    raise ValidationError(_('Enter proper discount'))
                line.option_discount = (line.product_uom_qty * line.unit_price)*opt.discount/100.0 \
                    if opt.discount else 0.0

    sale_id = fields.Many2one('sale.order', string="Sale Order")
    option_wise_discount_ids = fields.One2many('update.option.discount.line', 'option_discount_id',
                                               string="Option Wise Discount Items")


class UpdateOptionDiscountLine(models.TransientModel):
    _name = 'update.option.discount.line'

    name = fields.Char(string="Option")
    discount = fields.Float(string="Discount")
    option_discount_id = fields.Many2one('update.option.discount')
