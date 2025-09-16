from odoo import models, fields, api, _
from .dummy_data import DRUG_FORMS, ROUTE_SELECTION, DRUG_UNITS, FREQUENCY_PERIOD_SELECTION
from dateutil.relativedelta import relativedelta

class PrescriptionOrder(models.Model):
    _name = "prescription.order"
    _description = "Prescription"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    name = fields.Char("Prescription Reference", required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    patient_id = fields.Many2one("patient.record", required=True, ondelete="restrict")
    ordered_by = fields.Many2one("res.users", default=lambda self: self.env.user, string="Ordered By", required=True)
    line_ids = fields.One2many("prescription.order.line", "prescription_id", string="Drugs")
    patient_name = fields.Char(string="Name", related="patient_id.name", index=True)
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if 'name' not in vals:
            vals['name'] = self.env['ir.sequence'].next_by_code('prescription.order')
        return super(PrescriptionOrder, self).create(vals)

    def action_add_prescription_line(self):
        return {
            'name': _('Add Prescription Line'),
            'type': 'ir.actions.act_window',
            'res_model': 'prescription.order.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_prescription_id': self.id,
            }
    }






class PrescriptionLine(models.Model):
    _name = "prescription.order.line"
    _description = "Prescription Line"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Line Reference", required=True, default=lambda self: _('New'), copy=False, readonly=True)
    prescription_id = fields.Many2one("prescription.order", ondelete="cascade")
    patient_id = fields.Many2one("patient.record", related="prescription_id.patient_id", store=True, readonly=True, tracking=True)
    patient_name = fields.Char(string="Name", related="patient_id.name", index=True)
    gender = fields.Selection(related="patient_id.gender")
    age = fields.Integer(related="patient_id.age")
    vitals_ids = fields.One2many('patient.vitals', 'patient_id', string="Vitals Records", related="patient_id.vitals_ids", readonly=True)
    biometrics_ids = fields.One2many('patient.biometrics', 'patient_id', string="Biometric Records", related="patient_id.biometrics_ids", readonly=True)
    conditions_ids = fields.One2many('patient.conditions', 'patient_id', string="Medical Conditions", related="patient_id.conditions_ids", readonly=True)
    allergies_ids = fields.One2many('patient.allergies', 'patient_id', string="Allergies", related="patient_id.allergies_ids", readonly=True)
    blood_pressure = fields.Char(string="BP (mmHg)", compute="_compute_vitals")
    respiratory_rate = fields.Integer(string="R.Rate (breaths/min)", compute="_compute_vitals")
    spo2 = fields.Float(string="SpO₂(%)", compute="_compute_vitals")
    heart_rate = fields.Integer(string="H.Rate (bpm)", compute="_compute_vitals")
    temperature = fields.Float(string="Temperature (°C)", compute="_compute_vitals")
    weight = fields.Float(string="Weight (kg)", compute="_compute_vitals")
    height = fields.Integer(string="Height (cm)", compute="_compute_vitals")
    prescribed_by = fields.Many2one("res.users", default=lambda self: self.env.user, readonly=True)
    drug_id = fields.Many2one("pharmacy.drug", required=True, tracking=True)
    
    dose = fields.Float("Dose", tracking=True)
    dose_unit = fields.Selection(DRUG_UNITS, string="Dose Unit", tracking=True)
    frequency = fields.Integer("Frequency Number", tracking=True)
    frequency_unit = fields.Selection(
        selection=FREQUENCY_PERIOD_SELECTION,
        string="Frequency Unit",
        default='day'
    , tracking=True)
    indication = fields.Char("Indication", tracking=True)
    instructions = fields.Text("Doctor Instructions", tracking=True)
    duration = fields.Integer("Duration", tracking=True)
    duration_unit = fields.Selection([
        ("days", "Days"),
        ("weeks", "Weeks"),
        ("months", "Months"),
        ("years", "Years")
    ], string="Duration Unit", tracking=True)
    date_start = fields.Datetime("Start Date", default=fields.Datetime.now, tracking=True)
    date_end = fields.Datetime("End Date", compute="_compute_end_date", store=True)
    route = fields.Selection(ROUTE_SELECTION, string="Route of Administration", related="drug_id.route", readonly=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("active", "Active"),
        ("ended", "Ended"),
        ("cancelled", "Discontinued"),
    ], default="draft", tracking=True)
    date_prescribed = fields.Datetime("Date Prescribed", default=fields.Datetime.now)
    # Dispensing Instructions
    qty_to_dispense = fields.Float("Quantity to Dispense" , tracking=True)
    qty_unit = fields.Selection(selection=DRUG_UNITS, string="Dispense Unit", tracking=True)
    dispensing_instructions = fields.Text("Dispensing Instructions", tracking=True)
    dispense_ids = fields.One2many("prescription.dispense", "line_id", string="Dispenses", tracking=True)
    total_dispensed = fields.Float("Total Dispensed", compute="_compute_total_dispensed")
    remaining_qty = fields.Float("Remaining", compute="_compute_total_dispensed")
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if 'name' not in vals:
            vals['name'] = self.env['ir.sequence'].next_by_code('prescription.order.line')
        return super(PrescriptionLine, self).create(vals)

    @api.depends("dispense_ids.dispensed_qty")
    def _compute_total_dispensed(self):
        for rec in self:
            total = sum(d.dispensed_qty for d in rec.dispense_ids)
            rec.total_dispensed = total
            rec.remaining_qty = rec.qty_to_dispense - total


    @api.depends("dispense_ids.dispensed_qty", "qty_to_dispense")
    def _compute_total_dispensed(self):
        for rec in self:
            total = sum(d.dispensed_qty for d in rec.dispense_ids)
            rec.total_dispensed = total
            rec.remaining_qty = rec.qty_to_dispense - total
    

    @api.depends('date_start', 'duration', 'duration_unit')
    def _compute_end_date(self):
        for record in self:
            if not record.date_start or not record.duration or not record.duration_unit:
                record.date_end = False
                continue
            
            # Convert duration to relativedelta based on unit
            if record.duration_unit == 'days':
                delta = relativedelta(days=record.duration)
            elif record.duration_unit == 'weeks':
                delta = relativedelta(weeks=record.duration)
            elif record.duration_unit == 'months':
                delta = relativedelta(months=record.duration)
            elif record.duration_unit == 'years':
                delta = relativedelta(years=record.duration)
            else:
                record.date_end = False
                continue
            
            # Calculate end date
            record.date_end = record.date_start + delta

    @api.depends('vitals_ids','biometrics_ids')
    def _compute_vitals(self):
        latest_vital = self.vitals_ids.sorted(key='create_date', reverse=True)[:1]
        latest_biometric = self.biometrics_ids.sorted(key='create_date', reverse=True)[:1]
        for rec in self:
            rec.blood_pressure = latest_vital.blood_pressure
            rec.respiratory_rate = latest_vital.respiratory_rate
            rec.spo2 = latest_vital.spo2
            rec.heart_rate = latest_vital.heart_rate
            rec.temperature = latest_vital.temperature
            rec.weight = latest_biometric.weight
            rec.height = latest_biometric.height

    # Add these methods to your PrescriptionOrderLine class

    def confirm_order(self):
        for line in self:
            if line.state == 'draft':
                line.write({'state': 'active','date_prescribed': fields.Datetime.now()})
            else:
                raise models.ValidationError("You can only confirm a draft prescription")

    def view_prescription(self):
        self.ensure_one()
        return {
            'name': _('View/Edit Prescription'),
            'type': 'ir.actions.act_window',
            'res_model': 'prescription.order.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': False,
            'context': {
                'default_prescription_id': self.prescription_id.id,
                'default_drug_id': self.drug_id.id,
                'default_dose': self.dose,
                'default_dose_unit': self.dose_unit,
                'default_frequency': self.frequency,
                'default_frequency_unit': self.frequency_unit,
                'default_indication': self.indication,
                'default_instructions': self.instructions,
                'default_duration': self.duration,
                'default_duration_unit': self.duration_unit,
                'default_date_start': self.date_start,
                'default_qty_to_dispense': self.qty_to_dispense,
                'default_qty_unit': self.qty_unit,
                'default_dispensing_instructions': self.dispensing_instructions,
                'default_state': self.state,
                'edit_mode': True,
                'default_line_id': self.id,
            }
        }
    
    def cancel_prescription(self):
        if self.state == 'active':
            self.write({
                'state': 'cancelled',
            })
        else:
            raise models.ValidationError("Prescription is already ended or discontinued.")



class PrescriptionDispense(models.Model):
    _name = "prescription.dispense"
    _description = "Drug Dispensing"

    name = fields.Char("Dispense Reference", required=True, default=lambda self: _('New'), copy=False, readonly=True)
    line_id = fields.Many2one("prescription.order.line", ondelete="cascade")
    prescription_id = fields.Many2one("prescription.order", related="line_id.prescription_id", store=True)
    patient_id = fields.Many2one("patient.record", related="prescription_id.patient_id", store=True)

    dispensed_qty = fields.Float("Qty Dispensed", required=True)
    dispensed_unit = fields.Selection(related="line_id.qty_unit", string="Dispense Unit", readonly=True)
    dispensed_date = fields.Datetime("Dispensed On", default=fields.Datetime.now)
    dispensed_by = fields.Many2one("res.users", string="Dispensed By", default=lambda self: self.env.user)
    notes = fields.Text("Notes")
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('prescription.dispense') or _('New')
        return super(PrescriptionDispense, self).create(vals)

    @api.constrains('dispensed_qty', 'line_id')
    def _check_dispensed_quantity(self):
        for record in self:
            if record.line_id and record.dispensed_qty > 0:
                # Calculate total already dispensed (excluding current record if updating)
                existing_dispenses = record.line_id.dispense_ids - record
                total_dispensed = sum(existing_dispenses.mapped('dispensed_qty'))
                remaining = record.line_id.qty_to_dispense - total_dispensed
                
                if record.dispensed_qty > remaining:
                    raise models.ValidationError(
                        _("Cannot dispense more than remaining quantity!\n"
                          "Prescribed: %(prescribed)s %(unit)s\n"
                          "Already Dispensed: %(dispensed)s %(unit)s\n"
                          "Remaining: %(remaining)s %(unit)s\n"
                          "Trying to dispense: %(trying)s %(unit)s") % {
                              'prescribed': record.line_id.qty_to_dispense,
                              'dispensed': total_dispensed,
                              'remaining': remaining,
                              'trying': record.dispensed_qty,
                              'unit': record.dispensed_unit or ''
                          }
                    )

    @api.onchange('dispensed_qty')
    def _onchange_dispensed_qty(self):
        for record in self:
            if record.line_id and record.dispensed_qty > 0:
                # Calculate remaining quantity (including this record for real-time feedback)
                total_dispensed = sum(record.line_id.dispense_ids.mapped('dispensed_qty'))
                remaining = record.line_id.qty_to_dispense - total_dispensed
                
                if record.dispensed_qty > remaining:
                    return {
                        'warning': {
                            'title': _("Quantity Exceeded"),
                            'message': _("You are trying to dispense %(qty)s %(unit)s, but only %(remaining)s %(unit)s remains.\n"
                                       "Prescribed: %(prescribed)s %(unit)s\n"
                                       "Already Dispensed: %(dispensed)s %(unit)s") % {
                                           'qty': record.dispensed_qty,
                                           'remaining': remaining,
                                           'prescribed': record.line_id.qty_to_dispense,
                                           'dispensed': total_dispensed,
                                           'unit': record.dispensed_unit or ''
                                       }
                        }
                    }