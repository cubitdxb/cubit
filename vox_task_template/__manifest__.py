# -*- coding: utf-8 -*-
{
    'name': "Project Templates",

    'summary': """
        Project and task templates""",

    'description': """
       Project & Task templates
    """,

    'author': "Jishnu K",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Services',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['project', 'documents_project', 'sale', 'crm_lead_fields', 'report_templates', 'report_xlsx',
                'purchase', 'stock', 'hr_timesheet', 'vox_user_groups', 'mail','purchase_stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'security/gross_profit_user.xml',
        'data/task_delivery_sequence.xml',
        'data/project_template.xml',
        'data/project_stages.xml',
        'data/ir_crone_data.xml',
        'data/project_stage_email_notification.xml',
        'data/sign_off_email_notification.xml',
        'data/mail_template.xml',
        'data/delivery_mail.xml',
        'data/purchase_amount_all_wrapper_server_action.xml',
        'data/sale_amount_all_wrapper_server_action.xml',
        'wizard/create_project.xml',
        'wizard/create_delivery.xml',
        'wizard/purchase_import_excel.xml',
        'wizard/create_purchase.xml',
        'wizard/update_option_discount_wiz_views.xml',
        'report/sign_off_document.xml',
        'report/repair_and_form_template.xml',
        'report/sale_project_task.xml',
        'report/delivery_note.xml',
        'report/delivery_note_for_renewal.xml',
        'report/delivery_note_for_customs.xml',
        'views/purchase.xml',
        'views/sale_order_inherit.xml',
        'views/project_task_inherit.xml',
        'views/project_project.xml',
        'views/task_delivery.xml',
        'views/task_delivery_line_views.xml',
        'views/purchase_delivery_line_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'license': 'LGPL-3',
}
