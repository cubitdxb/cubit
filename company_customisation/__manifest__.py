# -*- coding: utf-8 -*-
{
    'name': "cubit_company_customization",

    'summary': """
        Cubit company customization""",

    'description': """
       Cubit company customizations
    """,

    'author': "Jishnu K",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['web', 'base','web_studio', 'stock','account_asset'],

    # always loaded
    'data': [
        'views/company.xml',
        'views/account_account.xml',
        'views/account_journal_inherit.xml',
        'views/account_tax_inherit.xml',
        'views/account_asset_inherit.xml',
        'views/bank_inherit.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
