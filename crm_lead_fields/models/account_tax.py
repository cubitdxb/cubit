from odoo import fields, models, api, _
class AccountTax(models.Model):
    _inherit = "account.tax"

    sale_add_tax = fields.Boolean("Add Tax in Sale")