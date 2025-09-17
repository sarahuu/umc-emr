from odoo import models, fields, api, _
import random
from odoo.tools import populate
from faker import Faker
import logging
_logger = logging.getLogger(__name__)
fake = Faker()


class PatientRecord(models.Model):
    _name = 'patient.record'
    _description = 'Patient Record Information'
    _rec_name = 'patient_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    user_id = fields.Many2one('res.users', string="User Account", help="Associated Odoo user account")
    patient_id = fields.Char(string="Identifier", readonly=True, copy=False, default='New')
    allergies_ids = fields.One2many('patient.allergies', 'patient_id', string="Allergies", tracking=True)
    immunization_ids = fields.One2many('patient.immunization', 'patient_id', string="Immunizations", tracking=True)
    form_ids = fields.One2many('patient.form', 'patient_id', string="Forms", help="Forms associated with this patient", tracking=True)
    demographic_id = fields.Many2one('patient.demographic', string="Patient Demographic", ondelete="restrict")
    vitals_ids = fields.One2many('patient.vitals', 'patient_id', string="Vitals Records",tracking=True)
    blood_pressure = fields.Char(string="BP (mmHg)", compute="_compute_vitals")
    respiratory_rate = fields.Integer(string="R.Rate (breaths/min)", compute="_compute_vitals")
    spo2 = fields.Float(string="SpO₂(%)", compute="_compute_vitals")
    heart_rate = fields.Integer(string="H.Rate (bpm)", compute="_compute_vitals")
    temperature = fields.Float(string="Temperature (°C)", compute="_compute_vitals")
    weight = fields.Float(string="Weight (kg)", compute="_compute_vitals")
    height = fields.Integer(string="Height (cm)", compute="_compute_vitals")
    biometrics_ids = fields.One2many('patient.biometrics', 'patient_id', string="Biometric Records", tracking=True)
    conditions_ids = fields.One2many('patient.conditions', 'patient_id', string="Medical Conditions", tracking=True)
    name = fields.Char(string="Name", related="demographic_id.name", store=True, index=True)
    gender = fields.Selection(related="demographic_id.gender", store=True)
    age = fields.Integer(related="demographic_id.age", store=True)
    member_type = fields.Selection([
        ('student', 'Student'), 
        ('staff', 'Staff'),
    ], string="Member Type", store=True)
    image_1920 = fields.Binary(string="Image")
    is_deceased = fields.Boolean("Deceased", default=False, tracking=True)
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
    ('uniq_patient_id', 'unique(patient_id)', 'The patient ID must be unique!')
]


    @api.model
    def create(self, vals):
        if vals.get('patient_id', 'New') == 'New':
            vals['patient_id'] = self.env['ir.sequence'].next_by_code('patient.record') or _('New')
        record = super(PatientRecord, self).create(vals)
        if not record.user_id and record.demographic_id and record.demographic_id.partner_id:
            user_vals = {
                'name': record.name,
                'login': record.demographic_id.email,
                'partner_id': record.demographic_id.partner_id.id,
                'groups_id': [(6, 0, [self.env.ref('emr_config.group_emr_patient').id])]
            }
            record.user_id = self.env['res.users'].create(user_vals)
        if record.image_1920:
            record.demographic_id.partner_id.image_1920 = record.image_1920
        return record
    def write(self, vals):

        res = super(PatientRecord, self).write(vals)
        self.demographic_id.partner_id.image_1920 = self.image_1920
        if 'email' in vals:
            self.user_id.partner_id.email = vals['email']
        return res
    
    def action_view_vitals_graph(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vitals Trend',
            'res_model': 'patient.vitals',
            'view_mode': 'graph',
            'views': [(False, 'graph')],
            'domain': [('patient_id', '=', self.id)],
            'context': {'search_default_group_by_recorded_at': 1},
            'target': 'new',
        }

    def action_view_biometrics_graph(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Biometrics Trend',
            'res_model': 'patient.biometrics',
            'view_mode': 'graph',
            'views': [(False, 'graph')],
            'domain': [('patient_id', '=', self.id)],
            'context': {'search_default_group_by_recorded_at': 1},
            'target': 'new',
        }
    
    @api.depends('vitals_ids','biometrics_ids')
    def _compute_vitals(self):
        latest_vital = self.vitals_ids.sorted(key='recorded_at', reverse=True)[:1]
        latest_biometric = self.biometrics_ids.sorted(key='recorded_at', reverse=True)[:1]
        for rec in self:
            rec.blood_pressure = latest_vital.blood_pressure
            rec.respiratory_rate = latest_vital.respiratory_rate
            rec.spo2 = latest_vital.spo2
            rec.heart_rate = latest_vital.heart_rate
            rec.temperature = latest_vital.temperature
            rec.weight = latest_biometric.weight
            rec.height = latest_biometric.height

     # --- populate config ---
    _populate_sizes = {"small": 50, "medium": 500, "large": 5000}

    def _populate_factories(self):
        return [
            ("member_type", lambda: random.choice(['student', 'staff'])),
            ("demographic_id", lambda: self.env['patient.demographic'].populate('small')[0].id)
        ]

    def _populate_dependencies(self):
        # ensure demographics are populated first
        return ['patient.demographic']

    def _populate(self, size):
        records = super()._populate(size)
        _logger.info("Populated %s PatientRecord(s)", len(records))
        return records


class PatientRecordDemographic(models.Model):
    _inherit = 'patient.record'

    first_name = fields.Char(string="First Name", related="demographic_id.first_name", readonly=False)
    last_name = fields.Char(string="Last Name", related="demographic_id.last_name", readonly=False)
    email = fields.Char('Email', related="demographic_id.email", readonly=False)
    other_name = fields.Char(string="Other Name", related="demographic_id.other_name", readonly=False)
    gender = fields.Selection(string="Gender", related="demographic_id.gender",readonly=False, store=True)
    age = fields.Integer(string="Age", related="demographic_id.age", store=True)
    date_of_birth = fields.Date(string="Date of Birth", related="demographic_id.date_of_birth", readonly=False)
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('unknown', 'Unknown')
    ], string="Marital Status", related="demographic_id.marital_status", readonly=False)
    next_of_kin_name = fields.Char(string="Next of Kin Name", related="demographic_id.next_of_kin_name", readonly=False)
    next_of_kin_relationship = fields.Selection(string="Relationship",selection=[
        ('spouse', 'Spouse'),
        ('parent', 'Parent'),
        ('child', 'Child'),
        ('sibling', 'Sibling'),
        ('other', 'Other'),
    ], related="demographic_id.next_of_kin_relationship", readonly=False)
    next_of_kin_phone = fields.Char(string="Next of Kin Phone", related="demographic_id.next_of_kin_phone", readonly=False)
    matric_number = fields.Char(string="Matric Number", related="demographic_id.student_demographic_id.matric_number", readonly=False)
    department_id = fields.Many2one('university.departments', string="Department", related="demographic_id.student_demographic_id.department_id", readonly=False)
    faculty_id = fields.Many2one('university.faculties', string="Faculty", related="demographic_id.student_demographic_id.faculty_id", readonly=False)
    level = fields.Selection([('100', '100 Level'), ('200', '200 Level'), ('300', '300 Level'), ('400', '400 Level'), ('500', '500 Level'), ('600', '600 Level')], related="demographic_id.student_demographic_id.level", string="Level", readonly=False)
    staff_number = fields.Char(string="Staff ID", related="demographic_id.staff_demographic_id.staff_number", readonly=False)
    employment_type = fields.Selection([('academic', 'Academic'), ('non_academic', 'Non-Academic')], related="demographic_id.staff_demographic_id.employment_type", string="Employment Type", readonly=False)
    designation = fields.Char(string="Designation", related="demographic_id.staff_demographic_id.designation", readonly=False)
    title = fields.Many2one('res.partner.title',related='demographic_id.partner_id.title',readonly=False,string='Title')
    phone = fields.Char(related='demographic_id.partner_id.phone',readonly=False,string='Phone')
    mobile = fields.Char(related='demographic_id.partner_id.mobile',readonly=False,string='Mobile')
    street = fields.Char(related='demographic_id.partner_id.street',readonly=False,string='Street')
    street2 = fields.Char(related='demographic_id.partner_id.street2',readonly=False,string='Street2')
    city = fields.Char(related='demographic_id.partner_id.city',readonly=False,string='City')
    state_id = fields.Many2one('res.country.state',related='demographic_id.partner_id.state_id',readonly=False,string='State')
    zip = fields.Char(related='demographic_id.partner_id.zip',readonly=False,string='ZIP')
    country_id = fields.Many2one('res.country',related='demographic_id.partner_id.country_id',readonly=False,string='Country')


    @api.model
    def create(self, vals):
        demographic_fields = [
            'first_name', 'last_name', 'email', 'phone', 'gender', 'date_of_birth',
            'marital_status', 'other_name', 'next_of_kin_name', 'next_of_kin_relationship',
            'next_of_kin_phone'
        ]
        demographic_vals = {field: vals.get(field) for field in demographic_fields if vals.get(field)}
        demographic_vals['name'] = f"{vals.get('first_name', '')} {vals.get('last_name', '')}".strip() or 'Unnamed'
        student_demographic = staff_demographic = None

        try:
            if 'member_type' in vals and vals.get('member_type') == 'student':
                student_vals = {
                    'matric_number': vals.get('matric_number'),
                    'department_id': vals.get('department_id'),
                    'faculty_id': vals.get('faculty_id'),
                    'level': vals.get('level')
                }
                student_demographic = self.env['patient.demographic.student'].create(student_vals)
                demographic_vals['student_demographic_id'] = student_demographic.id

            elif 'member_type' in vals and vals.get('member_type') == 'staff':
                staff_vals = {
                    'staff_number': vals.get('staff_number'),
                    'employment_type': vals.get('employment_type'),
                    'designation': vals.get('designation')
                }
                staff_demographic = self.env['patient.demographic.staff'].create(staff_vals)
                demographic_vals['staff_demographic_id'] = staff_demographic.id
            demographic = self.env['patient.demographic'].create(demographic_vals)
            vals['demographic_id'] = demographic.id
            record = super(PatientRecordDemographic, self).create(vals)
        except Exception as e:
            raise models.ValidationError(_("Failed to create patient demographic: %s") % str(e))
        return record
    
    @api.onchange('first_name', 'last_name')
    def _onchange_name(self):
        for record in self:
            record.name = f"{record.first_name or ''} {record.last_name or ''}".strip() or 'Unnamed'

