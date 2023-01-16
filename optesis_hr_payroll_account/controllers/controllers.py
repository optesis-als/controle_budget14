# -*- coding: utf-8 -*-
# from odoo import http


# class OptesisHrPayrollAccount(http.Controller):
#     @http.route('/optesis_hr_payroll_account/optesis_hr_payroll_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/optesis_hr_payroll_account/optesis_hr_payroll_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('optesis_hr_payroll_account.listing', {
#             'root': '/optesis_hr_payroll_account/optesis_hr_payroll_account',
#             'objects': http.request.env['optesis_hr_payroll_account.optesis_hr_payroll_account'].search([]),
#         })

#     @http.route('/optesis_hr_payroll_account/optesis_hr_payroll_account/objects/<model("optesis_hr_payroll_account.optesis_hr_payroll_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('optesis_hr_payroll_account.object', {
#             'object': obj
#         })
