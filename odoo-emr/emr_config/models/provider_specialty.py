from odoo import models, fields, api, _

class ProviderSpecialty(models.Model):
    _name = 'provider.specialty'
    _description = 'Provider Specialty Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'


    name = fields.Char(string="Specialty Name", required=True, help="Name of the medical specialty")
    description = fields.Text(string="Description", help="Detailed description of the specialty")
    active = fields.Boolean(string="Active", default=True, help="Indicates if the specialty is currently active")
    _sql_constraints = [
        ('uniq_name', 'unique(name)', 'Specialty Name must be unique!'),
    ]
