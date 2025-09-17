from odoo import models, fields, api, _
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class TimeSlot(models.Model):
    _name = 'appointment.timeslot'
    _description = 'Appointment Time Slot'
    _rec_name = 'timeslot_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    timeslot_id = fields.Char(string="Time Slot Name", default=_('New'))
    date = fields.Date(string="Date", required=True)
    start_time = fields.Float(string="Start Time (hours)", required=True)
    end_time = fields.Float(string="End Time (hours)", required=True)
    start_datetime = fields.Datetime(string="Start Datetime", compute="_compute_datetimes", store=True)
    end_datetime = fields.Datetime(string="End Datetime", compute="_compute_datetimes", store=True)
    provider_id = fields.Many2one('emr.provider', string="Provider", required=True)
    location_id = fields.Many2one('emr.locations', string="Location", required=True)
    duration = fields.Integer(string="Duration (minutes)", required=True, default=20)
    state = fields.Selection([('draft','Draft'),('posted','Posted'),('confirmed','Confirmed')], default='draft')
    # service_type = fields.Many2one('medical.service', string="Clinic Type", required=True, ondelete="cascade", domain="[('id', 'in', provider_id.service_ids.ids)]" if provider_id else [])
    available_slot_ids = fields.One2many('appointment.available.slot', 'slot_id', string="Granular Slots")
    active = fields.Boolean(default=True)

    service_type = fields.Many2one('medical.service', string="Clinic Type", required=True, ondelete="cascade",domain="[('id', 'in', allowed_service_type_ids)]")
    allowed_service_type_ids = fields.Many2many('medical.service',compute='_compute_allowed_service_types',string="Allowed Service Types")

    @api.depends('provider_id')
    def _compute_allowed_service_types(self):
        for record in self:
            if record.provider_id and record.provider_id.service_ids:
                # Assuming provider_id.service_type is a Many2many field
                record.allowed_service_type_ids = record.provider_id.service_ids.ids
            else:
                record.allowed_service_type_ids = False

    @api.model
    def create(self, vals):
        if vals.get('timeslot_id', _('New')) == _('New'):
            vals['timeslot_id'] = self.env['ir.sequence'].next_by_code('appointment.timeslot')
        return super().create(vals)

    @api.depends('date', 'start_time', 'end_time')
    def _compute_datetimes(self):
        for rec in self:
            if rec.date is not None:
                rec.start_datetime = datetime.combine(rec.date, datetime.min.time()) + timedelta(hours=rec.start_time)
                rec.end_datetime = datetime.combine(rec.date, datetime.min.time()) + timedelta(hours=rec.end_time)
            else:
                rec.start_datetime = False
                rec.end_datetime = False

    @api.constrains('date')
    def _check_future_date(self):
        for rec in self:
            if rec.date and rec.date < datetime.today().date():
                raise models.ValidationError(_("The appointment date must be today or a future date."))

    @api.constrains('start_datetime', 'end_datetime', 'provider_id')
    def _check_time_slot(self):
        for rec in self:
            if rec.start_datetime and rec.end_datetime and rec.start_datetime >= rec.end_datetime:
                raise models.ValidationError(_("Start time must be before end time."))

            overlapping = self.search([
                ('id', '!=', rec.id),
                ('provider_id', '=', rec.provider_id.id),
                ('start_datetime', '<', rec.end_datetime),
                ('end_datetime', '>', rec.start_datetime),
            ])
            if overlapping:
                raise models.ValidationError(_("This time slot overlaps with another slot for the same provider."))

    def generate_granular_slots(self):
        """Generates non-overlapping granular slots within this time slot."""
        self.available_slot_ids.unlink()
        start = self.start_datetime
        end = self.end_datetime
        duration = self.duration or 20

        while start < end:
            slot_end = start + timedelta(minutes=duration)
            if slot_end > end:
                break  # avoid creating partial slots beyond the end
            # Check overlap with existing slots
            overlapping = self.env['appointment.available.slot'].search([
                ('slot_id', '=', self.id),
                ('start_datetime', '<', slot_end),
                ('end_datetime', '>', start)
            ])
            if not overlapping:
                self.env['appointment.available.slot'].create({
                    'slot_id': self.id,
                    'start_datetime': start,
                    'end_datetime': slot_end,
                    'duration':self.duration,
                    'provider_id': self.provider_id.id,
                    'location_id': self.location_id.id,
                    'service_type': self.service_type.id
                })
            start = slot_end

    def action_post(self):
        for rec in self:
            if self.env['appointment.appointment'].search([('granular_slot_id.slot_id', '=', rec.id)]):
                raise models.ValidationError(_("Cannot post this time slot as there are linked appointments."))
            rec.available_slot_ids.unlink()
            rec.state = 'posted'

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'
            rec.generate_granular_slots()

    def action_reset(self):
        for rec in self:
            if self.env['appointment.appointment'].search([('granular_slot_id.slot_id', '=', rec.id)]) and rec.state != 'draft':
                raise models.ValidationError(_("Cannot reset this time slot as there are linked appointments."))
            rec.state = 'draft'
            rec.available_slot_ids.unlink()

    def unlink(self):
        for slot in self:
            booked_children = slot.available_slot_ids.filtered(lambda s: s.is_booked)
            if booked_children:
                raise models.ValidationError(_("Cannot delete this time slot because some granular slots are already booked."))
        return super(TimeSlot, self).unlink()

    @api.onchange('provider_id')
    def _onchange_provider_id(self):
        return {'domain': {'service_type': [('id', 'in', self.provider_id.service_ids.ids)] if self.provider_id else []}}



class AppointmentAvailableSlot(models.Model):
    _name = "appointment.available.slot"
    _description = "Available Appointment Slot"
    _rec_name = "available_slot_id"

    slot_id = fields.Many2one("appointment.timeslot", string="Time Slot Block", required=True, ondelete="cascade")
    available_slot_id = fields.Char(string="Available Slot ID", default=_('New'))
    start_datetime = fields.Datetime(required=True)
    end_datetime = fields.Datetime(required=True)
    start_time = fields.Float(compute="_compute_times", store=True)
    duration = fields.Integer(string="Duration (minutes)", help="Duration of the appointment in minutes", related="slot_id.duration")
    end_time = fields.Float(compute="_compute_times", store=True)
    provider_id = fields.Many2one("emr.provider", string="Provider", readonly=False, related="slot_id.provider_id")
    location_id = fields.Many2one("emr.locations", string="Location", readonly=False, related="slot_id.location_id")
    service_type = fields.Many2one("medical.service", string="Clinic Type", readonly=False, related="slot_id.service_type")
    is_booked = fields.Boolean(default=False)
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if vals.get('available_slot_id', _('New')) == _('New'):
            vals['available_slot_id'] = self.env['ir.sequence'].next_by_code('appointment.available.slot')
        return super().create(vals)
    
    def _get_display_name(self):
        result = {}
        for rec in self:
            display_time = format_datetime(
                self.env,
                rec.start_datetime,
                dt_format="dd-MMM-yyyy HH:mm",
                tz=self.env.user.tz or "UTC"
            )
            result[rec.id] = f"{rec.available_slot_id.display_name} - {display_time}"
        return result    
    @api.depends("start_datetime", "end_datetime")
    def _compute_times(self):
        for rec in self:
            rec.start_time = rec.start_datetime.hour + rec.start_datetime.minute / 60 if rec.start_datetime else 0
            rec.end_time = rec.end_datetime.hour + rec.end_datetime.minute / 60 if rec.end_datetime else 0

    @api.constrains("start_datetime", "end_datetime")
    def _check_time_validity(self):
        for rec in self:
            if rec.end_datetime <= rec.start_datetime:
                raise models.ValidationError(_("End time must be after start time."))

    def _cron_archive_expired_slots(self):
        today_start = fields.Datetime.to_datetime(fields.Date.context_today(self))
        today_end = today_start + timedelta(days=1)

        expired_slots = self.search([
            ('end_datetime', '<', today_end),
            ('active', '=', True),
        ])
        expired_slots.action_archive()



class EMRProvider(models.Model):
    _inherit = "emr.provider"

    is_available = fields.Boolean(
        string="Is Available",
        help="True if the provider has active available time slots"
    )

    def update_provider_availability(self):
        providers = self.search([])
        for provider in providers:
            active_slot = self.env["appointment.available.slot"].search_count([
                ("provider_id", "=", provider.id),
                ("active", "=", True),
                ('is_booked','=',False)
            ], limit=1)
            provider.is_available = bool(active_slot)

    def get_doctor_data(self):
        doctors = []
        for provider in self.search([('active', '=', True)]):
            speciality_names = ", ".join(provider.specialty_ids.mapped("name"))
            for service in provider.service_ids:
                doctors.append({
                    "id": provider.id,
                    "name": provider.name,
                    "speciality": speciality_names,
                    "about": provider.license_number or "",
                    "clinic_type": service.name,
                    "clinic_type_slug": service.slug,
                    "is_available": provider.is_available
                })
        return doctors
    

    def get_availability(self, clinic_type_slug):
        availability = []
        clinic_type = self.env['medical.service'].search([('slug','=',clinic_type_slug)])
        slots = self.env["appointment.available.slot"].search([
            ("provider_id", "=", self.id),
            ("service_type",'=', clinic_type.id),
            ("is_booked",'=',False),
            ("active", "=", True)
        ])
        slots_by_date = {}
        for slot in slots:
            slot_date = slot.start_datetime.date().isoformat()
            slot_time = slot.start_datetime.strftime("%H:%M")
            slots_by_date.setdefault(slot_date, []).append({'id':slot.id,'time':slot_time})

        for date, times in slots_by_date.items():
            availability.append({
                
                "date": date,
                "slots": times
            })

        return {
            "name": self.name,
            "about": self.about or "No about set",
            "doctor_id": self.id,
            "clinic_type": clinic_type.name,
            "clinic_type_slug": clinic_type.slug,
            "availability": availability
        }

    @api.model
    def get_doctor_availability(self, doctor_id, clinic_type):
        provider = self.browse(doctor_id)
        return provider.get_availability(clinic_type) if provider.exists() else {}
