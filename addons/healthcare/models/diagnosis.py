from odoo import models, fields, api

class MCHDiagnosis(models.Model):
    _name = 'mch.diagnosis'
    _description = 'Patient Diagnosis'
    
    name = fields.Char(string='Diagnosis Code')
    consultation_id = fields.Many2one('mch.consultation', string='Consultation')
    patient_id = fields.Many2one('mch.patient', string='Patient', related='consultation_id.patient_id', store=True)
    diagnosis_date = fields.Datetime(string='Date', default=fields.Datetime.now)
    icd_code = fields.Char(string='ICD Code')
    description = fields.Text(string='Description')
    notes = fields.Text(string='Clinical Notes')
    is_chronic = fields.Boolean(string='Chronic Condition')
    severity = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('critical', 'Critical')
    ], string='Severity')