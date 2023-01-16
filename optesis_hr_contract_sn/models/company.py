from odoo import api, fields, models, _


class hr_inherit(models.Model):

    _name = "res.company"
    _inherit = ['res.company']

    resume_entreprise = fields.Char('Résumé de la Société')
    activite = fields.Char('Activité de l\'établissement')