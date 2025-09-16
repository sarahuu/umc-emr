from odoo import fields, api, models, _


class PatientForm(models.Model):
    _name = "patient.form"
    _description = "Patient Forms"
    _order = "create_date desc"

    patient_id = fields.Many2one("patient.record", required=True, ondelete="cascade")
    form_type_id = fields.Many2one("emr.form.type", required=True)
    form_name = fields.Char('Form Name', related="form_type_id.form_name")
    reference_model = fields.Char("Model Name", related="form_type_id.model_id.model")
    reference_id = fields.Integer("Record ID")
    record_ref = fields.Reference(selection="_select_form_model",string="Form Record", help="Reference to the form record", default=False)
    created_by = fields.Many2one('res.users', string="Created By", default=lambda self: self.env.user, help="User who recorded this form")
    active = fields.Boolean(string="Active", default=True, help="Is this form active?")

    @api.model
    def _select_form_model(self):
        form_models = self.env['emr.form.type'].search([])
        return [(form_model.model_id.model, form_model.model_id.name) for form_model in form_models]

    
    @api.model
    def create(self, vals):
        record = super().create(vals)
        form_id = self.env['emr.form.type'].browse(vals.get('form_type_id'))
        model_name = form_id.model_id.model
        if model_name:
            sub_record =self.env[model_name].create({
                'patient_id': record.patient_id.id,
            })
            record.reference_id = sub_record.id
            record.record_ref = f"{model_name},{sub_record.id}"
        return record
    
    def action_open_form(self):
        self.ensure_one()
        if self.record_ref:
            return {
                "type": "ir.actions.act_window",
                "res_model": self.form_type_id.model_id.model,
                "res_id": self.reference_id,
                "view_mode": "form",
                "target": "new",
                "context": {"default_patient_id": self.patient_id.id}
            }

class SOAPForm(models.Model):
    _name = "patient.form.soap"
    _description = "SOAP Form"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    patient_id = fields.Many2one("patient.record", string="Patient", required=True, ondelete="cascade")
    name = fields.Char(string="Name", default="New", compute="_compute_name")
    subjective = fields.Text(string="Subjective", help="Subjective information provided by the patient", tracking=True)
    objective = fields.Text(string="Objective", help="Objective findings observed by the healthcare provider", tracking=True)
    assessment = fields.Text(string="Assessment", help="Assessment of the patient's condition", tracking=True)
    plan = fields.Text(string="Plan", help="Plan for treatment and follow-up", tracking=True)
    recorded_by = fields.Many2one('res.users', string="Recorded By", default=lambda self: self.env.user, help="User who recorded this form")
    active = fields.Boolean(string="Active", default=True, help="Is this form active?")


    @api.depends('patient_id')
    def _compute_name(self):
        for record in self:
            record.name = f"[{record.id}] {record.patient_id.name or 'Unknown Patient'} - {'SOAP Form'}"
