from odoo import models, fields, api, _


class PatientRecord(models.Model):
    _inherit = 'patient.record'

    visit_count = fields.Integer(string="Visit Count", compute="_compute_visit_count")
    active_visit = fields.Boolean(string="Active Visit", compute="_compute_active_visit")
    visit_ids = fields.One2many('appointment.visit', 'patient_id', string="Visits", help="Visits associated with this patient")

    @api.depends('visit_ids')
    def _compute_active_visit(self):
        for rec in self:
            rec.active_visit = any(visit.state == 'active' for visit in rec.visit_ids)

    @api.depends('visit_ids')
    def _compute_visit_count(self):
        for rec in self:
            rec.visit_count = len(rec.visit_ids)

    def action_open_visits(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Visits',
            'res_model': 'appointment.visit',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }