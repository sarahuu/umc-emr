from odoo import models, fields, api, _

class EmrEncounterType(models.Model):
    _name = 'emr.encounter.type'
    _description = 'EMR Encounter Type'
    _rec_name = 'encounter_name'

    encounter_name = fields.Char(string='Encounter Name', required=True)
    active = fields.Boolean('Active',default=True)
    _sql_constraints = [
    ('uniq_encounter_name', 'unique(encounter_name)', 'Encounter name must be unique!')
]


class EmrFormType(models.Model):
    _name = 'emr.form.type'
    _description = 'EMR Form'
    _rec_name = 'form_name'

    form_name = fields.Char(string='Form Name', required=True)
    model_id = fields.Many2one('ir.model', string='Model', ondelete="cascade", required=True)
    active = fields.Boolean('Active',default=True)
    _sql_constraints = [
    ('uniq_form_name', 'unique(form_name)', 'Form name must be unique!')
]


class EmrModelEncounterType(models.Model):
    _name = 'emr.model.encounter.type'
    _description = 'EMR Model Encounter Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'encounter_type_id'

    model_id = fields.Many2one('ir.model', string='Model', ondelete="cascade", required=True)
    encounter_type_id = fields.Many2one('emr.encounter.type', string='Encounter Type', ondelete="restrict", required=True, domain="[('active', '=', True)]")
    form_type_id = fields.Many2one('emr.form.type', string='Form Type', ondelete="restrict", domain="[('active', '=', True)]")
    active = fields.Boolean('Active',default=True)
    _sql_constraints = [
    ('uniq_model_encounter_form', 'unique(model_id, encounter_type_id, form_type_id)',
     'This combination of model, encounter type, and form type already exists.')
]
    def _get_display_name(self):
        result = {}
        for rec in self:
            name = f"{rec.model_id.model or ''} - {rec.encounter_type_id.encounter_name or ''} ({rec.form_type_id.form_name or ''})"
            result[rec.id] = name
        return result
    
    @api.constrains('model_id', 'form_type_id')
    def _check_model_match(self):
        for rec in self:
            if rec.form_type_id and rec.form_type_id.model_id != rec.model_id:
                raise models.ValidationError(_(
                    "Form Type (%s) must belong to the same model (%s)."
                ) % (rec.form_type_id.form_name, rec.model_id.model))
            
    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.model_id:
            return {
                'domain': {
                    'form_type_id': [('model_id', '=', self.model_id.id), ('active', '=', True)]
                }
            }
        else:
            return {
                'domain': {
                    'form_type_id': [('id', '=', False)] 
                }
            }