from odoo import models, fields, api

class MCHTesting(models.Model):
    _name = 'mch.testing'
    _description = 'Medical Testing'
    
    name = fields.Char(string='Test Reference', readonly=True, default='New')
    consultation_id = fields.Many2one('mch.consultation', string='Consultation')
    patient_id = fields.Many2one('mch.patient', string='Patient', related='consultation_id.patient_id', store=True)
    test_type_id = fields.Many2one('mch.test.type', string='Test Type', required=True)
    date_ordered = fields.Datetime(string='Date Ordered', default=fields.Datetime.now)
    date_collected = fields.Datetime(string='Date Collected')
    date_received = fields.Datetime(string='Date Received')
    date_completed = fields.Datetime(string='Date Completed')
    collected_by = fields.Many2one('mch.provider', string='Collected By')
    performed_by = fields.Many2one('mch.provider', string='Performed By')
    notes = fields.Text(string='Notes')
    result = fields.Text(string='Result')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ordered', 'Ordered'),
        ('collected', 'Collected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('mch.testing') or 'New'
        return super(MCHTesting, self).create(vals)
    
    def action_order_test(self):
        self.write({'state': 'ordered'})
    
    def action_collect_sample(self):
        self.write({
            'state': 'collected',
            'date_collected': fields.Datetime.now()
        })
    
    def action_receive_sample(self):
        self.write({
            'state': 'in_progress',
            'date_received': fields.Datetime.now()
        })
    
    def action_complete_test(self):
        self.write({
            'state': 'completed',
            'date_completed': fields.Datetime.now()
        })
    
    def action_cancel_test(self):
        self.write({'state': 'canceled'})

class MCHTestType(models.Model):
    _name = 'mch.test.type'
    _description = 'Test Type'
    
    name = fields.Char(string='Test Name', required=True)
    code = fields.Char(string='Test Code')
    description = fields.Text(string='Description')
    sample_type = fields.Char(string='Sample Type')
    preparation = fields.Text(string='Patient Preparation')
    turnaround_time = fields.Integer(string='Turnaround Time (hours)')
    active = fields.Boolean(string='Active', default=True)