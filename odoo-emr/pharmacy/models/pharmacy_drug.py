from odoo import models, fields, api, _
from .dummy_data import DRUG_FORMS, ROUTE_SELECTION, DRUG_UNITS
import re


class PharmacyDrug(models.Model):
    _name = "pharmacy.drug"
    _description = "Drug Catalog"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Drug Name", required=True)
    generic_name = fields.Char("Generic Name", default="Unknown", required=True)
    strength = fields.Char("Strength (e.g. 500mg)", required=True)
    form = fields.Selection(selection=DRUG_FORMS, string="Dosage Form", required=True)
    route = fields.Selection(selection=ROUTE_SELECTION, string="Route of Administration", required=True)
    unit = fields.Selection(selection=DRUG_UNITS, string="Default Unit", required=True)
    display_name = fields.Char("Display Name", compute="_compute_display_name", store=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('drug_unique_constraint', 'UNIQUE(generic_name, strength, form, route, unit)', 
         'A drug with these exact specifications already exists!'),
    ]

    @api.constrains('strength')
    def _check_strength_format(self):
        for rec in self:
            if rec.strength:
                pattern = r'^\d+(\.\d+)?[a-zA-Z]+$'
                if not re.match(pattern, rec.strength.replace(' ', '')):
                    raise models.ValidationError(_(
                        "Strength format is invalid. Please use format like: 500mg, 10ml, 0.5mg"
                    ))

    @api.depends("generic_name", "strength", "form")
    def _compute_display_name(self):
        for rec in self:
            parts = [rec.generic_name]
            if rec.strength:
                parts.append(rec.strength)
            if rec.form:
                parts.append(rec.form)
            rec.display_name = "-".join(parts)
