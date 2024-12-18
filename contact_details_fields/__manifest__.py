# -*- coding: utf-8 -*-
{
    'name': "Contact Details",

    'summary': """
        Contact Fields in form view""",

    'description': """
       Add fields in contact view
    """,

    'author': "Hilsha",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Contact',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','sale','web','hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
    'web.assets_backend': [
    'contact_details_fields/static/src/js/base_view.js',
    'contact_details_fields/static/src/scss/style.scss',
        ],
    },
    'license': 'LGPL-3',
}
