# -*- coding: utf-8 -*-
# from odoo import http


# class OptesisHrPayrollSn(http.Controller):
#     @http.route('/optesis_hr_payroll_sn/optesis_hr_payroll_sn/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/optesis_hr_payroll_sn/optesis_hr_payroll_sn/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('optesis_hr_payroll_sn.listing', {
#             'root': '/optesis_hr_payroll_sn/optesis_hr_payroll_sn',
#             'objects': http.request.env['optesis_hr_payroll_sn.optesis_hr_payroll_sn'].search([]),
#         })

#     @http.route('/optesis_hr_payroll_sn/optesis_hr_payroll_sn/objects/<model("optesis_hr_payroll_sn.optesis_hr_payroll_sn"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('optesis_hr_payroll_sn.object', {
#             'object': obj
#         })
