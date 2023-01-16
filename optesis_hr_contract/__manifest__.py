# -*- coding: utf-8 -*-
{
    'name': "optesis_hr_contract",

    'version': '14.0.0',
    'author': 'Optesis ',
    'category': 'Contrat des employés',
    'description': """
Moteur contrat optesis
=====================
                    """,
    'website': 'http://www.optesis.com',
    'depends': ['hr', 'base'],

    # always loaded
    'data': [
       'security/security.xml',
        'security/ir.model.access.csv',
        'data/hr_contract_data.xml',
        'views/hr_contract_views.xml',
        'views/hr_employee.xml',
        'data/sequence.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
