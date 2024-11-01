# -*- coding: utf-8 -*-
{
    'name': "Add task In Invoice",

    'summary': """
        Add Task In invoice""",

    'description': """
        Add Task In invoice
    """,

    'author': "Hilsha",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Project',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'vox_task_template'],

    # always loaded
    'data': [

        'security/ir.model.access.csv',
        'views/task.xml',

    ],

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
}
