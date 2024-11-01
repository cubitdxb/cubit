# -*- coding: utf-8 -*-
{
    'name': "Disable Required Fields",

    'summary': """
        Disable Required Fields""",

    'description': """
       Disable Required Fields
    """,

    'author': "Hilsha P H",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Services',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['project','account', 'vox_task_template','contact_details_fields','vox_task_invoice','crm_lead_fields'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase.xml',
        'views/sale.xml',
        'views/lead.xml',
        'views/project.xml',
        'views/partner.xml',
        'views/invoice.xml',


    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'license': 'LGPL-3',
}
