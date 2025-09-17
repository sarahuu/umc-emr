from odoo import models, fields, api
import random
from odoo.tools import populate
from faker import Faker
import logging
_logger = logging.getLogger(__name__)
fake = Faker()


class EMRProvider(models.Model):
    _name = 'emr.provider'
    _description = 'EMR Provider Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    first_name = fields.Char(string="First Name", required=True, tracking=True)
    last_name = fields.Char(string="Last Name", required=True, tracking=True)
    name = fields.Char(
        string="Full Name",
        compute='_compute_full_name',
        store=True,
        index=True,
        tracking=True
    )
    email = fields.Char(string="Email", tracking=True)
    phone = fields.Char(string="Phone", tracking=True)
    image_1920 = fields.Binary(string="Image", attachment=True)

    user_id = fields.Many2one('res.users', ondelete='restrict')
    partner_id = fields.Many2one('res.partner', ondelete='restrict')
    specialty_ids = fields.Many2many('provider.specialty', string="Specialties")
    service_ids = fields.Many2many('medical.service', string="Clinic Types")
    license_number = fields.Char(string="License Number", index=True, tracking=True)
    about = fields.Text("About")
    active = fields.Boolean(default=True, tracking=True)

    _sql_constraints = [
        ('uniq_license_number', 'unique(license_number)', 'License number must be unique!')
    ]

    @api.depends('first_name', 'last_name')
    def _compute_full_name(self):
        for rec in self:
            rec.name = " ".join(filter(None, [rec.first_name, rec.last_name]))

    @api.model
    def create(self, vals):
        partner = self.env['res.partner'].create({
            'name': f"{vals.get('first_name', '')} {vals.get('last_name', '')}".strip(),
            'email': vals.get('email'),
            'phone': vals.get('phone'),
        })
        vals['partner_id'] = partner.id
        rec = super().create(vals)
        if rec.email and not rec.user_id:
            group_id = self.env.ref('emr_config.group_emr_provider').id
            rec.user_id = self.env['res.users'].create({
                'name': rec.name,
                'login': rec.email,
                'partner_id': rec.partner_id.id,
                'groups_id': [(6, 0, [group_id])],
            })
        return rec

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec.partner_id.write({
                'name': rec.name,
                'email': rec.email,
                'phone': rec.phone,
            })
        return res
    
    def get_doctor_data(self):
        doctors = []
        for provider in self.search([('active', '=', True)]):
            speciality_names = ", ".join(provider.specialty_ids.mapped("name"))
            for service in provider.service_ids:
                doctors.append({
                    "_id": provider.id,
                    "name": provider.name,
                    "speciality": speciality_names,
                    "about": provider.about or "",
                    "clinic_type": service.name,
                    "clinic_type_slug": service.slug
                })
        return doctors
    
    _populate_sizes = {"small": 10, "medium": 100, "large": 1000}

    def _populate_factories(self):
        specialties = self.env['provider.specialty'].search([], limit=50).ids
        services = self.env['medical.service'].search([], limit=50).ids

        return [
            ("first_name", populate.random_firstnames()),
            ("last_name", populate.random_lastnames()),
            ("email", populate.email()),
            ("phone", populate.phonenumbers()),
            ("license_number", populate.seq("LIC-{:05d}")),  # unique sequence
            ("about", populate.lorem()),
            ("specialty_ids", populate.cartesian(specialties, min_size=1, max_size=3)),
            ("service_ids", populate.cartesian(services, min_size=1, max_size=2)),
            ("active", populate.randomize([True, False])),
        ]



