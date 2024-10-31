# -*- coding: utf-8 -*-
{
    'name': "Cubit CRM Reports",

    'summary': """
        Cubit CRM Reports""",

    'description': """
       Cubit CRM Reports
    """,

    'author': "Sangeetha S",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'CRM',
    'version': '15.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['crm', 'crm_lead_fields','report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/sales_consolidated_report_wiz.xml',
        'wizard/lead_presales_wiz.xml',
        'wizard/business_operation_wiz.xml',
        'wizard/cisco_report_wiz.xml',
        'wizard/consolidated_projects_wiz.xml',
        'wizard/project_tracker_wiz.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
