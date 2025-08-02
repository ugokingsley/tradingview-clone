from odoo import models, fields, api

class MCHFulfillment(models.Model):
    _name = 'mch.fulfillment'
    _description = 'Prescription Fulfillment'
    
    name = fields.Char(string='Fulfillment Reference', readonly=True, default='New')
    prescription_line_id = fields.Many2one('mch.prescription.line', string='Prescription Line', required=True)
    prescription_id = fields.Many2one('mch.prescription', string='Prescription', related='prescription_line_id.prescription_id', store=True)
    patient_id = fields.Many2one('mch.patient', string='Patient', related='prescription_id.patient_id', store=True)
    product_id = fields.Many2one('product.product', string='Product', related='prescription_line_id.product_id', store=True)
    is_vaccine = fields.Boolean(string='Is Vaccine', related='product_id.is_vaccine')
    quantity = fields.Float(string='Quantity', required=True)
    date_fulfilled = fields.Datetime(string='Date Fulfilled', default=fields.Datetime.now)
    fulfilled_by = fields.Many2one('mch.provider', string='Fulfilled By', required=True)
    facility_id = fields.Many2one('mch.facility', string='Facility', required=True)
    lot_id = fields.Many2one('stock.production.lot', string='Batch/Lot')
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('mch.fulfillment') or 'New'
        
        fulfillment = super(MCHFulfillment, self).create(vals)
        
        # Create vaccination record if this is a vaccine
        if fulfillment.is_vaccine:
            self.env['mch.vaccination'].create({
                'patient_id': fulfillment.patient_id.id,
                'vaccine_id': fulfillment.product_id.id,
                'date_administered': fulfillment.date_fulfilled,
                'administered_by': fulfillment.fulfilled_by.id,
                'facility_id': fulfillment.facility_id.id,
                'lot_id': fulfillment.lot_id.id,
                'fulfillment_id': fulfillment.id,
            })
        
        return fulfillment
    
    def action_confirm_fulfillment(self):
        self.write({'state': 'done'})
        
        # Update stock moves if needed
        if self.product_id.type == 'product':
            stock_move = self.env['stock.move'].create({
                'name': self.name,
                'product_id': self.product_id.id,
                'product_uom_qty': self.quantity,
                'product_uom': self.product_id.uom_id.id,
                'location_id': self.facility_id.location_id.id,
                'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                'state': 'done',
                'quantity_done': self.quantity,
                'lot_id': self.lot_id.id,
            })
            stock_move._action_done()
    
    def action_cancel_fulfillment(self):
        self.write({'state': 'canceled'})