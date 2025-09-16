from odoo import models, fields, api

class MedicalAllergen(models.Model):
    _name = 'medical.allergen'
    _description = 'Medical Allergen'
    _rec_name = 'emr_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    emr_name = fields.Char(string='EMR Display Name', required=True)
    name = fields.Char(required=True, string='Allergen (SNOMED Name)')
    snomed_code = fields.Char(required=True, string='SNOMED CT Code')
    allergen_type = fields.Selection([
        ('drug', 'Drug'),
        ('food', 'Food'),
        ('environmental', 'Environmental'),
        ('biological', 'Biological'),
        ('chemical', 'Chemical'),
        ('other', 'Other'),
    ], string='Allergen Type', required=True)
    description = fields.Text(string='Clinical Notes / Reaction')
    active = fields.Boolean(string='Active', default=True)
    _sql_constraints = [
    ('uniq_snomed_code', 'unique(snomed_code)', 'SNOMED CT Code must be unique!'),
    ('uniq_name', 'unique(name)', 'EMR Display Name must be unique!'),
    ('uniq_emr_name', 'unique(emr_name)', 'EMR Display Name must be unique!')

]
    
    @api.model
    def create(self, vals):
        if not vals.get('emr_name') and vals.get('name'):
            vals['emr_name'] = vals['name']
        return super().create(vals)

    def write(self, vals):
        if vals.get('name') and not vals.get('emr_name'):
            vals['emr_name'] = vals['name']
        return super().write(vals)

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self.emr_name = self.name

