from odoo import models, fields, api, _
from datetime import date, timedelta
import random

class PatientAllergies(models.Model):
    _name = 'patient.allergies'
    _description = 'Patient Allergies'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Allergen Name", related="allergen_id.emr_name", store=True, help="Display name of the allergen", tracking=True)
    patient_id = fields.Many2one('patient.record', string="Patient", required=True, ondelete='cascade', domain="[('active', '=', True)]", help="The patient who has the allergy", index=True)
    allergen_id = fields.Many2one('medical.allergen', string="Allergen", required=True, ondelete='restrict', domain="[('active', '=', True)]", help="The substance or agent causing the allergy")
    reaction_ids = fields.Many2many('medical.reactions', string="Reactions", help="Reactions associated with the allergy", domain="[('active', '=', True)]", tracking=True)
    severity = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ], string="Severity", default='mild', help="Severity of the allergy", tracking=True)
    onset_date = fields.Date(string="Date of Onset", help="Date when the allergy was first diagnosed or noticed", tracking=True)
    recorded_by = fields.Many2one('res.users', string="Recorded By", default=lambda self: self.env.user, help="User who recorded the condition", domain="[('active', '=', True)]")
    comments = fields.Text(string="Comments")
    active = fields.Boolean(string="Active", default=True)
    _sql_constraints = [
        ('uniq_patient_allergen', 'unique(patient_id, allergen_id)', 'This allergen is already recorded for the patient!'),
    ]

