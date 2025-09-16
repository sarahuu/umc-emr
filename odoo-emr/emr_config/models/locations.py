from odoo import models, fields, api,_

class EMRLocation(models.Model):
    _name = 'emr.locations'
    _description = 'EMR Locations'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Location Name", required=True)
    description = fields.Text(string="Description")
    code = fields.Char(string="Location Code", required=True, default=_('New'), index=True, copy=False, help="Unique code for the location")
    location_type = fields.Selection([
        ('outpatient', 'Outpatient Clinic'),
        ('inpatient', 'Inpatient Ward'),
        ('lab', 'Lab'),
        ('pharmacy', 'Pharmacy'),
    ])
    active = fields.Boolean(string="Active", default=True)
    _sql_constraints = [
    ('uniq_location_code', 'unique(code)', 'The location code must be unique!')
]


    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('emr.locations')
        return super().create(vals)
