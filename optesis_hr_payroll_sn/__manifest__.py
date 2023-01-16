# -*- coding: utf-8 -*-
{
    'name': "optesis_hr_payroll_sn",

    'summary': """
        Détail des règles de calcul de paie applicables au Sénégal
""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'optesis_hr_contract','optesis_hr_payroll', 'optesis_hr_contract_sn'],

    # always loaded
    'data': [
         'security/ir.model.access.csv',
        'data/hr_payroll_category.xml',
        'data/salary_rule_data.xml',
        'views/hr_contract.xml',
        
        'views/payroll_chart_template_views.xml',
        'data/chart_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
