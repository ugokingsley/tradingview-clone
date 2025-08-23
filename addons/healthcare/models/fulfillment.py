# from odoo import models, fields, api

# class MCHFulfillment(models.Model):
#     _name = 'mch.fulfillment'
#     _description = 'Prescription Fulfillment'
    
#     name = fields.Char(string='Fulfillment Reference', readonly=True, default='New')
#     prescription_line_id = fields.Many2one('mch.prescription.line', string='Prescription Line', required=True)
#     prescription_id = fields.Many2one('mch.prescription', string='Prescription', related='prescription_line_id.prescription_id', store=True)
#     patient_id = fields.Many2one('mch.patient', string='Patient', related='prescription_id.patient_id', store=True)
#     product_id = fields.Many2one('product.product', string='Product', related='prescription_line_id.product_id', store=True)
#     is_vaccine = fields.Boolean(string='Is Vaccine', related='product_id.is_vaccine')
#     quantity = fields.Float(string='Quantity', required=True)
#     date_fulfilled = fields.Datetime(string='Date Fulfilled', default=fields.Datetime.now)
#     fulfilled_by = fields.Many2one('mch.provider', string='Fulfilled By', required=True)
#     facility_id = fields.Many2one('mch.facility', string='Facility', required=True)
#     lot_id = fields.Many2one('stock.production.lot', string='Batch/Lot')
#     notes = fields.Text(string='Notes')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('done', 'Done'),
#         ('canceled', 'Canceled')
#     ], string='Status', default='draft')
    
#     @api.model
#     def create(self, vals):
#         if vals.get('name', 'New') == 'New':
#             vals['name'] = self.env['ir.sequence'].next_by_code('mch.fulfillment') or 'New'
        
#         fulfillment = super(MCHFulfillment, self).create(vals)
        
#         # Create vaccination record if this is a vaccine
#         if fulfillment.is_vaccine:
#             self.env['mch.vaccination'].create({
#                 'patient_id': fulfillment.patient_id.id,
#                 'vaccine_id': fulfillment.product_id.id,
#                 'date_administered': fulfillment.date_fulfilled,
#                 'administered_by': fulfillment.fulfilled_by.id,
#                 'facility_id': fulfillment.facility_id.id,
#                 'lot_id': fulfillment.lot_id.id,
#                 'fulfillment_id': fulfillment.id,
#             })
        
#         return fulfillment
    
#     def action_confirm_fulfillment(self):
#         self.write({'state': 'done'})
        
#         # Update stock moves if needed
#         if self.product_id.type == 'product':
#             stock_move = self.env['stock.move'].create({
#                 'name': self.name,
#                 'product_id': self.product_id.id,
#                 'product_uom_qty': self.quantity,
#                 'product_uom': self.product_id.uom_id.id,
#                 'location_id': self.facility_id.location_id.id,
#                 'location_dest_id': self.env.ref('stock.stock_location_customers').id,
#                 'state': 'done',
#                 'quantity_done': self.quantity,
#                 'lot_id': self.lot_id.id,
#             })
#             stock_move._action_done()
    
#     def action_cancel_fulfillment(self):
#         self.write({'state': 'canceled'})

# from odoo import models, fields, api, _
# from odoo.exceptions import ValidationError

# class MCHFulfillment(models.Model):
#     _name = 'mch.fulfillment'
#     _description = 'Prescription Fulfillment'
    
#     name = fields.Char(string='Fulfillment Reference', readonly=True, default='New')
#     prescription_line_id = fields.Many2one('mch.prescription.line', string='Prescription Line', required=False)
#     # prescription_id = fields.Many2one('mch.prescription', string='Prescription', related='prescription_line_id.prescription_id', store=False)
#     # patient_id = fields.Many2one('mch.patient', string='Patient', related='prescription_id.patient_id', store=False)
#     # product_id = fields.Many2one('product.product', string='Product', related='prescription_line_id.product_id', store=False)
#     # is_vaccine = fields.Boolean(string='Is Vaccine', related='product_id.is_vaccine', store=False)
#     prescription_id = fields.Many2one('mch.prescription', string='Prescription', compute='_compute_related_info', store=False)
#     patient_id = fields.Many2one('mch.patient', string='Patient', compute='_compute_related_info', store=False)
#     product_id = fields.Many2one('product.product', string='Product', compute='_compute_related_info', store=False)
#     is_vaccine = fields.Boolean(string='Is Vaccine', compute='_compute_related_info', store=False)

#     quantity = fields.Float(string='Quantity', required=True)
#     date_fulfilled = fields.Datetime(string='Date Fulfilled', default=fields.Datetime.now)
#     fulfilled_by = fields.Many2one('mch.provider', string='Fulfilled By', required=True)
#     facility_id = fields.Many2one('mch.facility', string='Facility', required=True)
#     lot_id = fields.Many2one('stock.production.lot', string='Batch/Lot')
#     notes = fields.Text(string='Notes')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('done', 'Done'),
#         ('canceled', 'Canceled')
#     ], string='Status', default='draft')

#     @api.depends('prescription_line_id')
#     def _compute_related_info(self):
#         for record in self:
#             # Handle None values gracefully to avoid serialization issues
#             if record.prescription_line_id and record.prescription_line_id.prescription_id:
#                 record.prescription_id = record.prescription_line_id.prescription_id
#                 record.patient_id = record.prescription_line_id.prescription_id.patient_id
#                 record.product_id = record.prescription_line_id.product_id
#                 record.is_vaccine = record.prescription_line_id.product_id.is_vaccine if record.prescription_line_id.product_id else False
#             else:
#                 record.prescription_id = False
#                 record.patient_id = False
#                 record.product_id = False
#                 record.is_vaccine = False
    
#     @api.constrains('is_vaccine', 'lot_id')
#     def _check_vaccine_lot_required(self):
#         """Ensure lot is provided for vaccines"""
#         for record in self:
#             if record.is_vaccine and not record.lot_id:
#                 raise ValidationError(_("Batch/Lot is required for vaccines."))
    
#     @api.onchange('prescription_line_id')
#     def _onchange_prescription_line_id(self):
#         """Update related fields when prescription line changes"""
#         if self.prescription_line_id:
#             self.product_id = self.prescription_line_id.product_id.id
#             self.quantity = self.prescription_line_id.quantity
    

#     # @api.onchange('product_id')
#     # def _onchange_product_id(self):
#     #     """Update domain for lot_id when product changes"""
#     #     self.lot_id = False
#     #     domain = {}
#     #     if self.product_id:
#     #         domain = {'lot_id': [('product_id', '=', self.product_id.id)]}
#     #     return {'domain': domain}

#     @api.onchange('prescription_line_id')
#     def _onchange_prescription_line_id(self):
#         """Update quantity when prescription line changes"""
#         if self.prescription_line_id:
#             self.quantity = self.prescription_line_id.quantity
#         else:
#             self.quantity = 0.0
    
#     @api.model
#     def create(self, vals):
#         if vals.get('name', 'New') == 'New':
#             vals['name'] = self.env['ir.sequence'].next_by_code('mch.fulfillment') or 'New'
        
#         # Check if lot is required for vaccine
#         if vals.get('is_vaccine') and not vals.get('lot_id'):
#             raise ValidationError(_("Batch/Lot is required for vaccines."))
        
#         fulfillment = super(MCHFulfillment, self).create(vals)
        
#         # Create vaccination record if this is a vaccine
#         if fulfillment.is_vaccine and fulfillment.lot_id:
#             self.env['mch.vaccination'].create({
#                 'patient_id': fulfillment.patient_id.id,
#                 'vaccine_id': fulfillment.product_id.id,
#                 'date_administered': fulfillment.date_fulfilled,
#                 'administered_by': fulfillment.fulfilled_by.id,
#                 'facility_id': fulfillment.facility_id.id,
#                 'lot_id': fulfillment.lot_id.id,
#                 'fulfillment_id': fulfillment.id,
#             })
        
#         return fulfillment
    
#     def write(self, vals):
#         """Handle validation when updating records"""
#         if 'is_vaccine' in vals or 'lot_id' in vals:
#             for record in self:
#                 is_vaccine = vals.get('is_vaccine', record.is_vaccine)
#                 lot_id = vals.get('lot_id', record.lot_id.id if record.lot_id else False)
#                 if is_vaccine and not lot_id:
#                     raise ValidationError(_("Batch/Lot is required for vaccines."))
#         return super().write(vals)
    
#     def action_confirm_fulfillment(self):
#         for record in self:
#             # Additional validation before confirming
#             if record.is_vaccine and not record.lot_id:
#                 raise ValidationError(_("Cannot confirm vaccine fulfillment without a Batch/Lot."))
            
#             record.write({'state': 'done'})
            
#             # Update stock moves if needed
#             if record.product_id.type == 'product':
#                 # Get the source location from facility or use default
#                 location_id = record.facility_id.location_id.id if record.facility_id.location_id else self.env.ref('stock.stock_location_stock').id
                
#                 stock_move = self.env['stock.move'].create({
#                     'name': record.name,
#                     'product_id': record.product_id.id,
#                     'product_uom_qty': record.quantity,
#                     'product_uom': record.product_id.uom_id.id,
#                     'location_id': location_id,
#                     'location_dest_id': self.env.ref('stock.stock_location_customers').id,
#                     'state': 'done',
#                     'quantity_done': record.quantity,
#                     'lot_id': record.lot_id.id if record.lot_id else False,
#                 })
#                 stock_move._action_done()
    
#     def action_cancel_fulfillment(self):
#         self.write({'state': 'canceled'})


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MCHFulfillment(models.Model):
    _name = 'mch.fulfillment'
    _description = 'Prescription Fulfillment'
    
    name = fields.Char(string='Fulfillment Reference', readonly=True, default='New')
    prescription_line_id = fields.Many2one('mch.prescription.line', string='Prescription Line', required=False)
    prescription_id = fields.Many2one('mch.prescription', string='Prescription', store=False)
    patient_id = fields.Many2one('mch.patient', string='Patient')
    product_id = fields.Many2one('product.product', string='Product')
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
    
    @api.onchange('prescription_line_id')
    def _onchange_prescription_line_id(self):
        """Update related fields when prescription line changes"""
        if self.prescription_line_id:
            self.product_id = self.prescription_line_id.product_id.id
            self.quantity = self.prescription_line_id.quantity
            self.patient_id = self.prescription_line_id.prescription_id.patient_id.id
        else:
            self.product_id = False
            self.quantity = 0.0
            self.patient_id = False
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Update domain for lot_id when product changes"""
        self.lot_id = False
        domain = {}
        if self.product_id:
            domain = {'lot_id': [('product_id', '=', self.product_id.id)]}
        return {'domain': domain}
    
    def _check_vaccine_requirements(self):
        """Check if vaccine requirements are met"""
        for record in self:
            if record.product_id and record.product_id.is_vaccine and not record.lot_id:
                raise ValidationError(_("Batch/Lot is required for vaccines."))
    
    @api.constrains('product_id', 'lot_id')
    def _check_vaccine_lot_required(self):
        """Ensure lot is provided for vaccines"""
        self._check_vaccine_requirements()
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('mch.fulfillment') or 'New'
        
        # Check if lot is required for vaccine
        product_id = vals.get('product_id')
        if product_id:
            product = self.env['product.product'].browse(product_id)
            if product.is_vaccine and not vals.get('lot_id'):
                raise ValidationError(_("Batch/Lot is required for vaccines."))
        
        fulfillment = super(MCHFulfillment, self).create(vals)
        
        # Create vaccination record if this is a vaccine
        if fulfillment.product_id.is_vaccine and fulfillment.lot_id:
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
    
    def write(self, vals):
        """Handle validation when updating records"""
        if 'product_id' in vals or 'lot_id' in vals:
            for record in self:
                product_id = vals.get('product_id', record.product_id.id if record.product_id else False)
                lot_id = vals.get('lot_id', record.lot_id.id if record.lot_id else False)
                
                if product_id:
                    product = self.env['product.product'].browse(product_id)
                    if product.is_vaccine and not lot_id:
                        raise ValidationError(_("Batch/Lot is required for vaccines."))
        return super().write(vals)
    
    def action_confirm_fulfillment(self):
        """Confirm fulfillment with validation"""
        self._check_vaccine_requirements()
        
        for record in self:
            record.write({'state': 'done'})
            
            # Update stock moves if needed
            if record.product_id.type == 'product':
                # Get the source location from facility or use default
                location_id = record.facility_id.location_id.id if record.facility_id.location_id else self.env.ref('stock.stock_location_stock').id
                
                stock_move = self.env['stock.move'].create({
                    'name': record.name,
                    'product_id': record.product_id.id,
                    'product_uom_qty': record.quantity,
                    'product_uom': record.product_id.uom_id.id,
                    'location_id': location_id,
                    'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                    'state': 'done',
                    'quantity_done': record.quantity,
                    'lot_id': record.lot_id.id if record.lot_id else False,
                })
                stock_move._action_done()
    
    def action_cancel_fulfillment(self):
        self.write({'state': 'canceled'})