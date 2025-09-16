from odoo import models, api, fields, _
from .lab_test import UNITS_SELECTION

class LabResult(models.Model):
    _name = "lab.result"
    _description = "Laboratory Result"
    _rec_name = "name"

    name = fields.Char("Result Reference", default=lambda self: _('New'), copy=False, readonly=True)
    order_line_id = fields.Many2one("lab.order.line", string="Lab Order Line", required=True, ondelete="cascade")
    patient_id = fields.Many2one("patient.record", string="Patient", related="order_line_id.patient_id")
    test_type_id = fields.Many2one("lab.test.type", string="Test Type", related="order_line_id.test_type_id")
    recorded_by = fields.Many2one("res.users", string="Recorded By", default=lambda self: self.env.user)
    parameter_result_ids = fields.One2many("lab.result.parameter", "result_id", string="Parameter Results")
    state = fields.Selection([
        ("draft", "Draft"),
        ("requested", "Requested"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    ], string="Status", related="order_line_id.state")

    @api.model
    def create(self, vals):
       if vals.get('name', _('New')) == _('New'):
           vals['name'] = self.env['ir.sequence'].next_by_code('lab.result')
       return super(LabResult, self).create(vals)




class LabResultParameter(models.Model):
    _name = "lab.result.parameter"
    _description = "Laboratory Result Parameter"

    result_id = fields.Many2one("lab.result", string="Lab Result", required=True, ondelete="cascade")
    test_type_id = fields.Many2one("lab.test.type",string="Test Type",related="result_id.test_type_id", store=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("requested", "Requested"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    ], string="Status", related="result_id.state")
    parameter_id = fields.Many2one("lab.test.parameter", string="Parameter", required=True, domain="[('test_type_id','=',test_type_id)]")
    parameter_type = fields.Selection(related="parameter_id.parameter_type")
    value_numeric = fields.Float("Numeric Value")
    value_text = fields.Char("Text Value")
    value_select = fields.Selection(
        selection="_get_selection_options",
        string="Select Value"
    )
    unit = fields.Selection(selection=UNITS_SELECTION, string="Unit", related="parameter_id.unit")
    reference_min = fields.Float("Ref Min", related="parameter_id.reference_min")
    reference_max = fields.Float("Ref Max", related="parameter_id.reference_max")
    is_abnormal = fields.Boolean("Abnormal?", compute="_compute_is_abnormal")


    @api.depends("value_numeric", "reference_min", "reference_max", "parameter_type")
    def _compute_is_abnormal(self):
        for rec in self:
            if rec.parameter_type == "numeric" and rec.value_numeric:
                rec.is_abnormal = not (rec.reference_min <= rec.value_numeric <= rec.reference_max)
            else:
                rec.is_abnormal = False

    @api.model
    def _get_selection_options(self):
        """Dynamically load selection options from parameter"""
        params = self.env["lab.test.parameter"].search([("parameter_type", "=", "select")])
        options = []
        for param in params:
            if param.selection_options:
                for opt in param.selection_options.split(","):
                    options.append((opt.strip(), opt.strip()))
        return options
