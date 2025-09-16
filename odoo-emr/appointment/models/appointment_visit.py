from odoo import models, api, fields, _


class EncounterGenerator(models.AbstractModel):
    _name = 'appointment.visit.encounter.generator'
    _description = 'Abstract Model for Encounter Generation'

    def create(self, vals):
        record = super().create(vals)
        mapping = self.env["emr.model.encounter.type"].search([
            ("model_id.model", "=", self._name)
        ], limit=1)

        if mapping:
            visit_id = self.env['appointment.visit'].search([('patient_id', '=', record.patient_id.id),('state','=','active')], limit=1)
            if not visit_id:
                raise models.ValidationError(_("No active visit found for the patient. Please start a visit for this patient."))
            self.env["appointment.visit.encounter"].create({
                "visit_id": visit_id.id,
                "encounter_record_id": "%s,%s" % (self._name, record.id),
                "start_datetime": fields.Datetime.now(),
                "encounter_type_id": mapping.encounter_type_id.id,
                "form_type_id": mapping.form_type_id.id,
            })
        return record


class AppointmentVisit(models.Model):
    _name = 'appointment.visit'
    _description = 'Appointment Visits'
    _rec_name = 'app_visit_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    app_visit_id = fields.Char(string="Visit ID", help="Unique identifier for the visit", default=lambda self: _('New'))
    visit_note_ids = fields.One2many('appointment.visit.note', 'parent_visit_id', string="Visit Notes", help="Notes associated with this visit", tracking=True)
    appointment_id = fields.Many2one('appointment.appointment', string="Appointment", help="Appointment associated with this visit",domain="[('patient_id', '=', patient_id),('status','=','confirmed')]", tracking=True)
    patient_id = fields.Many2one('patient.record', string="Patient", required=True, help="Patient associated with this visit")
    location_id = fields.Many2one('emr.locations', string="Location", required=True, tracking=True)
    diagnosis_ids = fields.Many2many('medical.conditions', string="Diagnoses", help="Medical conditions diagnosed during the visit", compute="_compute_diagnoses", tracking=True)
    visit_type = fields.Selection([('facility_visit','Facility Visit'), ('home_visit','Home Visit'), ('opd_visit','OPD Visit'), ('offline_visit','Offline Visit')], string="Visit Type", required=True)
    start_datetime = fields.Datetime(string="Start Date & Time", help="Start date and time of the visit")
    end_datetime = fields.Datetime(string="End Date & Time", help="End date and time of the visit")
    punctuality = fields.Selection([('on_time','On Time'), ('late','Late'), ('early','Early')], string="Punctuality", help="Punctuality of the visit", tracking=True)
    notes = fields.Text(string="Notes", help="Additional notes for the visit")
    status = fields.Selection([('new','New'),('ongoing','Ongoing'),('past','Past')], string="Status", default='new', help="Status of the visit")
    encounter_ids = fields.One2many('appointment.visit.encounter', 'visit_id', string="Encounters", help="Encounters associated with this visit", tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('ended', 'Ended'),
    ], string="State", default='draft', help="State of the visit")
    active = fields.Boolean(string="Active", default=True)

    @api.constrains('patient_id', 'state')
    def _check_single_active_visit(self):
        for visit in self:
            if visit.state == 'active':
                active_visits = self.search([
                    ('id', '!=', visit.id),
                    ('patient_id', '=', visit.patient_id.id),
                    ('state', '=', 'active')
                ])
                if active_visits:
                    raise models.ValidationError(
                        _("Patient %s already has an active visit.") % visit.patient_id.name
                    )

    def _compute_diagnoses(self):
        for rec in self:
            rec.diagnosis_ids = [(6, 0, rec.visit_note_ids.mapped('diagnosis_ids').ids)]
    
    @api.model
    def create(self, vals):
        if vals.get('app_visit_id', _('New'))==_('New'):
            vals['app_visit_id'] = self.env['ir.sequence'].next_by_code('appointment.visit')
        return super(AppointmentVisit, self).create(vals)

    def action_start(self):
        for rec in self:
            rec.write({'state': 'active'})
            rec.start_datetime = fields.Datetime.now()
            rec.message_post(body=f"Visit {rec.app_visit_id} started.")

    def action_end(self):
        for rec in self:
            rec.write({'state': 'ended'})
            rec.end_datetime = fields.Datetime.now()
            rec.message_post(body=f"Visit {rec.app_visit_id} ended.")
 
    @api.onchange('appointment_id')
    def _onchange_appointment_id(self):
        if self.appointment_id:
            self.location_id = self.appointment_id.location_id
            self.patient_id = self.appointment_id.patient_id

    def get_formview_action(self, access_uid=None):
        return {
            "name": "Visit Wizard",
            "type": "ir.actions.act_window",
            "res_model": "visit.wizard",
            "view_mode": "form",
            "target": "new", 
            "context": {"default_app_visit_id": self.id},
        }

    def get_visit_notes_action(self):
        return {
            "name": "Visit Notes",
            "type": "ir.actions.act_window",
            "res_model": "appointment.visit.note",
            "view_mode": "form",
            "target": "new",
            "context": {"default_parent_visit_id": self.id},
        }
    def unlink(self):
        for visit in self:
            if visit.encounter_ids:
                raise models.ValidationError("Cannot delete visit with linked encounters.")
        return super().unlink()


class AppointmentVisitNotes(models.Model):
    _name = 'appointment.visit.note'
    _description = 'Appointment Visit Notes'
    _inherit = ['appointment.visit.encounter.generator']

    parent_visit_id = fields.Many2one('appointment.visit', string="Visit", required=True, help="Visit associated with this note")
    patient_id = fields.Many2one('patient.record', string="Patient", related="parent_visit_id.patient_id",help="Patient associated with this note")
    diagnosis_ids = fields.Many2many('medical.conditions', string="Diagnoses", help="Medical conditions diagnosed during the visit")
    note = fields.Text(string="Note", required=True, help="Content of the note")
    image_id = fields.Many2many('ir.attachment', string="Images", help="Images related to the note")
    recorded_by = fields.Many2one('res.users', string="Recorded By", default=lambda self: self.env.user, help="User who recorded this note")
    active = fields.Boolean(string="Active", default=True, help="Is this note active?")


class AppointmentVisitEncounter(models.Model):
    _name = 'appointment.visit.encounter'
    _description = 'Appointment Visit Encounters'

    visit_id = fields.Many2one('appointment.visit', string="Visit", required=True, help="Visit associated with this encounter")
    encounter_record_id = fields.Reference(selection="_select_encounter_record", string="Encounter Record", help="Reference to the encounter record")
    encounter_type_id = fields.Many2one('emr.encounter.type', string="Encounter Type", help="Type of the encounter")
    start_datetime = fields.Datetime(string="Start Date & Time", required=True, help="Start date and time of the encounter")
    recorded_by = fields.Many2one('res.users', string="Recorded By", default=lambda self: self.env.user, help="User who recorded this encounter")
    form_type_id = fields.Many2one('emr.form.type', string="Form Name", help="Name of the form used for this encounter")
    active = fields.Boolean(string="Active", default=True, help="Is this encounter active?")

    @api.model
    def _select_encounter_record(self):
        models_encounter = self.env['emr.model.encounter.type'].search([])
        return [(model_encounter.model_id.model, model_encounter.model_id.name) for model_encounter in models_encounter]
    

