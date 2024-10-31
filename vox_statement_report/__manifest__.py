# -*- coding: utf-8 -*-
{
    'name': "vox_statement_report",

    'summary': """
        Add Project Reference and Lpo number in Follow Up report""",

    'description': """
        	Changes in Print Follow-up Letter 
    """,

    'author': "Hilsha",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_followup','account_reports'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/date_view.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/statement.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'assets': {
        'account_followup.assets_followup_report': [
            'vox_statement_report/static/src/scss/style.scss',
        ],
    },
    # 'assets': {
    #
    #     'web.assets_backend': [
    #         'vox_statement_report/static/src/js/**/*',
    #
    #     ],
    #
    #     'web.assets_qweb': [
    #         'vox_statement_report/static/src/xml/**/*',
    #     ],
    # },
'license': 'LGPL-3',
}
