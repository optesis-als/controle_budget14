# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Treesa Maria Jude (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
from odoo import models, fields

import time
from datetime import datetime
from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

 
    relation_ids = fields.One2many('optesis.relation', 'employee_id', 'Relation')
    ir = fields.Float('Nombre de parts IR', compute="get_ir_trimf", store=True, default=1)
    trimf = fields.Float('Nombre de parts TRIMF', compute="get_ir_trimf", store=True, default=1)
    ir_changed = fields.Integer(default=0)
    
    @api.depends('relation_ids')
    def get_ir_trimf(self):
        for value in self:
            value.ir = 1 #on initialise le ir à 1 
            value.trimf = 1 #on initialise le trimf à 1 
            #nbj_sup = 0 
            status = 'single' #status à Célibataire
            for line in value.relation_ids:
                if line.type == 'enfant': #si la relation est enfant
                    now = datetime.now()
                    dur = now - line.birth
                    if dur.days < 8770:  # et si l'enfant a moins de 25 ans
                        value.ir += 0.5 #on ajout 0.5 pour chaq nouvelle relation (enfant)

                     
                    #commenté par diw
                    # obtenir ds jrs supplémentaires pr ls vacances:si l'enfant est 1e fille et elle                         a - de 15ans
                    #if dur.days <= 5114 and value.gender == 'female': 
                        #nbj_sup += 1

                if line.type == 'conjoint': #si la relation est conjoint
                    if line.salari == 0: #si le conjoint n'est pas  un salerié
                        value.ir += 1 # on ajout 1 pour chaq nouvelle relation (conjoint)
                        value.trimf += 1 # on ajout 1 pour chaq nouvelle relation (conjoint)
                    else:
                        value.ir += 0.5 #si le conjoint est un salerié on ajout 0.5
                    status = 'married' #on met status a marrié si la relation est conjoint
                    
            value.marital = status #le champs marital '	État Civil' va prendre la valeur du status

            #commenté par diw
            #if value.contract_id:
                #old_nbj_sup = value.contract_id.nbj_sup
                #if nbj_sup > old_nbj_sup:
                    #value.contract_id.write({'nbj_sup': nbj_sup})
                    # create leaves line allocation
                    #self.env['hr.leave.allocation'].create({
                        #'name': "Extra days Allowance",
                        #'number_of_days': nbj_sup,
                        #'state': 'validate',
                        #'employee_id': value.id
                    #})

            if value.ir >= 5:
                value.ir = 5
            if value.trimf >= 5:
                value.trimf = 5
                
    

class OptesisRelation(models.Model):
    _name = 'optesis.relation'
    _description = "les relations familiales"

    type = fields.Selection([('conjoint', 'Conjoint'), ('enfant', 'Enfant'), ('autre', 'Autres parents')],
                            'Type de relation')
    nom = fields.Char('Nom')
    prenom = fields.Char('Prenom')
    birth = fields.Datetime('Date de naissance')
    date_mariage = fields.Datetime('Date de mariage')
    salari = fields.Boolean('Salarie', default=0)
    employee_id = fields.Many2one('hr.employee')