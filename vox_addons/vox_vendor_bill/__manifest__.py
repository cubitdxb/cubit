{
    'name': "vox_vendor_bill",

    'summary': """
        vendor bill creation 
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Hilsha",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'uom','purchase', 'account','vox_task_invoice'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_wizard.xml',
        'wizard/purchase_creation_type.xml',

        'views/views.xml',
        'views/templates.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
# -*- coding: utf-8 -*-
