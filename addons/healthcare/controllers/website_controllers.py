from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

import logging
_logger = logging.getLogger(__name__)

class MCHWebsiteController(http.Controller):

    @http.route('/mch-test', type='http', auth="public")
    def test_route(self, **kw):
        return "MCH Module is Working!"

    @http.route('/mch', type='http', auth="public", website=True)
    def mch_homepage(self, **kw):
        _logger.info("MCH Homepage accessed")  # Debug line
        try:
            return request.render("maternal_child_health.mch_homepage_template")
        except Exception as e:
            _logger.error("Template error: %s", str(e))
            raise

    # @http.route('/mch', type='http', auth="public", website=True)
    # def mch_homepage(self, **kw):
    #     return request.render("maternal_child_health.mch_homepage_template")

    @http.route('/mch/providers', type='http', auth="public", website=True)
    def provider_list(self, **kw):
        providers = request.env['mch.provider'].sudo().search([])
        return request.render("maternal_child_health.provider_list_template", {
            'providers': providers,
        })

    @http.route('/mch/facilities', type='http', auth="public", website=True)
    def facility_list(self, **kw):
        facilities = request.env['mch.facility'].sudo().search([])
        return request.render("maternal_child_health.facility_list_template", {
            'facilities': facilities,
        })

    @http.route('/mch/provider/signup', type='http', auth="public", website=True)
    def provider_signup(self, **post):
        if post.get('signup_email'):
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
            return request.redirect('/mch/provider/thank-you')
        
        facilities = request.env['mch.facility'].sudo().search([])
        return request.render("maternal_child_health.provider_signup_template", {
            'facilities': facilities,
        })

    @http.route('/mch/provider/thank-you', type='http', auth="public", website=True)
    def provider_thank_you(self, **kw):
        return request.render("maternal_child_health.provider_thank_you_template")

class MCHPatientPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'consultation_count' in counters:
            patient = request.env['mch.patient'].sudo().search(
                [('partner_id', '=', request.env.user.partner_id.id)], limit=1)
            if patient:
                values['consultation_count'] = len(patient.consultation_ids)
        return values

    @http.route(['/my/mch', '/my/mch/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_mch(self, page=1, **kw):
        patient = request.env['mch.patient'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        
        if not patient:
            return request.redirect('/my')
            
        # Pager for consultations
        consultations = patient.consultation_ids.sorted('date', reverse=True)
        pager = request.website.pager(
            url="/my/mch",
            total=len(consultations),
            page=page,
            step=10
        )
        consultations = consultations[(page-1)*10 : page*10]
        
        values = {
            'patient': patient,
            'consultations': consultations,
            'pager': pager,
        }
        return request.render("maternal_child_health.portal_my_mch", values)