# -*- coding: utf-8 -*-

from odoo.exceptions import AccessError, MissingError
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class PurchaseCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'purchase_rfq_count' in counters:
            user_id = request.env.user.id
            values['purchase_rfq_count'] = request.env['rfq.purchase.requests'].search_count([
                ('rfq_created_by_id_prsit', "=", user_id)
            ]) if request.env['rfq.purchase.requests'].check_access_rights('read', raise_exception=False) else 0
        return values

    @http.route(['/my/purchase_rfq'], type='http', auth="user", website=True)
    def portal_my_purchase_rfqs(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        user_id = request.env.user.id
        PurchaseOrder = request.env['rfq.purchase.requests']

#        domain = [('is_created_from_webrfq_prsit', '=', True), ('rfq_created_by_id_prsit', "=", user_id)]
        domain = [('rfq_created_by_id_prsit', "=", user_id)]

        orders = PurchaseOrder.sudo().search(domain)
        request.session['my_purchases_rfq_history'] = orders.ids[:100]

        values.update({
            'purchase_rfqs': orders,
            'page_name': 'purchase_rfq',
            'default_url': '/my/purchase_rfq',
        })
        return request.render("odoo_create_portal_po_request.portal_my_purchase_rfqs", values)

    @http.route(['/my/purchase_rfq/<int:order_id>'], type='http', auth="public", website=True)
    def portal_my_purchase_rfq(self, order_id=None, access_token=None, **kw):
        try:
            order_sudo = self._document_check_access('rfq.purchase.requests', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = {
            'purchase_rfq': order_sudo,
            'purchase_form': True,
            'default_url': '/my/purchase_rfq',
        }
        return request.render("odoo_create_portal_po_request.portal_my_purchase_rfq", values)
