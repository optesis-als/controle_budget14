# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_optesis_hr_payroll_account = fields.Boolean(string='Payroll Accounting')
    
    number_of_days_work = fields.Float(string="Nombre jours de travail", default=30)
    number_of_hours_work = fields.Float(string="Nombre d'heures de travail", default=173)
    
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param

        days_work = self.number_of_days_work and self.number_of_days_work or False
        hours_work = self.number_of_hours_work and self.number_of_hours_work or False

        set_param('optesis_hr_payroll.number_of_days_work', days_work)
        set_param('optesis_hr_payroll.number_of_hours_work', hours_work)
    
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            number_of_days_work = self.env['ir.config_parameter'].sudo().get_param('optesis_hr_payroll.number_of_days_work'),
            number_of_hours_work =self.env['ir.config_parameter'].sudo().get_param('optesis_hr_payroll.number_of_hours_work'),
        )
        return res
       

    



#class OPTResCompanyInherit(models.Model):
 #   _inherit = 'res.company'

    
  #  number_of_days_work = fields.Float(string="Nombre jours de travail")
   # number_of_hours_work = fields.Float(string="Nombre d'heures de travail")
   