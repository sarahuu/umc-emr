from odoo import models, fields, api, _

class PatientImmunization(models.Model):
    _name = 'patient.immunization'
    _description = 'Patient Immunization'
    _rec_name = 'name'
    _order = 'immunization_id desc'

    name = fields.Char(string="Immunization Name", compute="_compute_name", store=True)
    immunization_id = fields.Many2one('medical.immunization', string="Immunization", required=True, ondelete='cascade')
    patient_id = fields.Many2one('patient.record', string="Patient", required=True, ondelete='cascade')
    child_ids = fields.One2many('patient.immunization.line', 'parent_id', string="Doses")
    last_dose_taken = fields.Many2one('patient.immunization.line', compute="_compute_last_dose_taken", string="Last Dose Taken")
    active = fields.Boolean(string="Active", default=True)

    @api.depends('immunization_id')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.immunization_id.emr_name if rec.immunization_id else _('New')

    @api.depends('child_ids.vaccination_date')
    def _compute_last_dose_taken(self):
        for rec in self:
            doses_with_date = rec.child_ids.filtered(lambda d: d.vaccination_date)
            rec.last_dose_taken = max(doses_with_date, key=lambda x: x.vaccination_date) if doses_with_date else False

    @api.onchange('immunization_id')
    def _onchange_immunization_id(self):
        if self.immunization_id:
            self.name = self.immunization_id.emr_name

    def action_view_child_immunizations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} Doses',
            'res_model': 'patient.immunization.line',
            'view_mode': 'list,form',
            'domain': [('parent_id', '=', self.id)],
            'context': {'default_parent_id': self.id},
            'target': 'new',
        }


class PatientImmunizationLine(models.Model):
    _name = 'patient.immunization.line'
    _description = 'Patient Immunization Line'

    parent_id = fields.Many2one('patient.immunization', string="Parent Immunization", required=True, ondelete='cascade')
    immunization_number = fields.Char(string="Immunization Number", readonly=True, copy=False, default='New')
    dose_number = fields.Integer(string="Dose Number", required=True, default=1)
    vaccination_date = fields.Datetime(string="Vaccination Date", required=True)
    manufacturer = fields.Char(string="Manufacturer")
    lot_number = fields.Char(string="Lot Number")
    expiration_date = fields.Date(string="Expiration Date")
    recorded_by = fields.Many2one('res.users', string="Recorded By", default=lambda self: self.env.user)
    
    name = fields.Char(string="Immunization Name", compute="_compute_name", store=True)
    immunization_id = fields.Many2one('medical.immunization', related="parent_id.immunization_id", string="Immunization", readonly=True)

    @api.model
    def create(self, vals):
        vals['immunization_number'] = self.env['ir.sequence'].next_by_code('patient.immunization.line') or 'New'
        return super(PatientImmunizationLine, self).create(vals)

    @api.depends('parent_id', 'dose_number', 'vaccination_date')
    def _compute_name(self):
        for rec in self:
            if rec.parent_id and rec.vaccination_date:
                vacc_date_dt = fields.Datetime.to_datetime(rec.vaccination_date)
                immun_name = rec.parent_id.immunization_id.emr_name if rec.parent_id.immunization_id else _('New')
                rec.name = f"{immun_name} Dose-{rec.dose_number} on {vacc_date_dt.strftime('%B %d, %Y')}"
            else:
                rec.name = _('New')
