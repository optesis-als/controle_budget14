## -*- coding : utf-8 -*-

#from odoo.addons.website.controllers.main import Website
#from odoo import http
#from odoo.http import request


#class AddRFQ(http.Controller):
#    @http.route('/add_rfq', type='http', auth='user', website=True)
#    def prsit_add_po_rfq(self, **kwargs):
#        if not kwargs:
#            Partners = request.env['res.partner'].search([])
#            Products = request.env['product.product'].search([])
#            values = {
#                'products': Products,
#                'partners': Partners,
#            }
#            return request.render("odoo_create_portal_po_request.add_po_request_form", values)


#class SubmitRFQ(Website):
#    @http.route('/submit/rfq', type='http', auth="user", website=True)
#    def prsit_submit_po_rfq(self, **kwargs):
#        if kwargs:
#            user_id = request.env.user.id
#            partner_id = int(kwargs.get('partner_id', False))
#            seq = int(kwargs.get("seq", False))

#            po_vals = {
#                'partner_id': partner_id,
#                'is_created_from_webrfq_prsit': True,
#                'rfq_created_by_id_prsit': user_id,
#           }
#            product_qty_list = []

#            for seq_id in range(1, seq+1):
#                product_qty_list.append((0, 0, {
#                    'name': kwargs.get("description_{}".format(seq_id), False),
#                    'product_id': int(kwargs.get("product_id_{}".format(seq_id), False)),
#                    'product_qty': int(kwargs.get("quantity_{}".format(seq_id), False)),
#                }))

#            po_vals.update({'order_line': product_qty_list})
#            request.env['rfq.purchase.requests'].create(po_vals)

#            return request.redirect('/po/contactus-thank-you')
