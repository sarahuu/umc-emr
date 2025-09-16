from odoo import models, fields, api, _
import re

class MedicalService(models.Model):
    _name = 'medical.service'
    _description = 'Clinic Service Types'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'


    name = fields.Char(string="Service Name", required=True, help="Name of the medical service, e.g. 'Antenatal Care'")
    description = fields.Text(string="Description", help="Detailed description of the service")
    slug = fields.Char("Slug", compute="_compute_slug", store=True)
    active = fields.Boolean(string="Active", default=True, help="Indicates if the service is currently active")
    _sql_constraints = [
        ('uniq_name', 'unique(name)', 'Service Name must be unique!'),
    ]

    @api.depends("name")
    def _compute_slug(self):
        for record in self:
            if record.name:
                slug = record.name.lower()
                slug = re.sub(r'\s+', '-', slug)
                slug = re.sub(r'[^a-z0-9\-]', '', slug)
                record.slug = slug
            else:
                record.slug = False 

