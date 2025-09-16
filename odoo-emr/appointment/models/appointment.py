from odoo import models, fields, api, _
from datetime import datetime, timedelta

class MedicalAppointment(models.Model):
    _name = 'appointment.appointment'
    _description = 'Medical Appointment Information'
    _rec_name = 'appointment_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    appointment_id = fields.Char(string="Appointment ID", readonly=True, copy=False, default=_('New'), help="Unique identifier for the appointment")
    provider_id = fields.Many2one('emr.provider', string="Provider", help="Provider assigned to this appointment", domain="[('active', '=', True)]")
    location_id = fields.Many2one('emr.locations', string="Location", help="Location where the appointment will take place", domain="[('active', '=', True)]")
    service_type = fields.Many2one('medical.service', string="Clinic Type", help="Type of service for this appointment", domain="[('active', '=', True)]")

    granular_slot_id = fields.Many2one('appointment.available.slot', string="Available Slot", help="Available time slot for the appointment", domain="[('is_booked', '=', False),('active','=',True)]")
    #date & time fields 
    date_confirmed = fields.Datetime(string="Date Confirmed", help="Date and time when the appointment was confirmed", tracking=True) 
    date_scheduled = fields.Datetime(string="Date Scheduled", help="Date and time when the appointment is scheduled", tracking=True)
    date_cancelled = fields.Datetime(string="Date Cancelled", help="Date and time when the appointment was cancelled", tracking=True)
    date_checkedin = fields.Datetime(string="Date Checked In", help="Date and time when the patient checked in", tracking=True)
    date_completed = fields.Datetime(string="Date Completed", help="Date and time when the appointment was completed", tracking=True)
    start_datetime = fields.Datetime(string="Appointment Start", help="Start date and time of the appointment", tracking=True)
    end_datetime = fields.Datetime(string="Appointment End", compute="_compute_end_datetime", store=True, help="End date and time of the appointment", tracking=True)
    duration = fields.Float(string="Duration", help="Duration of the appointment in hours")
    state = fields.Selection([
        ('requested', 'Requested'),
        ('scheduled', 'Scheduled'),
        ('checked_in', 'Checked In'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('missed', 'Missed')
    ], string="State", default='requested', help="State of the appointment", tracking=True)
    status = fields.Selection([('draft', 'Draft'),('confirmed', 'Confirmed')], string="Status", default='draft', help="Status of the appointment", tracking=True)
    note = fields.Text(string="Note", help="Additional notes for the appointment")

    # Patient fields
    patient_id = fields.Many2one('patient.record', string="Patient", help="Patient for whom the appointment is scheduled", tracking=True)
    patient_identifier = fields.Char(string="Identifier", related="patient_id.patient_id")
    patient_name = fields.Char(string="Patient Name", related="patient_id.name", help="Name of the patient")
    gender = fields.Selection(string="Gender", related="patient_id.gender")
    age = fields.Integer(string="Age", related="patient_id.age")
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
    ('unique_appointment_id', 'unique(appointment_id)', 'Appointment ID must be unique!'),
    ('unique_slot_booking', 'unique(granular_slot_id)', 'This slot is already booked.'),
]

    @api.constrains('provider_id', 'patient_id')
    def _check_provider_patient(self):
        for rec in self:
            if rec.state in ['scheduled', 'checked_in', 'completed'] and not rec.provider_id:
                raise models.ValidationError("A provider must be assigned before scheduling or checking in.")
            if rec.state != 'requested' and not rec.patient_id:
                raise models.ValidationError("Patient is required once appointment progresses beyond 'requested'.")


    @api.model
    def create(self, vals):
        if vals.get('appointment_id', _('New')) == _('New'):
            vals['appointment_id'] = self.env['ir.sequence'].next_by_code('appointment.appointment') or _('New')
        if vals.get("granular_slot_id"):
            slot = self.env["appointment.available.slot"].browse(vals["granular_slot_id"])
            vals.update({
                "provider_id": slot.provider_id.id,
                "location_id": slot.location_id.id,
                "service_type": slot.service_type.id,
                "start_datetime": slot.start_datetime,
                "duration": slot.duration,
            })
        return super().create(vals)

    def write(self, vals):
        if vals.get("granular_slot_id"):
            slot = self.env["appointment.available.slot"].browse(vals["granular_slot_id"])
            vals.update({
                "provider_id": slot.provider_id.id,
                "location_id": slot.location_id.id,
                "service_type": slot.service_type.id,
                "start_datetime": slot.start_datetime,
                "duration": slot.duration,
            })
        return super().write(vals)
    
    @api.depends('start_datetime', 'duration')
    def _compute_end_datetime(self):
        for rec in self:
            if rec.start_datetime and rec.duration:
                rec.end_datetime = rec.start_datetime + timedelta(minutes=rec.duration)
            else:
                rec.end_datetime = False

    @api.onchange('granular_slot_id')
    def _onchange_granular_slot_id(self):
        if self.granular_slot_id:
            self.provider_id = self.granular_slot_id.provider_id
            self.location_id = self.granular_slot_id.location_id
            self.service_type = self.granular_slot_id.service_type
            self.start_datetime = self.granular_slot_id.start_datetime
            self.duration = self.granular_slot_id.duration

    @api.onchange('provider_id')
    def _onchange_provider_id(self):
        if self.provider_id:
            return {
                'domain': {
                    'service_type': [('id', 'in', self.provider_id.service_ids.ids)]
                }
            }
    @api.onchange('service_type')
    def _onchange_service_type(self):
        if self.service_type:
            providers = self.env['emr.provider'].search([('service_ids', 'in', self.service_type.id)])
            return {'domain': {'provider_id': [('id', 'in', providers.ids)]}}

    def confirm(self):
        if self.status != 'draft':
            raise models.ValidationError("Only draft appointments can be confirmed.")
        self.write({'status': 'confirmed'})
        self.granular_slot_id.write({'is_booked': True})
        self.date_confirmed = fields.Datetime.now()
        return True

    def schedule_app(self):
        if not self.provider_id:
            raise models.ValidationError('Please select a provider to schedule this appointment')
        self.write({'state': 'scheduled', 'date_scheduled': fields.Datetime.now()})

    def check_in(self):
        if self.state == 'scheduled':
            if self.patient_id.active_visit:
                raise models.ValidationError(
                    f"Patient already has an active visit. End that visit before checking in."
                )
            self.write({'state':'checked_in','date_checkedin':fields.Datetime.now()})
            tolerance = 10 #minuted
            scheduled = self.start_datetime
            if scheduled:
                diff_minutes = (fields.Datetime.now() - scheduled).total_seconds() / 60.0
                if abs(diff_minutes) <= tolerance:
                    punctuality_status = 'on_time'
                elif diff_minutes > tolerance:
                    punctuality_status = 'late'
                else:
                    punctuality_status = 'early'
            else:
                punctuality_status = False  # No scheduled time
            visit = self.env['appointment.visit'].create({
                'appointment_id': self.id,
                'patient_id': self.patient_id.id,
                'location_id': self.location_id.id,
                'visit_type': 'facility_visit',
                'punctuality':punctuality_status
            })
            visit.action_start()
        else:
            raise models.ValidationError("You can't check in if appointment has not been scheduled")

    def check_out(self):
        if self.state == 'checked_in':
            self.write({'state':'completed','date_completed':fields.Datetime.now()})
            visit = self.env['appointment.visit'].search([('appointment_id', '=', self.id)], limit=1)
            if visit:
                visit.action_end()
        else:
            raise models.ValidationError("You can't check out if appointment has not been checked in")

    def cancel(self):
        if self.state == 'completed':
            raise models.ValidationError("Completed appointments cannot be cancelled.")
        self.write({'state': 'cancelled', 'date_cancelled': fields.Datetime.now()})
        self.granular_slot_id.write({'is_booked': False})
        self.message_post(body=f"Appointment cancelled.")

    def reschedule(self):
        return {
        'name': 'Reschedule Appointment',
        'type': 'ir.actions.act_window',
        'res_model': 'appointment.reschedule.wizard', 
        'view_mode': 'form',
        'view_id': self.env.ref('appointment.view_appointment_reschedule_wizard_form').id,
        'target': 'new',
        'context': {
            'default_appointment_id': self.id,
        },
    }

    def _cron_mark_missed_appointments(self):
        """Cron job to mark overdue scheduled appointments as missed."""
        now = fields.Datetime.now()
        overdue_apps = self.search([
            ('state', '=', 'scheduled'),
            ('start_datetime', '<', now)
        ])
        for app in overdue_apps:
            app.write({'state': 'missed'})
            if app.granular_slot_id:
                app.granular_slot_id.write({'is_booked': False})


    @api.model
    def book_appointment(self,slot_id,patient_id, note):
        patient = self.env['patient.record'].search([('id','=',patient_id)], limit=1)
        Slot = self.env["appointment.available.slot"]
        slot = Slot.search([
            ("id", "=", slot_id),
            ('is_booked','=',False),
            ("active", "=", True),
        ], limit=1)

        if not slot:
            return {"success": False, "message": "Slot not available"}

        # Mark slot as inactive (booked)
        slot.active = False

        # Create appointment record
        appointment = self.create({
            "granular_slot_id": slot.id,
            "patient_id": patient.id,
            "note":note
        })
        appointment.confirm()
        return {
            "success": True,
            "appointment_id": appointment.id,
            "time": appointment.start_datetime.strftime("%d %b %Y | %I:%M %p"),
            "message": "Appointment booked successfully",
        }
    
    @api.model
    def get_user_appointments(self, patient_id):
        appointments = self.search([("patient_id", "=", patient_id),("status",'=','confirmed')])
        result = []
        for appt in appointments:
            result.append({
                "id": appt.id,
                "date_time": appt.start_datetime.strftime("%d %b %Y | %I:%M %p"),
                "isCancelled": appt.state == "cancelled",
                "isCompleted": appt.state == "completed",
                "doctor": {
                    "name": appt.provider_id.name,
                }
            })
        return result