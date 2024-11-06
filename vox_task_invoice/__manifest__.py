# -*- coding: utf-8 -*-
{
    'name': "vox_task_invoice",

    'summary': """
        Create Invoice from task""",

    'description': """
        Invoice creation from task
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_timesheet', 'account', 'vox_task_template', 'vox_sales_team_access',
                'vox_invoice_global_discount', 'l10n_ae'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'wizard/sale_order_line_edit_view.xml',
        'wizard/create_invoice.xml',
        'wizard/recipient_bank_account.xml',
        'wizard/sale_make_invoice_advance_views.xml',
        'views/account_tax.xml',
        'views/tracker_selection.xml',
        'views/task.xml',
        'views/check_tracker.xml',
        'views/invoice.xml',
        'views/templates.xml',
        'views/sale_views.xml',
        'views/tracker_dashboard.xml',
        'views/purchase_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
