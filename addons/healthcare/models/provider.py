from odoo import models, fields, api


class MCHProvider(models.Model):
    _name = 'mch.provider'
    _description = 'Healthcare Provider'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Provider Name', required=True)
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
    facility_id = fields.Many2one('mch.facility', string='Facilities')
    active = fields.Boolean(string='Active', default=True)
    user_id = fields.Many2one('res.users', string='Related User')
    consultation_ids = fields.One2many(
        'mch.consultation',
        'provider_id',
        string="Consultations"
    )

    @api.model
    def create(self, vals):
        # Create related user if not exists
        if not vals.get('user_id'):
            user_vals = {
                'name': vals.get('name'),
                'login': vals.get('email', f"{vals.get('name').replace(' ', '.').lower()}@mch.example.com"),
                'groups_id': [(4, self.env.ref('maternal_child_health.group_mch_provider').id)],
            }
            user = self.env['res.users'].create(user_vals)
            vals['user_id'] = user.id

        return super(MCHProvider, self).create(vals)


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
