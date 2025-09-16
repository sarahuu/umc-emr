from odoo import models, fields, api


class StudentFaculties(models.Model):
    _name = 'university.faculties'
    _description = 'Student Faculties'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Faculty Name", required=True)
    code = fields.Char(string="Faculty Code", required=True)
    active = fields.Boolean(string="Active", default=True)
    _sql_constraints = [
        ('uniq_name', 'unique(name)', 'Faculty Name must be unique!'),
        ('uniq_code', 'unique(code)', 'Faculty Code must be unique!'),
    ]


class StudentDepartments(models.Model):
    _name = 'university.departments'
    _description = 'Student Departments'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Department Name", required=True)
    code = fields.Char(string="Department Code", required=True)
    faculty = fields.Many2one('university.faculties', string="Faculty", required=True, ondelete='restrict')
    active = fields.Boolean(string="Active", default=True)
    _sql_constraints = [
        ('uniq_name', 'unique(name)', 'Department Name must be unique!'),
        ('uniq_code', 'unique(code)', 'Department Code must be unique!'),
    ]
