from odoo import models, fields, api
from odoo.exceptions import UserError
from ..models.dummy_data import DRUG_UNITS, FREQUENCY_PERIOD_SELECTION

class PrescriptionWizard(models.TransientModel):
    _name = 'prescription.order.wizard'
    _description = 'Prescription Entry Wizard'

    line_id = fields.Many2one('prescription.order.line', string='Prescription Line')
    prescription_id = fields.Many2one('prescription.order', string='Prescription Order')
    drug_id = fields.Many2one('pharmacy.drug', string='Drug', required=True)
    dose = fields.Float("Dose")
    dose_unit = fields.Selection(DRUG_UNITS, string="Dose Unit")
    frequency = fields.Integer("Frequency Number")
    frequency_unit = fields.Selection(
        selection=FREQUENCY_PERIOD_SELECTION,
        string="Frequency Unit",
        default='day'
    )
    indication = fields.Char("Indication")
    instructions = fields.Text("Doctor Instructions")
    duration = fields.Integer("Duration")
    duration_unit = fields.Selection([
        ("days", "Days"),
        ("weeks", "Weeks"),
        ("months", "Months"),
        ("years", "Years")
    ], string="Duration Unit", default="days")
    date_start = fields.Datetime("Start Date", default=fields.Datetime.now)
    qty_to_dispense = fields.Float("Quantity to Dispense")
    qty_unit = fields.Selection(selection=DRUG_UNITS, string="Dispense Unit")
    dispensing_instructions = fields.Text("Dispensing Instructions")
    state = fields.Selection([
        ("draft", "Draft"),
        ("active", "Active"),
        ("ended", "Ended"),
        ("cancelled", "Discontinued"),
    ], related="line_id.state", string="Status", readonly=True)

    edit_mode = fields.Boolean(default=False)


    def action_add_prescription(self):
        line_vals = {
            'prescription_id': self.prescription_id.id,
            'drug_id': self.drug_id.id,
            'dose': self.dose,
            'dose_unit': self.dose_unit,
            'frequency': self.frequency,
            'frequency_unit': self.frequency_unit,
            'indication': self.indication,
            'instructions': self.instructions,
            'duration': self.duration,
            'duration_unit': self.duration_unit,
            'date_start': self.date_start,
            'qty_to_dispense': self.qty_to_dispense,
            'qty_unit': self.qty_unit,
            'dispensing_instructions': self.dispensing_instructions,
        }
        if self.edit_mode and self.line_id:
            self.line_id.write(line_vals)
        else:
            self.env['prescription.order.line'].create(line_vals)
        
        return {'type': 'ir.actions.act_window_close'}
    
    def cancel_prescription(self):
        if self.line_id:
            self.line_id.cancel_prescription()

    def confirm_order(self):
        if self.line_id:
            self.line_id.confirm_order()
        else:
            raise UserError("No prescription order line associated.")
