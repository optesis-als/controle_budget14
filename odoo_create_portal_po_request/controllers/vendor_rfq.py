# -*- coding : utf-8 -*-

from odoo.addons.website.controllers.main import Website
from odoo import http
from odoo.http import request


class AddVendorRfq(http.Controller):

    @http.route('/add_vendor_rfq', type='http', auth='user', website=True)
    def prsit_add_po_rfq(self, **kwargs):
        #Partners = request.env['res.partner'].search([])
        approvers = request.env['hr.employee'].sudo().search([])
        Products = request.env['product.product'].sudo().search([])
        values = {
            'products': Products,
            #'partners': Partners,
            'approvers': approvers,
        }
        return request.render("odoo_create_portal_po_request.add_po_request_form", values)

    @http.route('/edit_vendor_rfq', type='http', auth='user', website=True)
    def prsit_edit_po_rfq(self, **kwargs):
        if kwargs.get('order_id'):
            order_id = int(kwargs.get('order_id', False))
            Partners = request.env['res.partner'].search([])
            approvers = request.env['hr.employee'].sudo().search([])
            Products = request.env['product.product'].sudo().search([])
            values = {
                'products': Products,
                #'partners': Partners,
                'approvers': approvers,
            }
            rfq_purchase = request.env['rfq.purchase.requests'].sudo().browse(order_id)
            values.update({'rfq_purchase': rfq_purchase})
        return request.render('odoo_create_portal_po_request.edit_po_request_form', values)

    @http.route('/submit/vendor/rfq', type='http', auth="user", website=True)
    def prsit_submit_po_rfq(self, **kwargs):
        if kwargs:
            user_id = request.env.user
            #partner_id = int(kwargs.get('partner_id', '1'))
            approver_id = int(kwargs.get('approver_id', '1'))
            date_order = kwargs.get('date_order')
            seq = int(kwargs.get("seq", '0'))
            po_vals = {
                #'partner_id': partner_id,
                'partner_id': user_id.partner_id.id,
                'approver_id': approver_id,
                'is_created_from_webrfq_prsit': True,
                'rfq_created_by_id_prsit': user_id.id,
                'date_order': date_order,
            }
            product_qty_list = []

            for seq_id in range(1, seq + 1):
                if kwargs.get("product_id_{}".format(seq_id)):
                    product_qty_list.append((0, 0, {
                        'name': kwargs.get("description_{}".format(seq_id), False),
                        'product_id': int(kwargs.get("product_id_{}".format(seq_id), False)),
                        'product_qty': int(kwargs.get("quantity_{}".format(seq_id), False)),
                    }))

            if not kwargs.get('rfq_purchase_requests_id'):

                po_vals.update({'order_line': product_qty_list})
                po = request.env['rfq.purchase.requests'].sudo().create(po_vals)
                values = {
                    'purchaseOrder': po
                }

            elif kwargs.get('rfq_purchase_requests_id'):
                order_id = int(kwargs.get('rfq_purchase_requests_id', False))
                rfq_purchase_requests = request.env['rfq.purchase.requests'].sudo().browse(order_id)

                for line in rfq_purchase_requests.order_line:
                    if kwargs.get("product_id_{}".format(line.id)):
                        product_qty_list.append((1, line.id, {
                            'name': kwargs.get("description_{}".format(line.id), False),
                            'product_id': int(kwargs.get("product_id_{}".format(line.id), False)),
                            'product_qty': float(kwargs.get("quantity_{}".format(line.id), False)),
                        }))
                    else:
                        product_qty_list.append((2, line.id, 0))

                po_vals.update({'order_line': product_qty_list})
                rfq_purchase_requests.write(po_vals)
                values = {
                    'purchaseOrder': rfq_purchase_requests.id
                }
            return request.render('odoo_create_portal_po_request.po_thanks_template', values)
        else:
            return request.redirect("/")


