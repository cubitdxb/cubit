# -*- coding: utf-8 -*-
{
    'name': "vox_sales_team_access",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sales_team', 'crm_lead_fields', 'vox_task_template', 'vox_user_groups', 'purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',

        'security/security.xml',
        'data/data.xml',
        'views/partner.xml',
        'views/assign_manager.xml',
        'views/views.xml',
        'views/sale_team.xml',
        'views/templates.xml',
        'views/res_users.xml',
        'views/cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
