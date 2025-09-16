from odoo import models, fields, api, _
import re


class PatientVitals(models.Model):
    _name = 'patient.vitals'
    _description = 'Patient Vitals Information'

    patient_id = fields.Many2one('patient.record', string="Patient", required=True)
    blood_pressure = fields.Char(string="Blood Pressure (mmHg)", help="Systolic/Diastolic format, e.g., 120/80", tracking=True)
    systolic_bp = fields.Integer(string="Systolic BP", help="Systolic blood pressure in mmHg", compute='_compute_blood_pressure', store=True)
    diastolic_bp = fields.Integer(string="Diastolic BP", help="Diastolic blood pressure in mmHg", compute='_compute_blood_pressure', store=True)
    heart_rate = fields.Integer(string="Heart Rate (bpm)", help="Beats per minute")
    respiratory_rate = fields.Integer(string="Respiratory Rate (breaths/min)", help="Breaths per minute")
    temperature = fields.Float(string="Temperature (°C)", help="Body temperature in degrees Celsius")
    recorded_at = fields.Datetime(string="Recorded At", default=fields.Datetime.now)
    recorded_label = fields.Char(compute='_compute_recorded_label', store=True)
    spo2 = fields.Float(string="SpO₂ (%)", help="Oxygen saturation percentage")
    active = fields.Boolean(string="Active", default=True)


    @api.constrains('temperature', 'spo2', 'heart_rate', 'respiratory_rate', 'blood_pressure')
    def _check_vital_signs(self):
        for rec in self:
            if rec.temperature and not (25 <= rec.temperature <= 45):
                raise models.ValidationError(_("Temperature must be between 25°C and 45°C."))

            if rec.spo2 and not (0 <= rec.spo2 <= 100):
                raise models.ValidationError(_("SpO₂ must be between 0% and 100%."))

            if rec.heart_rate is not None and rec.heart_rate < 0:
                raise models.ValidationError(_("Heart rate must be a positive number."))

            if rec.respiratory_rate is not None and rec.respiratory_rate < 0:
                raise models.ValidationError(_("Respiratory rate must be a positive number."))

            if rec.blood_pressure:
                match = re.fullmatch(r'\s*(\d+)\s*/\s*(\d+)\s*', rec.blood_pressure)
                if not match:
                    raise models.ValidationError(_("Blood Pressure must be in the format '120/80' with integers."))
    
    @api.depends('blood_pressure')
    def _compute_blood_pressure(self):
        for record in self:
            if record.blood_pressure:
                match = re.fullmatch(r'\s*(\d+)\s*/\s*(\d+)\s*', record.blood_pressure)
                if match:
                    record.systolic_bp = int(match.group(1))
                    record.diastolic_bp = int(match.group(2))
                else:
                    record.systolic_bp = 0
                    record.diastolic_bp = 0
            else:
                record.systolic_bp = 0
                record.diastolic_bp = 0
    
    @api.depends('recorded_at')
    def _compute_recorded_label(self):
        for rec in self:
            if rec.recorded_at:
                rec.recorded_label = rec.recorded_at.strftime('%B %d, %Y %I:%M %p')
            else:
                rec.recorded_label = _('Not Recorded')
