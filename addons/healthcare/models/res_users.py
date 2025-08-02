from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    facility_ids = fields.Many2many('mch.facility', string='Facilities')
