from odoo import models, fields, api, _
from datetime import date

class PatientCondition(models.Model):
    _name = 'patient.conditions'
    _description = 'Patient Condition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = "onset_date desc, id desc"


    patient_id = fields.Many2one('patient.record', string="Patient", required=True, ondelete='cascade', domain="[('active', '=', True)]", help="The patient who has the condition")
    condition_id = fields.Many2one('medical.conditions', string="Medical Condition", required=True, ondelete='cascade', domain="[('active', '=', True)]", help="The medical condition being recorded")
    name = fields.Char(string="Condition Name", related="condition_id.emr_name", store=True, help="Display name of the medical condition")
    onset_date = fields.Date(string="Date of Onset", help="Date when the condition was first diagnosed or noticed", tracking=True)
    clinical_status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('remission', 'In Remission'),
        ('resolved', 'Resolved'),
    ], string="Clinical Status", default='active', help="Current status of the condition", tracking=True)
    recorded_by = fields.Many2one('res.users', string="Recorded By", default=lambda self: self.env.user, help="User who recorded the condition", tracking=True, domain="[('active', '=', True)]")
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)
    _sql_constraints = [
        ('uniq_patient_condition',
        'unique(patient_id, condition_id)',
        'This condition is already recorded for the patient!')
    ]

    @api.constrains('onset_date')
    def _check_onset_date(self):
        for rec in self:
            if rec.onset_date and rec.onset_date > date.today():
                raise models.ValidationError(_("Onset date cannot be in the future."))