import time
from datetime import datetime
from odoo import models, api

class HrPayslipInheritIr(models.Model):
    _inherit = 'hr.payslip'



    def get_cumul_ir(self, ir_of_current_payslip):
        self.ensure_one()
        for payslip in self:
            cumul_ir = 0.0
            #c'est pour l'année en cour
            for line in self.env['hr.payslip'].search([('employee_id', '=', payslip.employee_id.id)], limit=2):
                if line.date_from.year == payslip.date_from.year:
                    cumul_ir += sum(payslip_line.total for payslip_line in line.line_ids if payslip_line.code == "C7010") #IR provisoire cumul
            cumul_ir += ir_of_current_payslip
            return cumul_ir