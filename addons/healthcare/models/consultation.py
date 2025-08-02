from odoo import models, fields, api

class MCHConsultation(models.Model):
    _name = 'mch.consultation'
    _description = 'Patient Consultation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Consultation Reference', readonly=True, default='New')
    patient_id = fields.Many2one('mch.patient', string='Patient', required=True)
    provider_id = fields.Many2one('mch.provider', string='Provider', required=True)
    facility_id = fields.Many2one('mch.facility', string='Facility', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    reason = fields.Text(string='Reason for Visit')
    notes = fields.Text(string='Clinical Notes')
    height = fields.Float(string='Height (cm)')
    weight = fields.Float(string='Weight (kg)')
    temperature = fields.Float(string='Temperature (°C)')
    blood_pressure = fields.Char(string='Blood Pressure')
    pulse = fields.Integer(string='Pulse (bpm)')
    respiratory_rate = fields.Integer(string='Respiratory Rate')
    bmi = fields.Float(string='BMI', compute='_compute_bmi')
    diagnosis_ids = fields.One2many('mch.diagnosis', 'consultation_id', string='Diagnoses')
    test_ids = fields.One2many('mch.testing', 'consultation_id', string='Tests')
    prescription_ids = fields.One2many('mch.prescription', 'consultation_id', string='Prescriptions')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft')
    
    @api.depends('height', 'weight')
    def _compute_bmi(self):
        for record in self:
            if record.height and record.weight:
                record.bmi = record.weight / ((record.height / 100) ** 2)
            else:
                record.bmi = 0.0
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('mch.consultation') or 'New'
        return super(MCHConsultation, self).create(vals)
    
    def action_start_consultation(self):
        self.write({'state': 'in_progress'})
    
    def action_complete_consultation(self):
        self.write({'state': 'completed'})
    
    def action_cancel_consultation(self):
        self.write({'state': 'canceled'})