from odoo import models, fields, api, _


class PatientRecord(models.Model):
    _inherit = 'patient.record'

    lab_order_count = fields.Integer(string="Lab Order Count", compute="_compute_lab_order_count")
    lab_order_ids = fields.One2many('lab.order', 'patient_id', string="Lab Orders", help="Lab orders associated with this patient")

    @api.depends('lab_order_ids')
    def _compute_lab_order_count(self):
        for rec in self:
            rec.lab_order_count = len(rec.lab_order_ids)

    def action_open_lab_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lab Orders',
            'res_model': 'lab.order',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }