## -*- coding: utf-8 -*-
###################################################################################
#
#    Copyright (C) 2018-TODAY Opteis (<https://www.optesis.com>).
#    Author: Treesa Maria Jude  (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#                                                                                 
###################################################################################

{
    'name': 'optesis_hr_contract_sn',
    'version': '14.0.0',
    'summary': """""",
    'description': """""",
    'category': 'Human Resources',
    'author': 'Optesis SA,',
    'maintainer': 'Optesis',
    'company': 'Optesis SA',
    'website': 'https://www.moore.sn',
    'depends': [
                'optesis_hr_contract',
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_view.xml',
        'views/contract_view.xml',
        'views/convention_collective_views.xml',
        'report/custom_report_contrat.xml',
        'report/contrat_cdd.xml',
        'report/contrat_cdi.xml',
        'report/contrat_dmt_internal_report.xml',
        'report/custom_report.xml',
        'views/company_inherit.xml',
        'report/report.xml'
              ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

