from odoo import models, api, fields, _

class LabOrder(models.Model):
    _name = "lab.order"
    _description = "Lab Order"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    name = fields.Char("Order Reference", required=True, default=lambda self: _('New'), copy=False, readonly=True)
    patient_id = fields.Many2one("patient.record", string="Patient", required=True, ondelete="restrict", tracking=True)
    patient_name = fields.Char("Patient Name", related="patient_id.name", readonly=True)
    ordered_by = fields.Many2one("res.users", string="Ordered By", required=True, default=lambda self: self.env.user, tracking=True)
    line_ids = fields.One2many("lab.order.line", "order_id", string="Ordered Tests")
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def create(self, vals):
       if vals.get('name', _('New')) == _('New'):
           vals['name'] = self.env['ir.sequence'].next_by_code('lab.order')
       return super(LabOrder, self).create(vals)



class LabOrderLine(models.Model):
    _name = "lab.order.line"
    _description = "Lab Order Line"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Order Line Reference", required=True, default=lambda self: _('New'), copy=False, readonly=True)
    order_id = fields.Many2one("lab.order", string="Lab Order", required=True, ondelete="cascade")
    patient_id = fields.Many2one("patient.record", string="Patient", related="order_id.patient_id", store=True, readonly=True)
    patient_name = fields.Char("Patient Name", related="patient_id.name", readonly=True)
    test_type_id = fields.Many2one("lab.test.type", string="Test Type", required=True)
    result_id = fields.Many2one("lab.result", string="Lab Result")
    parameter_result_ids = fields.One2many(string="Parameter Results", related="result_id.parameter_result_ids", readonly=False)
    reference_number = fields.Char("Reference Number")
    state = fields.Selection([
        ("draft", "Draft"),
        ("requested", "Requested"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    ], string="Status", default="draft", tracking=True)
    rejection_reason = fields.Text("Rejection Reason")
    accepted_by = fields.Many2one("res.users", string="Accepted By", tracking=True)
    rejected_by = fields.Many2one("res.users", string="Rejected By", tracking=True)
    notes = fields.Text("Notes")
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def create(self, vals):
       if vals.get('name', _('New')) == _('New'):
           vals['name'] = self.env['ir.sequence'].next_by_code('lab.order.line')
       return super(LabOrderLine, self).create(vals)
    
    def _ensure_result(self):
        if not self.result_id:
            self.result_id = self.env['lab.result'].create({
                'order_line_id': self.id,
            })
            print(f"Created Lab Result with ID: {self.result_id.id}")
    
    def confirm_order(self):
        if self.state != 'draft':
            raise models.ValidationError(_("You can't confirm a non-draft order"))
        self.write({'state':'requested'})
        self._ensure_result()

    def accept_order(self):
        if self.state == 'requested':
            self.write({'state': 'accepted', 'accepted_by': self.env.user})
            self._ensure_result()
        else:
            raise models.ValidationError(_("Only requested orders can be accepted."))
    
    def reject_order(self):
        if self.state in ['accepted','requested']:
            self.write({'state': 'rejected', 'rejected_by': self.env.user})
        else:
            raise models.ValidationError(_("Only requested/accepted orders can be rejected."))
    
    def mark_completed(self):
        result = self.env['lab.result'].search([('order_line_id', '=', self.id)], limit=1)
        if self.state == 'accepted':
            if not result:
                raise models.ValidationError(_("Cannot mark as completed without associated results."))
            self.write({'state': 'completed'})
        else:
            raise models.ValidationError(_("Only accepted orders can be marked as completed."))

    def action_view_results(self):
        result = self.env['lab.result'].search([('order_line_id', '=', self.id)], limit=1)
        vals = {
            'type': 'ir.actions.act_window',
            'name': 'Lab Results',
            'res_model': 'lab.result',
            'view_mode': 'form',
            'target': 'new',
        }
        if result:
            vals["res_id"] = result.id
        else:
            vals['context'] = {'default_order_line_id': self.id}
        return vals
    
    def _compute_result_id(self):
        for rec in self:
            result = self.env['lab.result'].search([('order_line_id', '=', rec.id)], limit=1)
            rec.result_id = result.id if result else False