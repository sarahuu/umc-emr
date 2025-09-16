from odoo import models, api, fields, _



UNITS_SELECTION = [
    ('', 'None'),
    ('%', 'Percent (%)'),
    ('ratio', 'Ratio'),
    ('ng', 'Nanogram (ng)'),
    ('µg', 'Microgram (µg)'),
    ('mg', 'Milligram (mg)'),
    ('g', 'Gram (g)'),
    ('kg', 'Kilogram (kg)'),
    ('mmol', 'Millimole (mmol)'),
    ('mol', 'Mole (mol)'),
    ('ml', 'Milliliter (mL)'),
    ('l', 'Liter (L)'),
    ('µl', 'Microliter (µL)'),
    ('mg/dl', 'Milligram per deciliter (mg/dL)'),
    ('g/dl', 'Gram per deciliter (g/dL)'),
    ('µg/ml', 'Microgram per milliliter (µg/mL)'),
    ('ng/ml', 'Nanogram per milliliter (ng/mL)'),
    ('mmol/l', 'Millimole per liter (mmol/L)'),
    ('mol/l', 'Mole per liter (mol/L)'),
    ('meq/l', 'Milliequivalent per liter (mEq/L)'),
    ('iu/l', 'International Unit per liter (IU/L)'),
    ('u/l', 'Enzyme Unit per liter (U/L)'),
    ('10^3/µl', 'Thousands per microliter (10^3/µL)'),
    ('10^6/µl', 'Millions per microliter (10^6/µL)'),
    ('fl', 'Femtoliter (fL)'),
    ('pg', 'Picogram (pg)'),
    ('s', 'Seconds (s)'),
    ('min', 'Minutes (min)'),
    ('h', 'Hours (h)'),
    ('celsius', 'Degrees Celsius (°C)'),
    ('ratio_index', 'Index/Ratio (unitless)'),
]

class LabTestType(models.Model):
    _name = "lab.test.type"
    _description = "Laboratory Test Type"

    emr_name = fields.Char("Laboratory Test Name", required=True)
    name = fields.Char("SNOMED CT Name", required=True)
    code = fields.Char("SNOMED CT Code", required=True)
    description = fields.Text("Description")
    parameter_ids = fields.One2many("lab.test.parameter", "test_type_id", string="Parameters")
    active = fields.Boolean(default=True)
    _sql_constraints = [
        ('uniq_test_name', 'unique(name)', 'Test name must be unique!')
    ]


class LabTestParameter(models.Model):
    _name = "lab.test.parameter"
    _description = "Laboratory Test Parameter"

    name = fields.Char("Parameter", required=True)
    reference_min = fields.Float("Reference Min")
    reference_max = fields.Float("Reference Max")
    test_type_id = fields.Many2one("lab.test.type", string="Test Type", required=True, ondelete="cascade")
    parameter_type = fields.Selection([
        ('numeric', 'Numeric'),
        ('select', 'Select'),
        ('text', 'Text'),
    ], string="Parameter Type", required=True, default="numeric")
    unit = fields.Selection(selection=UNITS_SELECTION, string="Unit")
    reference_min = fields.Float("Reference Min")
    reference_max = fields.Float("Reference Max")
    selection_options = fields.Char(
        "Selection Options",
        help="Comma-separated list of options if parameter type is 'Select', e.g., Positive,Negative"
    )
    active = fields.Boolean(default=True)
    _sql_constraints = [
        ('uniq_param_name', 'unique(name)', 'Parameter name must be unique!')
    ]

