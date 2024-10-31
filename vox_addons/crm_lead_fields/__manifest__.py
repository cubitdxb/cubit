# -*- coding: utf-8 -*-
{
    'name': "CRM fields",

    'summary': """
        Add Extra fields in CRM view""",

    'description': """
        Add field in CRM view
    """,

    'author': "Hilsha",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'CRM',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'sale', 'sale_crm', 'purchase', 'project', 'account', 'contact_details_fields',
                'sales_team', 'crm_enterprise','sale_project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'data/crm_stage.xml',
        'data/ir_cron_data.xml',
        'data/presale_not_done_l3_l4_mail.xml',
        'data/sale_person_mail.xml',

        'views/tables_views.xml',
        'views/account_tax.xml',
        'views/crm_stage.xml',
        'views/sale_import.xml',
        'views/lead_views.xml',
        'views/user_target.xml',
        'views/templates.xml',
        'views/sale_views.xml',
        'views/sale_name.xml',
        'views/crm_sale_team.xml',
        'views/dashboard_view.xml',
        'data/table_data.xml',
        'wizard/end_user_required_conditions_views.xml',

    ],
    'assets': {

        'web.assets_qweb': [
            'crm_lead_fields/static/src/xml/**/*',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
