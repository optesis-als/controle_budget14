# -*- coding: utf-8 -*-
# from odoo import http


# class OptesisHrContract(http.Controller):
#     @http.route('/optesis_hr_contract/optesis_hr_contract/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/optesis_hr_contract/optesis_hr_contract/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('optesis_hr_contract.listing', {
#             'root': '/optesis_hr_contract/optesis_hr_contract',
#             'objects': http.request.env['optesis_hr_contract.optesis_hr_contract'].search([]),
#         })

#     @http.route('/optesis_hr_contract/optesis_hr_contract/objects/<model("optesis_hr_contract.optesis_hr_contract"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('optesis_hr_contract.object', {
#             'object': obj
#         })
