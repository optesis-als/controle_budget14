import time
from datetime import datetime, date, time as t
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    adresse = fields.Char('Adresse')
    matricule_cnss = fields.Char('Matricule CNSS')
    ipres = fields.Char('Numero IPRES')
    mutuelle = fields.Char('Numero mutuelle')
    compte = fields.Char('Compte contribuable')
    num_chezemployeur = fields.Char('Numero chez l\'employeur')
    p_pere = fields.Char('Fils de (pére)')
    p_mere = fields.Char('et de (mère)')
    delivre_a = fields.Char('délivré à')
    le = fields.Date("Le")
    par = fields.Char('Par')
    group_ethique = fields.Char('Groupe ethique')
    