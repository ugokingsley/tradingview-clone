from odoo import models, fields, api

class MCHPrescription(models.Model):
    _name = 'mch.prescription'
    _description = 'Medical Prescription'
    
    name = fields.Char(string='Prescription Reference', readonly=True, default='New')
    consultation_id = fields.Many2one('mch.consultation', string='Consultation')
    patient_id = fields.Many2one('mch.patient', string='Patient', related='consultation_id.patient_id', store=True)
    provider_id = fields.Many2one('mch.provider', string='Prescribing Provider', required=True)
    date_prescribed = fields.Datetime(string='Date Prescribed', default=fields.Datetime.now)
    prescription_line_ids = fields.One2many('mch.prescription.line', 'prescription_id', string='Prescription Lines')
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft')
    type = fields.Selection([('drug', 'Drug'), ('vaccine', 'Vaccine')], default='drug')
    fulfillment_ids = fields.One2many(
        comodel_name="mch.fulfillment",
        inverse_name="prescription_id",
        string="Fulfillments"
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('mch.prescription') or 'New'
        return super(MCHPrescription, self).create(vals)
    
    def action_confirm_prescription(self):
        self.write({'state': 'active'})
    
    def action_complete_prescription(self):
        self.write({'state': 'completed'})
    
    def action_cancel_prescription(self):
        self.write({'state': 'canceled'})

class MCHPrescriptionLine(models.Model):
    _name = 'mch.prescription.line'
    _description = 'Prescription Line'
    
    prescription_id = fields.Many2one('mch.prescription', string='Prescription')
    product_id = fields.Many2one('product.product', string='Medication/Vaccine', required=True)
    is_vaccine = fields.Boolean(string='Is Vaccine', related='product_id.is_vaccine')
    dose = fields.Float(string='Dose')
    dose_uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    route = fields.Selection([
        ('oral', 'Oral'),
        ('iv', 'Intravenous'),
        ('im', 'Intramuscular'),
        ('sc', 'Subcutaneous'),
        ('topical', 'Topical'),
        ('other', 'Other')
    ], string='Route of Administration')
    frequency = fields.Char(string='Frequency')
    duration = fields.Integer(string='Duration (days)')
    quantity = fields.Float(string='Quantity', required=True)
    refills = fields.Integer(string='Refills')
    notes = fields.Text(string='Notes')
    fulfillment_ids = fields.One2many('mch.fulfillment', 'prescription_line_id', string='Fulfillments')
    fulfilled_qty = fields.Float(string='Fulfilled Quantity', compute='_compute_fulfilled_qty')
    remaining_qty = fields.Float(string='Remaining Quantity', compute='_compute_remaining_qty')
    
    @api.depends('fulfillment_ids', 'fulfillment_ids.quantity')
    def _compute_fulfilled_qty(self):
        for line in self:
            line.fulfilled_qty = sum(line.fulfillment_ids.mapped('quantity'))
    
    @api.depends('quantity', 'fulfilled_qty')
    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = line.quantity - line.fulfilled_qty