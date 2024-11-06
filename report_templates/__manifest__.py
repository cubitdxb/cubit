# -*- coding: utf-8 -*-
{
    'name': "Sale Report Templates",

    'summary': """
        Sale Report templates""",

    'description': """
       Sales report templates
    """,

    'author': "Jishnu K",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'crm_lead_fields', 'company_customisation'],

    # always loaded
    'data': [
        'report/layout.xml',
        'report/cb_common.xml',
        'report/business_proposal_template.xml',
        'report/contract_order.xml',
        'report/contract_order_sl_no.xml',
        'report/quotation_order.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
