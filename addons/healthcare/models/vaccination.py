from odoo import models, fields, api
from datetime import timedelta

class MCHVaccination(models.Model):
    _name = 'mch.vaccination'
    _description = 'Vaccination Record'
    
    name = fields.Char(string='Vaccination Reference', readonly=True, default='New')
    patient_id = fields.Many2one('mch.patient', string='Patient', required=True)
    vaccine_id = fields.Many2one('product.product', string='Vaccine', required=True, domain=[('is_vaccine', '=', True)])
    date_administered = fields.Datetime(string='Date Administered', default=fields.Datetime.now)
    administered_by = fields.Many2one('mch.provider', string='Administered By', required=True)
    facility_id = fields.Many2one('mch.facility', string='Facility', required=True)
    lot_id = fields.Many2one('stock.production.lot', string='Batch/Lot')
    dose = fields.Float(string='Dose')
    route = fields.Selection([
        ('im', 'Intramuscular'),
        ('sc', 'Subcutaneous'),
        ('oral', 'Oral'),
        ('nasal', 'Nasal'),
        ('other', 'Other')
    ], string='Route of Administration')
    site = fields.Selection([
        ('left_arm', 'Left Arm'),
        ('right_arm', 'Right Arm'),
        ('left_thigh', 'Left Thigh'),
        ('right_thigh', 'Right Thigh'),
        ('other', 'Other')
    ], string='Site')
    notes = fields.Text(string='Notes')
    next_due_date = fields.Date(string='Next Dose Due Date', compute='_compute_next_due_date')
    fulfillment_id = fields.Many2one('mch.fulfillment', string='Related Fulfillment')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('mch.vaccination') or 'New'
        return super(MCHVaccination, self).create(vals)
    
    @api.depends('vaccine_id', 'date_administered')
    def _compute_next_due_date(self):
        for record in self:
            if not record.vaccine_id or not record.date_administered:
                record.next_due_date = False
                continue
            
            # Get vaccine schedule for this vaccine
            schedule = self.env['mch.vaccine.schedule'].search([
                ('vaccine_id', '=', record.vaccine_id.id),
                ('dose_number', '>', 1)
            ], order='dose_number')
            
            if schedule:
                # Calculate next due date based on interval
                next_dose_schedule = schedule[0]
                record.next_due_date = fields.Date.from_string(record.date_administered) + timedelta(days=next_dose_schedule.min_age_days)
            else:
                record.next_due_date = False

class MCHVaccineSchedule(models.Model):
    _name = 'mch.vaccine.schedule'
    _description = 'Vaccination Schedule'
    
    name = fields.Char(string='Schedule Name', required=True)
    vaccine_id = fields.Many2one('product.product', string='Vaccine', required=True, domain=[('is_vaccine', '=', True)])
    dose_number = fields.Integer(string='Dose Number', required=True)
    min_age_days = fields.Integer(string='Minimum Age (days)', required=True)
    max_age_days = fields.Integer(string='Maximum Age (days)')
    description = fields.Text(string='Description')
    
    _sql_constraints = [
        ('dose_number_unique', 'unique(vaccine_id, dose_number)', 'Dose number must be unique per vaccine!'),
    ]