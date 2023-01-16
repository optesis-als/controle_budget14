# -*- coding: utf-8 -*-
# from odoo import http


# class OptesisHrPayroll(http.Controller):
#     @http.route('/optesis_hr_payroll/optesis_hr_payroll/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/optesis_hr_payroll/optesis_hr_payroll/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('optesis_hr_payroll.listing', {
#             'root': '/optesis_hr_payroll/optesis_hr_payroll',
#             'objects': http.request.env['optesis_hr_payroll.optesis_hr_payroll'].search([]),
#         })

#     @http.route('/optesis_hr_payroll/optesis_hr_payroll/objects/<model("optesis_hr_payroll.optesis_hr_payroll"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('optesis_hr_payroll.object', {
#             'object': obj
#         })
