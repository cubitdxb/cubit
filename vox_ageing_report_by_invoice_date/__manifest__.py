# -*- coding: utf-8 -*-
{
    'name': "vox_ageing_report_by_invoice_date",

    'summary': """
       Receivable and payable Report by Invoice date""",

    'description': """
         Receivable and payable Report by Invoice date
    """,

    'author': "Hilsha P H",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_reports','vox_ageing_report_interval'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
