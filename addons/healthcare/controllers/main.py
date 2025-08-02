from odoo import http
from odoo.http import request

class MCHWebsiteController(http.Controller):
    
    @http.route('/mch/providers/signup', type='http', auth="public", website=True)
    def provider_signup(self, **post):
        if post.get('signup_email'):
            # Handle provider signup
            provider_values = {
                'name': post.get('name'),
                'email': post.get('signup_email'),
                'provider_type': post.get('provider_type'),
                'license_number': post.get('license_number'),
            }
            
            facility_id = post.get('facility_id')
            if facility_id:
                provider_values['facility_ids'] = [(4, int(facility_id))]
            
            provider = request.env['mch.provider'].sudo().create(provider_values)
            
            return request.redirect('/web')
        
        facilities = request.env['mch.facility'].sudo().search([])
        return request.render('maternal_child_health.provider_signup_form', {
            'facilities': facilities,
        })
    
    @http.route('/mch/patient/portal', type='http', auth="user", website=True)
    def patient_portal(self, **kw):
        patient = request.env['mch.patient'].search([
            ('partner_id', '=', request.env.user.partner_id.id)
        ], limit=1)
        
        if not patient:
            return request.redirect('/')
            
        return request.render('maternal_child_health.patient_portal', {
            'patient': patient,
            'vaccinations': patient.vaccination_ids.sorted(key=lambda r: r.date_administered, reverse=True),
            'consultations': patient.consultation_ids.sorted(key=lambda r: r.date, reverse=True),
        })