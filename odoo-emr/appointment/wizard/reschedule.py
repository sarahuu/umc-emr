from odoo import models, fields, api

class RescheduleWizard(models.TransientModel):
    _name = 'appointment.reschedule.wizard'
    _description = 'Reschedule Wizard'

    appointment_id = fields.Many2one('appointment.appointment', string="Appointment")
    old_timeslot_id = fields.Many2one('appointment.available.slot', string="Current Time Slot", related="appointment_id.granular_slot_id", readonly=True)
    service_type_id = fields.Many2one('medical.service', string="Clinic Type")
    timeslot_id = fields.Many2one(
        'appointment.available.slot',
        string="New Time Slot",
        domain="[('service_type', '=', service_type_id),('is_booked', '=', False)]",
    )
    provider_id = fields.Many2one('emr.provider', string="Provider")
    location_id = fields.Many2one('emr.locations', string="Location")
    new_date = fields.Datetime("New Date")

    @api.onchange('timeslot_id')
    def _onchange_timeslot_id(self):
        if self.timeslot_id:
            self.service_type_id = self.timeslot_id.service_type
            self.provider_id = self.timeslot_id.provider_id
            self.location_id = self.timeslot_id.location_id
            self.new_date = self.timeslot_id.start_datetime
        else:
            self.service_type_id = False
            self.provider_id = False
            self.location_id = False
            self.new_date = False

    def confirm_reschedule(self):
        if not self.appointment_id:
            raise models.ValidationError("Please select an appointment")
        if self.timeslot_id and self.timeslot_id.is_booked:
            raise models.ValidationError("The current time slot is already booked.")
        if self.old_timeslot_id:
            self.old_timeslot_id.write({'is_booked': False})

        self.appointment_id.write({
            'service_type': self.service_type_id.id if not self.timeslot_id else self.timeslot_id.service_type.id,
            'provider_id': self.provider_id.id if not self.timeslot_id else self.timeslot_id.provider_id.id,
            'location_id': self.location_id.id if not self.timeslot_id else self.timeslot_id.location_id.id,
            'start_datetime': self.new_date if not self.timeslot_id else self.timeslot_id.start_datetime,
            'granular_slot_id': self.timeslot_id.id if self.timeslot_id else False,
            'state': 'requested',
            'date_confirmed':fields.Datetime.now()
        })
        
        self.timeslot_id.write({'is_booked': True})
        return {'type': 'ir.actions.act_window_close'}
