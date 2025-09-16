from odoo import models, fields, api, _

class MedicalImmunization(models.Model):
    _name = 'medical.immunization'
    _description = 'Medical Immunization'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='SNOMED Name', required=True)
    emr_name = fields.Char(string='EMR Display Name', required=True)
    snomed_code = fields.Char(string='SNOMED CT Code', help='Standard vaccine code (e.g., SNOMED)')
    vaccine_type = fields.Selection([
        ('viral', 'Viral'),
        ('bacterial', 'Bacterial'),
        ('toxoid', 'Toxoid'),
        ('subunit', 'Subunit'),
        ('mrna', 'mRNA'),
        ('other', 'Other'),
    ], string='Vaccine Type')
    notes = fields.Text(string='Clinical Notes')
    active = fields.Boolean(string='Active', default=True)
    _sql_constraints = [
        ('uniq_snomed_code', 'unique(snomed_code)', 'SNOMED Code must be unique!'),
        ('uniq_name', 'unique(name)', 'SNOMED Name must be unique!'),
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
