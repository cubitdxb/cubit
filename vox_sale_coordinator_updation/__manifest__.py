# -*- coding: utf-8 -*-
##############################################################################
#
#    VOXTRON SOLUTIONS LLP.
#    Copyright (C) 2017-TODAY VOXTRON SOLUTIONS (<http://www.voxtronme.com>).
#    Author: Hilsha(<http://www.voxtronme.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Update Sales Coordinator',
    'version': '15.0.1.0.0',
    'summary': 'Update Sales Coordinator',
    'description': 'This module helps you to Update Sales Coordinator',
    'category': 'Sales',
    'author': 'Hilsha P H ',
    'website': 'http://www.voxtronme.com',
    'company': 'Voxtron Solutions',
    'depends': ['sale','vox_sales_team_access'],
    'data': [
             'security/ir.model.access.csv',
             'views/sale_views.xml',
             ],
    'css': [],
    'images': [],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}