from odoo import models, fields, api, _
from odoo.tools import populate
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

    _populate_sizes = {"small": 10, "medium": 50, "large": 500}

    def _populate_factories(self):
        Patient = self.env['patient.record']
        Allergen = self.env['medical.allergen']
        Reaction = self.env['medical.reactions']
        User = self.env['res.users']

        # Grab available IDs for relations
        patient_ids = Patient.search([], limit=200).ids or [None]
        allergen_ids = Allergen.search([], limit=50).ids or [None]
        reaction_ids = Reaction.search([], limit=50).ids or []
        user_ids = [self.env.user.id]

        return [
            ("patient_id", populate.randomize(patient_ids)),
            ("allergen_id", populate.randomize(allergen_ids)),
            ("severity", populate.randomize(['mild', 'moderate', 'severe'])),
            ("onset_date", lambda: date.today() - timedelta(days=random.randint(1, 2000))),
            ("recorded_by", populate.randomize(user_ids)),
            ("comments", populate.iterate(["No issues", "Patient reports reaction", "Requires monitoring", "Critical case"])),
            # reactions must be set after record creation
        ]

    def _populate(self, size):
        records = super()._populate(size)

        # Add Many2many reaction_ids
        Reaction = self.env['medical.reactions']
        reaction_ids = Reaction.search([], limit=50).ids
        if reaction_ids:
            for rec in records:
                rec.reaction_ids = [(6, 0, random.sample(reaction_ids, k=random.randint(1, min(3, len(reaction_ids)))))]
        return records