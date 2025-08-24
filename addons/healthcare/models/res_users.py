from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    provider_id = fields.Many2one('mch.provider', string='Related Provider')
    facility_ids = fields.Many2many(
        'mch.facility',
        string='Facilities',
        help="Facilities this user has access to"
    )

    @api.model
    def _login_redirect(self, uid, redirect=None):
        """Override login redirect for providers"""
        user = self.browse(uid)
        
        # Check if user is a provider
        provider = self.env['mch.provider'].sudo().search([
            ('user_id', '=', user.id)
        ], limit=1)
        
        if provider:
            return '/mch/provider/dashboard'
        
        # Default behavior for other users
        return super()._login_redirect(uid, redirect)