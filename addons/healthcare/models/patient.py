from odoo import models, fields, api

class MCHPatient(models.Model):
    _name = 'mch.patient'
    _description = 'Maternal and Child Health Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Patient Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Related Partner')
    date_of_birth = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age', compute='_compute_age')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender')
    state = fields.Char(string='State Of Origin', required=True)
    is_pregnant = fields.Boolean(string='Is Pregnant')
    pregnancy_week = fields.Integer(string='Pregnancy Week')
    blood_type = fields.Selection([
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')
    ], string='Blood Type')
    allergies = fields.Text(string='Allergies')
    medical_history = fields.Text(string='Medical History')
    facility_id = fields.Many2one('mch.facility', string='Primary Facility')
    active = fields.Boolean(string='Active', default=True)
    image = fields.Binary(string='Photo')
    
    # Child-specific fields
    is_child = fields.Boolean(string='Is Child')
    mother_id = fields.Many2one('mch.patient', string='Mother')
    birth_weight = fields.Float(string='Birth Weight (kg)')
    birth_height = fields.Float(string='Birth Height (cm)')
    
    # Vaccination fields
    vaccination_ids = fields.One2many('mch.vaccination', 'patient_id', string='Vaccinations')
    next_vaccination_date = fields.Date(string='Next Vaccination Due', compute='_compute_next_vaccination')
    
    consultation_ids = fields.One2many(
        'mch.consultation',  # related model
        'patient_id',        # inverse field in mch.consultation
        string='Consultations'
    )
    
    def action_open_consultations(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Consultations',
            'res_model': 'mch.consultation',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }

    def action_open_vaccinations(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vaccinations',
            'res_model': 'mch.vaccination',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }
    
    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                today = fields.Date.today()
                dob = record.date_of_birth
                record.age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            else:
                record.age = 0
    
    @api.depends('vaccination_ids', 'date_of_birth', 'is_child')
    def _compute_next_vaccination(self):
        for patient in self:
            if not patient.is_child:
                patient.next_vaccination_date = False
                continue
                
            # Get all scheduled vaccines for child's age
            schedule = self.env['mch.vaccine.schedule'].search([
                ('min_age_days', '<=', patient.age * 365),
                ('max_age_days', '>=', patient.age * 365),
            ])
            
            # Filter out already administered vaccines
            administered_vaccines = patient.vaccination_ids.mapped('vaccine_id')
            pending_schedule = schedule.filtered(lambda s: s.vaccine_id not in administered_vaccines)
            
            if pending_schedule:
                patient.next_vaccination_date = fields.Date.today()
            else:
                patient.next_vaccination_date = False