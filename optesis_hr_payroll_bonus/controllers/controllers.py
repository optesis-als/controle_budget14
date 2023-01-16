# -*- coding: utf-8 -*-
# from odoo import http


# class OptesisOptipay(http.Controller):
#     @http.route('/optesis_optipay/optesis_optipay/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/optesis_optipay/optesis_optipay/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('optesis_optipay.listing', {
#             'root': '/optesis_optipay/optesis_optipay',
#             'objects': http.request.env['optesis_optipay.optesis_optipay'].search([]),
#         })

#     @http.route('/optesis_optipay/optesis_optipay/objects/<model("optesis_optipay.optesis_optipay"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('optesis_optipay.object', {
#             'object': obj
#         })
