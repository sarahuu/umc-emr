from odoo import models, fields, api, _


class PatientRecord(models.Model):
    _inherit = 'patient.record'

    prescription_order_count = fields.Integer(string="Prescription Order Count", compute="_compute_prescription_order_count")
    prescription_order_ids = fields.One2many('prescription.order', 'patient_id', string="Prescription Orders", help="Prescription orders associated with this patient")

    @api.depends('prescription_order_ids')
    def _compute_prescription_order_count(self):
        for rec in self:
            rec.prescription_order_count = len(rec.prescription_order_ids)

    def action_open_prescription_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'prescription Orders',
            'res_model': 'prescription.order',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }