from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    provider_id = fields.Many2one('mch.provider', string='Related Provider')
    facility_ids = fields.Many2many(
        'mch.facility',
        string='Facilities',
        help="Facilities this user has access to"
    )