{
    'name': 'Purchase request for Control budget',
    'author': 'OPTESIS SA',
    'version': '14.0.0.0',
    'category': 'Tools',
    'description': """
Ce module permet de faire le control budgetairepour le secteur privé
""",
    'summary': 'Comptabilite',
    'sequence': 9,
    'depends': ['base','purchase_request'],
    'data': [
        'views/purchase_request_line_view.xml',
        'wizard/purchase_request_line_make_purchase_order_view.xml'
    ],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
