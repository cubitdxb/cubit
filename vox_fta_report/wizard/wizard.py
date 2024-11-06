from odoo import models, fields, api


class FTA_Report(models.TransientModel):
    _name = "fta.report.xls"
    _description = " FTA Report"

    date_start = fields.Date('Date', required=True,default=fields.Date.context_today)
    date_end = fields.Date('Date End',required=True,default=fields.Date.context_today)
    company_id = fields.Many2one('res.company', required=True,string='Company',default=lambda self: self.env.company)
    report_id = fields.Selection([
        ('std_rated_sales', 'Std Rated Sales'),
        ('out_of_scope_sales', 'Out of scope Sales'),
        ('tourist_refund_adj', 'Tourist Refund Adj'),
        ('import_of_services', 'Import of Services'),
        ('zero_rated_sales', 'Zero Rated Sales'),
        ('exempt_supplies', 'Exempt Supplies'),
        ('goods_imported_into_uae', 'Goods Imported into UAE'),
        ('adjustment_goods_import', 'Adjustment - Goods Import'),
        ('std_rated_purchases', 'Std Rated Purchases'),
        ('supplies_subjected_to_rcm', 'Supplies subject to RCM'),

    ],
        string='Report', default='soft', required=True)

    tax_ids = fields.Many2many('account.tax', required=True, string='TAX')

    def print_xls_report(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'account.move'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]

        return self.env.ref('vox_fta_report.std_rated_sale_report_xls').report_action(self, data=datas)
    #

    # def print_xls_report(self, context=None):
    #     context = self._context
    #     datas = {'ids': context.get('active_ids', [])}
    #     datas['model'] = 'fta.report.xls'
    #     datas['form'] = self.read()[0]
    #     return self.env.ref('vox_fta_report.std_rated_sale_report_xls').report_action(self, data=datas)


