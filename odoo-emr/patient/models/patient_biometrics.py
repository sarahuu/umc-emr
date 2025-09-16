from odoo import models, fields, api, _

class PatientBiometrics(models.Model):
    _name="patient.biometrics"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'recorded_at desc'
    _description="Patient Biometrics"

    patient_id = fields.Many2one('patient.record', string="Patient", required=True)
    weight = fields.Float(string="Weight (kg)", digits=(5, 2))
    height = fields.Integer(string="Height (cm)")
    bmi = fields.Float(string="BMI (kg/m²)", digits=(6,1), compute="_compute_bmi", store=True)
    muac = fields.Integer(string="MUAC (cm)")
    recorded_at = fields.Datetime(string="Recorded At", default=fields.Datetime.now)
    recorded_label = fields.Char(compute='_compute_recorded_label', store=True)

    @api.constrains('weight', 'height')
    def _check_biometrics(self):
        for rec in self:
            if rec.weight and rec.weight <= 0:
                raise models.ValidationError(_("Weight must be greater than 0."))
            if rec.height and rec.height <= 0:
                raise models.ValidationError(_("Height must be greater than 0."))

    @api.depends('recorded_at')
    def _compute_recorded_label(self):
        for rec in self:
            if rec.recorded_at:
                rec.recorded_label = rec.recorded_at.strftime('%B %d, %Y %I:%M %p')
            else:
                rec.recorded_label = _('Not Recorded')

    @api.depends('weight','height')
    def _compute_bmi(self):
        for rec in self:
            if rec.height and rec.weight:
                height_square = (rec.height/100)**2
                rec.bmi = rec.weight / height_square
            else:
                rec.bmi = 0

