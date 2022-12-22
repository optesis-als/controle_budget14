# -*- coding : utf-8 -*-

{
    'name': 'Odoo Create Portal PO Request',
    'summary': """
        Odoo Create Portal PO Request""",
    'description': """
           Create Portal PO Request
           Create Vendor RFQ PO Request
        """,
    'author': "INTESLAR",
    'website': "www.inteslar",
    'category': 'purchase',
    'version': '14.3',
    'depends': [
        'website',
        'purchase',
        'portal',
        'hr'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/po_request_data.xml',
        'views/assets.xml',
        'views/portal_template.xml',
        'views/add_requests_quotation_template.xml',
        'views/edit_requests_quotation_template.xml',
        'views/add_thanking_you.xml',
        'views/request_purchase_views.xml',
        'views/purchase_order_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
