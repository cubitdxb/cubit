# -*- coding: utf-8 -*-
{
    'name': "Vox Purchase Discount",

    'summary': """
        Purchase Discount""",

    'description': """
       Purchase Discount
    """,

    'author': "Hilsha P H",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Services',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['project', 'vox_task_template','vox_invoice_global_discount','vox_vendor_bill'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/data.xml',
        'views/purchase.xml',


    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'license': 'LGPL-3',
}
