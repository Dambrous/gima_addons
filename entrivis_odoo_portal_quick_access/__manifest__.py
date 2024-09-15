# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2020-Today Entrivis Tech PVT. LTD. (<http://www.entrivistech.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
{
    'name': "Odoo Portal Quick Menu Access",
    'category': 'Website/Website',
    "summary": """Document menu access for website pages on the customer portal.""",
    'version': "17.0.1.0",
    "description": "This module is used to access document menu for website pages on the Customer Portal.",
    'website': "www.entrivistech.com",
    'author': 'Entrivis Tech Pvt. Ltd.',
    'maintainer': 'Entrivis Tech Pvt. Ltd.',
    'depends': ['portal', 'website'],
    'data': [
        'views/portal_template_view.xml',
        'views/res_company_view.xml',
        'views/res_config_settings_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'currency': 'USD',
    'license': 'OPL-1',
    'images': ['static/description/odoo-quick-portal-access.png'],
}
