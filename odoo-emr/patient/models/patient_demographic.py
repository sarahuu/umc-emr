from odoo import models, fields, api, _
from datetime import date



class PatientDemographicStudent(models.Model):
    _name = 'patient.demographic.student'
    _description = 'Student Medical Records'

    matric_number = fields.Char(string="Matric Number", required=True)
    faculty_id = fields.Many2one('university.faculties', string="Faculty")
    department_id = fields.Many2one('university.departments', string="Department",domain="[('faculty_id', '=', faculty_id)]")
    level = fields.Selection([('100', '100 Level'), ('200', '200 Level'), ('300', '300 Level'), ('400', '400 Level'), ('500', '500 Level'), ('600', '600 Level')])
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ('uniq_matric_number', 'unique(matric_number)', 'Matric Number must be unique!')
    ]
    
class PatientDemographicStaff(models.Model):
    _name = 'patient.demographic.staff'
    _description = 'Staff Medical Records'

    staff_number = fields.Char(string="Staff ID")
    employment_type = fields.Selection([('academic', 'Academic'), ('non_academic', 'Non-Academic')])
    designation = fields.Char(string="Designation")
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ('uniq_staff_number', 'unique(staff_number)', 'Staff ID must be unique!')
    ]


class PatientDemographic(models.Model):
    _name = 'patient.demographic'
    _description = 'Patient Demographic Information'

    first_name = fields.Char(string="First Name", required=True)
    last_name = fields.Char(string="Last Name", required=True)
    other_name = fields.Char(string="Other Name")
    name = fields.Char(string="Full Name",compute='_compute_full_name',store=True,index=True)
    gender = fields.Selection([('male', 'Male'),('female', 'Female'),('other', 'Other'),('unknown', 'Unknown')], string="Gender", required=True)
    age = fields.Integer("Age",compute='_compute_age', store=True, readonly=True)
    date_of_birth = fields.Date(string="Date of Birth")
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('unknown', 'Unknown')
    ], string="Marital Status")
    next_of_kin_name = fields.Char(string="Next of Kin Name")
    next_of_kin_relationship = fields.Selection(string="Relationship",selection=[
        ('spouse', 'Spouse'),
        ('parent', 'Parent'),
        ('child', 'Child'),
        ('sibling', 'Sibling'),
        ('other', 'Other'),
    ])
    next_of_kin_phone = fields.Char(string="Next of Kin Phone")
    member_type = fields.Selection([
        ('student', 'Student'), 
        ('staff', 'Staff'),
    ], string="Member Type", required=True, default='student')
    student_demographic_id = fields.Many2one('patient.demographic.student', string="Student Demographic", ondelete='restrict')
    staff_demographic_id = fields.Many2one('patient.demographic.staff', string="Staff Demographic", ondelete='restrict')
   
    
    #partner_id fields
    partner_id = fields.Many2one('res.partner', string="Partner", required=True, ondelete='restrict')
    title = fields.Many2one('res.partner.title', string="Title", related="partner_id.title", readonly=False)
    email = fields.Char(string="Email", required=True, related="partner_id.email", readonly=False)
    street = fields.Char(string="Street", related="partner_id.street", readonly=False)
    street2 = fields.Char(string="Street2", related="partner_id.street2", readonly=False)
    zip = fields.Char(string="ZIP", change_default=True, related="partner_id.zip", readonly=False)
    city = fields.Char(string="City", related="partner_id.city", readonly=False)
    state_id = fields.Many2one("res.country.state", string='State', domain="[('country_id', '=', country_id)]", related="partner_id.state_id", readonly=False)
    country_id = fields.Many2one('res.country', string='Country',  related="partner_id.country_id", readonly=False)
    phone = fields.Char(string="Phone Number", related="partner_id.phone", readonly=False)
    mobile = fields.Char(string="Mobile Number", related="partner_id.mobile", readonly=False)

    _sql_constraints = [
        ('email_unique', 'unique(email)', 'Email must be unique!')
    ]
    
    @api.constrains('member_type', 'student_demographic_id', 'staff_demographic_id')
    def _check_member_type_consistency(self):
        for rec in self:
            if rec.member_type == 'student' and rec.staff_demographic_id:
                raise models.ValidationError("Student cannot have staff demographic data.")
            if rec.member_type == 'staff' and rec.student_demographic_id:
                raise models.ValidationError("Staff cannot have student demographic data.")
    
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = f"{vals.get('first_name', '')} {vals.get('last_name', '')}".strip() or 'Unnamed'
        partner_vals = {
            'name': vals.get('name', 'Unnamed'),
            'email': vals.get('email'),
            'phone': vals.get('phone'),
            'street': vals.get('street'),
            'street2': vals.get('street2'),
            'city': vals.get('city'),
            'state_id': vals.get('state_id'),
            'country_id': vals.get('country_id'),
            'zip': vals.get('zip'),
            'mobile': vals.get('mobile'),
        }
        partner_id = self.env['res.partner'].create(partner_vals)
        vals['partner_id'] = partner_id.id
        record = super(PatientDemographic, self).create(vals)
        return record

    def write(self, vals):
        if 'name' in vals:
            vals['name'] = f"{vals.get('first_name', '')} {vals.get('last_name', '')}".strip() or 'Unnamed'
        res = super(PatientDemographic, self).write(vals)
        return res

    @api.depends('date_of_birth')
    def _compute_age(self):
        today = date.today()
        for patient in self:
            if patient.date_of_birth:
                dob = patient.date_of_birth
                patient.age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            else:
                patient.age = 0

    @api.depends('first_name', 'last_name')
    def _compute_full_name(self):
        for record in self:
            names = [record.first_name or '', record.last_name or '']
            record.name = ' '.join(filter(None, names))


