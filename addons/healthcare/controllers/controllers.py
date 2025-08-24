from odoo import http, fields, api
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from datetime import datetime, timedelta



import logging
_logger = logging.getLogger(__name__)



class MCHWebsiteController(http.Controller):

    @http.route('/mch-test', type='http', auth="public")
    def test_route(self, **kw):
        return "MCH Module is Working!"
    
    @http.route('/mch/provider/login', type='http', auth="public", website=True)
    def provider_login_page(self, **kw):
        """Custom login page for providers"""
        return request.render("healthcare.provider_login_template")

    @http.route('/mch', type='http', auth="public", website=True)
    def mch_homepage(self, **kw):
        _logger.info("MCH Homepage accessed")  # Debug line
        try:
            return request.render("healthcare.mch_homepage_template")
        except Exception as e:
            _logger.error("Template error: %s", str(e))
            raise

    @http.route('/mch/providers', type='http', auth="public", website=True)
    def provider_list(self, **kw):
        providers = request.env['mch.provider'].sudo().search([])
        return request.render("healthcare.provider_list_template", {
            'providers': providers,
        })

    @http.route('/mch/facilities', type='http', auth="public", website=True)
    def facility_list(self, **kw):
        facilities = request.env['mch.facility'].sudo().search([])
        return request.render("healthcare.facility_list_template", {
            'facilities': facilities,
        })


    @http.route('/mch/provider/signup', type='http', auth="public", website=True)
    def provider_signup(self, **post):
        if post.get('email'):
            # Ensure email is not None
            email = post.get('email', '').strip() if post.get('email') else ''
            provider_values = {
                'name': post.get('name', '').strip(),
                'email': email,
                'provider_type': post.get('provider_type', '').strip(),
                'license_number': post.get('license_number', '').strip(),
            }
            
            facility_id = post.get('facility_id')
            if facility_id and facility_id.isdigit():
                provider_values['facility_id'] = int(facility_id)
            
            provider = request.env['mch.provider'].sudo().create(provider_values)
            return request.redirect('/mch/provider/thank-you')
        
        facilities = request.env['mch.facility'].sudo().search([])
        return request.render("healthcare.provider_signup_template", {
            'facilities': facilities,
        })


    @http.route('/mch/provider/thank-you', type='http', auth="public", website=True)
    def provider_thank_you(self, **kw):
        return request.render("healthcare.provider_thank_you_template")
    

    @http.route('/mch/provider/dashboard', type='http', auth="user", website=True)
    def provider_dashboard(self, **kw):
        """Provider dashboard with statistics"""
        provider = request.env['mch.provider'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not provider:
            return request.redirect('/web/login?error=not_provider')
        
        # Get statistics
        patient_count = request.env['mch.patient'].sudo().search_count([
            ('facility_id', '=', provider.facility_id.id)
        ])
        
        today = fields.Date.today()
        vaccination_today_count = request.env['mch.vaccination'].sudo().search_count([
            ('facility_id', '=', provider.facility_id.id),
            ('date_administered', '>=', today),
            ('date_administered', '<', today + timedelta(days=1))
        ])
        
        pregnant_count = request.env['mch.patient'].sudo().search_count([
            ('facility_id', '=', provider.facility_id.id),
            ('is_pregnant', '=', True)
        ])
        
        child_count = request.env['mch.patient'].sudo().search_count([
            ('facility_id', '=', provider.facility_id.id),
            ('is_child', '=', True)
        ])
        
        # Get recent vaccinations
        recent_vaccinations = request.env['mch.vaccination'].sudo().search([
            ('facility_id', '=', provider.facility_id.id)
        ], order='date_administered desc', limit=5)
        
        return request.render("healthcare.provider_dashboard_template", {
            'provider': provider,
            'patient_count': patient_count,
            'vaccination_today_count': vaccination_today_count,
            'pregnant_count': pregnant_count,
            'child_count': child_count,
            'recent_vaccinations': recent_vaccinations,
        })

    @http.route('/mch/provider/register-patient', type='http', auth="user", website=True)
    def provider_register_patient(self, **post):
        """Patient registration form for providers"""
        provider = request.env['mch.provider'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not provider:
            return request.redirect('/web/login?error=not_provider')
        
        # Handle form submission
        if post.get('name'):
            try:
                patient_vals = {
                    'name': post.get('name'),
                    'date_of_birth': post.get('date_of_birth'),
                    'gender': post.get('gender'),
                    'blood_type': post.get('blood_type'),
                    'allergies': post.get('allergies'),
                    'medical_history': post.get('medical_history'),
                    'facility_id': provider.facility_id.id,
                    'is_child': post.get('is_child') == 'true',
                }
                
                # Handle pregnancy information
                if post.get('is_pregnant'):
                    patient_vals['is_pregnant'] = True
                    patient_vals['pregnancy_week'] = int(post.get('pregnancy_week', 0))
                
                # Handle child-specific fields
                if post.get('is_child') == 'true':
                    patient_vals['birth_weight'] = float(post.get('birth_weight', 0))
                    patient_vals['birth_height'] = float(post.get('birth_height', 0))
                    if post.get('mother_id'):
                        patient_vals['mother_id'] = int(post.get('mother_id'))
                
                # Create patient
                patient = request.env['mch.patient'].sudo().create(patient_vals)
                
                return request.redirect(f'/mch/provider/success?message=Patient {patient.name} registered successfully&next_action=register_patient')
                
            except Exception as e:
                _logger.error("Error creating patient: %s", str(e))
                return request.redirect('/mch/provider/register-patient?error=create_failed')
        
        # Get existing patients for mother selection
        existing_patients = request.env['mch.patient'].sudo().search([
            ('facility_id', '=', provider.facility_id.id)
        ])
        
        return request.render("healthcare.provider_patient_registration_template", {
            'provider': provider,
            'existing_patients': existing_patients,
        })

    @http.route('/mch/provider/vaccinate', type='http', auth="user", website=True)
    def provider_vaccinate(self, **post):
        """Vaccination administration form"""
        provider = request.env['mch.provider'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not provider:
            return request.redirect('/web/login?error=not_provider')
        
        # Handle form submission
        if post.get('patient_id') and post.get('vaccine_id'):
            try:
                vaccination_vals = {
                    'patient_id': int(post.get('patient_id')),
                    'vaccine_id': int(post.get('vaccine_id')),
                    'date_administered': post.get('date_administered'),
                    'administered_by': provider.id,
                    'facility_id': provider.facility_id.id,
                    'lot_id': post.get('lot_id'),
                    'dose': float(post.get('dose', 0)) if post.get('dose') else 0,
                    'route': post.get('route'),
                    'site': post.get('site'),
                    'notes': post.get('notes'),
                }
                
                # Create vaccination record
                vaccination = request.env['mch.vaccination'].sudo().create(vaccination_vals)
                
                return request.redirect(f'/mch/provider/success?message=Vaccination recorded for {vaccination.patient_id.name}&next_action=vaccinate')
                
            except Exception as e:
                _logger.error("Error recording vaccination: %s", str(e))
                return request.redirect('/mch/provider/vaccinate?error=create_failed')
        
        # Get patients from provider's facility
        patients = request.env['mch.patient'].sudo().search([
            ('facility_id', '=', provider.facility_id.id)
        ])
        
        # Get vaccines
        vaccines = request.env['product.product'].sudo().search([
            ('is_vaccine', '=', True)
        ])
        
        # Default datetime for form
        default_datetime = datetime.now().strftime('%Y-%m-%dT%H:%M')
        
        return request.render("healthcare.provider_vaccination_template", {
            'provider': provider,
            'patients': patients,
            'vaccines': vaccines,
            'default_datetime': default_datetime,
        })

    @http.route('/mch/provider/success', type='http', auth="user", website=True)
    def provider_success(self, **kw):
        """Success page after provider actions"""
        message = kw.get('message', 'Action completed successfully')
        next_action = kw.get('next_action', 'dashboard')
        
        next_actions = {
            'register_patient': {
                'url': '/mch/provider/register-patient',
                'label': 'Register Another Patient'
            },
            'vaccinate': {
                'url': '/mch/provider/vaccinate',
                'label': 'Record Another Vaccination'
            },
            'dashboard': {
                'url': '/mch/provider/dashboard',
                'label': 'Go to Dashboard'
            }
        }
        
        next_action_info = next_actions.get(next_action, next_actions['dashboard'])
        
        return request.render("healthcare.provider_success_template", {
            'message': message,
            'next_action_url': next_action_info['url'],
            'next_action_label': next_action_info['label'],
        })

    @http.route('/mch/provider/vaccinations', type='http', auth="user", website=True)
    def provider_vaccination_list(self, **kw):
        """List of vaccinations for the provider's facility"""
        provider = request.env['mch.provider'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not provider:
            return request.redirect('/web/login?error=not_provider')
        
        # Get vaccinations from provider's facility
        vaccinations = request.env['mch.vaccination'].sudo().search([
            ('facility_id', '=', provider.facility_id.id)
        ], order='date_administered desc')
        
        return request.render("healthcare.provider_vaccination_list_template", {
            'provider': provider,
            'vaccinations': vaccinations,
        })
        
    @http.route('/mch/provider/patients', type='http', auth="user", website=True)
    def provider_patient_list(self, **kw):
        """List of patients for the provider's facility"""
        provider = request.env['mch.provider'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not provider:
            return request.redirect('/web/login?error=not_provider')
        
        patients = request.env['mch.patient'].sudo().search([
            ('facility_id', '=', provider.facility_id.id)
        ])
        
        return request.render("healthcare.provider_patient_list_template", {
            'provider': provider,
            'patients': patients,
        })


class MCHProviderAuth(http.Controller):
    """Authentication and access control for providers"""
    
    @http.route('/mch/provider/check', type='http', auth="user")
    def check_provider_access(self, **kw):
        """Check if current user is a provider"""
        provider = request.env['mch.provider'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if provider:
            return "authorized"
        return "unauthorized"



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
        return request.render("healthcare.portal_my_mch", values)