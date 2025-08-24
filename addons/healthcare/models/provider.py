import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError



class MCHProvider(models.Model):
    _name = 'mch.provider'
    _description = 'Healthcare Provider'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Provider Name', required=True)
    email = fields.Char(string='Email', required=True)
    partner_id = fields.Many2one('res.partner', string='Related Partner')
    license_number = fields.Char(string='License Number')
    provider_type = fields.Selection([
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('midwife', 'Midwife'),
        ('pharmacist', 'Pharmacist'),
        ('lab_tech', 'Lab Technician')
    ], string='Provider Type')
    specialty = fields.Char(string='Specialty')
    facility_id = fields.Many2one('mch.facility', string='Facilities', required=True)
    active = fields.Boolean(string='Active', default=True)
    user_id = fields.Many2one('res.users', string='Related User')
    consultation_ids = fields.One2many(
        'mch.consultation',
        'provider_id',
        string="Consultations"
    )

    _sql_constraints = [
        ('email_unique', 'unique(email)', 'Email must be unique'),
    ]

    @api.constrains('email')
    def _check_email(self):
        for provider in self:
            if provider.email and '@' not in provider.email:
                raise ValidationError("Please enter a valid email address")

    @api.model
    def create(self, vals):
        # Create related user if not exists
        if not vals.get('user_id'):
            # Safe reference to the group
            group_id = False
            try:
                provider_group = self.env.ref('maternal_child_health.group_mch_provider', raise_if_not_found=False)
                if provider_group:
                    group_id = provider_group.id
            except:
                pass
            
            # Generate a proper login/email
            provider_name = vals.get('name', 'provider').strip()
            if not provider_name:
                provider_name = 'provider'
                
            # Clean the name for email
            clean_name = re.sub(r'[^a-zA-Z0-9\.]', '.', provider_name).lower()
            clean_name = re.sub(r'\.+', '.', clean_name).strip('.')
            
            # Use provided email or generate one
            email = vals.get('email', '').strip()
            if not email or '@' not in email:
                email = f"{clean_name}@mch.example.com"
            
            # Ensure login is set and valid
            login = email  # Use email as login
            
            user_vals = {
                'name': provider_name,
                'login': login,
                'email': email,
            }
            
            # Only add group if it exists
            if group_id:
                user_vals['groups_id'] = [(4, group_id)]
            
            try:
                # Create the user first
                user = self.env['res.users'].create(user_vals)
                vals['user_id'] = user.id
                
                # Link the provider to the user after creation
                user.sudo().write({'provider_id': self.id})
            except Exception as e:
                raise UserError(f"Failed to create user: {str(e)}")

        return super(MCHProvider, self).create(vals)

    # @api.model
    # def create(self, vals):
    #     # Create related user if not exists
    #     if not vals.get('user_id'):
    #         # Safe reference to the group - won't crash if group doesn't exist
    #         group_id = False
    #         try:
    #             provider_group = self.env.ref('maternal_child_health.group_mch_provider', raise_if_not_found=False)
    #             if provider_group:
    #                 group_id = provider_group.id
    #         except:
    #             # Group doesn't exist yet, skip adding it
    #             pass
            
    #         # Use the email from vals or generate a default
    #         login_email = vals.get('email', f"{vals.get('name', 'provider').replace(' ', '.').lower()}@mch.example.com")
            
    #         user_vals = {
    #             'name': vals.get('name'),
    #             'login': login_email,
    #             'email': login_email,  # Also set email for the user
    #         }
            
    #         # Only add group if it exists
    #         if group_id:
    #             user_vals['groups_id'] = [(4, group_id)]
            
    #         user = self.env['res.users'].create(user_vals)
    #         vals['user_id'] = user.id
    #         user.sudo().write({'provider_id': self.id})

    #     return super(MCHProvider, self).create(vals)
    
    
class MCHFacility(models.Model):
    _name = 'mch.facility'
    _description = 'Healthcare Facility'

    name = fields.Char(string='Facility Name', required=True)
    code = fields.Char(string='Facility Code')
    address = fields.Text(string='Address')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    facility_type = fields.Selection([
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('pharmacy', 'Pharmacy'),
        ('lab', 'Laboratory')
    ], string='Facility Type')
    active = fields.Boolean(string='Active', default=True)
    provider_ids = fields.One2many(
        'mch.provider', 'facility_id', string='Providers')
