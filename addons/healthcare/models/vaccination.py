from odoo import models, fields, api
from datetime import timedelta

class MCHVaccination(models.Model):
    _name = 'mch.vaccination'
    _description = 'Vaccination Record'
    
    name = fields.Char(string='Vaccination Reference', readonly=True, default='New')
    patient_id = fields.Many2one('mch.patient', string='Patient', required=True)
    vaccine_id = fields.Many2one('product.product', string='Vaccine', required=False, domain=[('is_vaccine', '=', True)])
    date_administered = fields.Datetime(string='Date Administered', default=fields.Datetime.now)
    administered_by = fields.Many2one('mch.provider', string='Administered By', required=True)
    facility_id = fields.Many2one('mch.facility', string='Facility', required=True)
    # lot_id = fields.Many2one('stock.production.lot', string='Batch/Lot')
    lot_id = fields.Char(string='Batch/Lot Number')
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
    campaign_id = fields.Many2one('mch.vaccination.campaign', string='Campaign')

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


class MCHVaccinationCampaign(models.Model):
    _name = 'mch.vaccination.campaign'
    _description = 'Vaccination Campaign'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Campaign Name', required=True, tracking=True)
    description = fields.Text(string='Description')
    vaccine_id = fields.Many2one(
        'product.product', 
        string='Target Vaccine', 
        domain=[('is_vaccine', '=', True)],
        required=True,
        tracking=True
    )
    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    target_population = fields.Integer(string='Target Population')
    facility_ids = fields.Many2many('mch.facility', string='Participating Facilities')
    provider_ids = fields.Many2many('mch.provider', string='Assigned Providers')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='ongoing', tracking=True)
    fulfillment_ids = fields.One2many(
        'mch.campaign.fulfillment', 
        'campaign_id', 
        string='Campaign Fulfillments'
    )

    vaccinated_count = fields.Integer(
        string='Vaccinated Count', 
        compute='_compute_vaccinated_count', 
        store=True
    )

    @api.depends('fulfillment_ids')
    def _compute_vaccinated_count(self):
        for rec in self:
            rec.vaccinated_count = len(rec.fulfillment_ids.filtered(lambda f: f.vaccination_id))

    def action_start(self):
        self.write({'state': 'ongoing'})

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class MCHCampaignFulfillment(models.Model):
    _name = 'mch.campaign.fulfillment'
    _description = 'Vaccination Campaign Fulfillment'

    campaign_id = fields.Many2one(
        'mch.vaccination.campaign', 
        string='Campaign', 
        required=True, 
        ondelete='cascade'
    )
    patient_id = fields.Many2one(
        'mch.patient', 
        string='Patient', 
        required=True
    )
    vaccination_id = fields.Many2one(
        'mch.vaccination', 
        string='Vaccination Record',
        help='Link to the actual vaccination event for traceability'
    )
    provider_id = fields.Many2one(
        'mch.provider', 
        string='Administered By', 
        required=True
    )
    facility_id = fields.Many2one(
        'mch.facility', 
        string='Facility', 
        required=True
    )
    date_administered = fields.Datetime(
        string='Date Administered', 
        default=fields.Datetime.now
    )
    status = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('vaccinated', 'Vaccinated'),
        ('missed', 'Missed'),
    ], default='scheduled', string='Status')

    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('status') == 'vaccinated' and not vals.get('vaccination_id'):
            campaign = self.env['mch.vaccination.campaign'].browse(vals.get('campaign_id'))
            vaccination = self.env['mch.vaccination'].create({
                'patient_id': vals.get('patient_id'),
                'vaccine_id': campaign.vaccine_id.id,
                'administered_by': vals.get('provider_id'),
                'facility_id': vals.get('facility_id'),
                'date_administered': vals.get('date_administered', fields.Datetime.now()),
                'lot_id': 'CAMPAIGN-' + str(campaign.id),
            })
            vals['vaccination_id'] = vaccination.id
        return super().create(vals)
