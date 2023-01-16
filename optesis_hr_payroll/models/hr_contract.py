# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrContract(models.Model):
    """
    Employee contract based on the visa, work permits
    allows to configure different Salary structure
    """
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    
    #calendrier de paie :pour Définir la fréquence du paiement du salaire
    schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-weekly'),
        ('bi-monthly', 'Bi-monthly'),
    ], string='Scheduled Pay', index=True, default='monthly',
    help="Defines the frequency of the wage payment.")
    
    #Horaire de travail de l'employé.
    resource_calendar_id = fields.Many2one(required=True, help="Employee's working schedule.")
    
    #Allocation de logement
    hra = fields.Monetary(string='HRA', help="House rent allowance.")
    
    #Allocation de Voyage
    travel_allowance = fields.Monetary(string="Travel Allowance", help="Travel allowance")
    
    #Allocation de cherté
    da = fields.Monetary(string="DA", help="Dearness allowance")
    
    #indemnités de repas
    meal_allowance = fields.Monetary(string="Meal Allowance", help="Meal allowance")
    
    #Allocation médicale
    medical_allowance = fields.Monetary(string="Medical Allowance", help="Medical allowance")
    
    #Les autres indemnités
    other_allowance = fields.Monetary(string="Other Allowance", help="Other allowances")

    def get_all_structures(self):
        """
        @return: the structures linked to the given contracts, ordered by hierachy (parent=False first,
                 then first level children and so on) and without duplicata
                 
                 les structures liées aux contrats donnés, classées par hiérarchie (parent=False first,
                 puis les enfants du premier niveau et ainsi de suite) et sans doublons
        """
        structures = self.mapped('struct_id')
        if not structures:
            return []
        # YTI TODO return browse records
        return list(set(structures._get_parent_structure().ids))

    def get_attribute(self, code, attribute):
        return self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1)[attribute]

    def set_attribute_value(self, code, active):
        for contract in self:
            if active:
                value = self.env['hr.contract.advantage.template'].search([('code', '=', code)], limit=1).default_value
                contract[code] = value
            else:
                contract[code] = 0.0


class HrContractAdvantageTemplate(models.Model):
    _name = 'hr.contract.advantage.template'
    _description = "Employee's Advantage on Contract"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    
    #Borne inférieure autorisée par l'employeur pour cet avantage
    lower_bound = fields.Float('Lower Bound', help="Lower bound authorized by the employer for this advantage")
    
    #Borne supérieure autorisée par l'employeur pour cet avantage
    upper_bound = fields.Float('Upper Bound', help="Upper bound authorized by the employer for this advantage")
    
    #Valeur par défaut pour cet avantage
    default_value = fields.Float('Default value for this advantage')
