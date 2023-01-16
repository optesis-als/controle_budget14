# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_optesis_hr_payroll_account = fields.Boolean(string='Payroll Accounting')
    number_of_days_work = fields.Float(related='company_id.number_of_days_work', readonly=False, string=" nombre jours de travail", default="30")
    number_of_hours_work = fields.Float(string="Nombre d'heures de travail", related='company_id.number_of_hours_work', readonly=False, default="173.33")

    


   


class OPTResCompanyInherit(models.Model):
    _inherit = 'res.company'

    
    number_of_days_work = fields.Float(string="Nombre jours de travail")
    number_of_hours_work = fields.Float(string="Nombre d'heures de travail")
   