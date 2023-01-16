import time
from datetime import datetime, date, time as t
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class HrContractBonus(models.Model):
    _inherit = 'hr.contract'

    
    nb_days = fields.Float(string="Anciennete", compute="_get_duration")
    cumul_jour = fields.Float("Cumul jours anterieur")
    cumul_conges = fields.Float("Cumul conges anterieur")
    nbj_aquis = fields.Float("Nombre de jour aquis", store=True)
    nbj_pris = fields.Float("Nombre de jour pris", default="0")
    motif = fields.Selection([('licenciement', 'Licenciement'), ('expirationnormal', 'Expiration normale du contrat'),
                              ('demissionmutation', 'Démission-Mutation')], string='Motif de sortie')
    last_date = fields.Date("derniere date")
  
    motif_entree = fields.Selection([('embauche', 'Embauche'),('changementcategorieprofessionnel', 'Changement De Categorie Professionnelle'),        ('changementcategoriefamille', 'Changement De Categorie de Famille'),
                                     ('changementresidencehabituelle', 'Changement De Residence habituelle')], string='Motif Entrée')
    dateAnciennete = fields.Date("Date d'ancienneté", default=lambda self: fields.Date.to_string(date.today()))
    typeContract = fields.Selection([('cdi', 'CDI'), ('cdd', 'CDD'), ('others', 'Autres')], string="Type de contract")
    nbj_sup = fields.Float("Nombre de jour supplementaire")
    year_extra_day_anciennete = fields.Integer()
    convention_id = fields.Many2one('line.optesis.convention', 'Categorie')
    salaire_base = fields.Integer("Salaire de Base")
    sursalaire = fields.Integer("Sursalaire")
    prime = fields.Integer("Prime")
    date_entree = fields.Date("Date d \'entrée")
    nom_employee = fields.Char("Précédent employeur")
    periode_essai = fields.Selection([('avec', 'd\'une periode d\'essai'),('sans', 'sans periode d\'essai')], string='Essai', default="avec")
    duree = fields.Integer("Durée")
    statut = fields.Selection([('cadre', 'Cadre'),('noncardre', 'Non Cadre')], string='Statut')


    @api.depends('dateAnciennete')
    def _get_duration(self):
        for record in self:
            server_dt = DEFAULT_SERVER_DATE_FORMAT
            today = datetime.now()
            dateAnciennete = datetime.strptime(str(record.dateAnciennete), server_dt)
            dur = today - dateAnciennete
            record.nb_days = dur.days
            
            
    @api.onchange("convention_id")
    def onchange_categ(self):
        if self.convention_id:
            self.wage = self.convention_id.wage
