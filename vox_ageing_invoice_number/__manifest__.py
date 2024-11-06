# -*- coding: utf-8 -*-
{
    'name': "vox_ageing_invoice_number",

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
    'depends': ['base','account','report_xlsx','vox_payment_allocation','vox_task_invoice'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'data/data.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
