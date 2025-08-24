import json
import secrets
from datetime import datetime, timedelta
from odoo import http, fields
from odoo.http import request, Response
import logging

_logger = logging.getLogger(__name__)

class MCHAPIController(http.Controller):

    @http.route('/api/mch/provider/login', type='json', auth="none", methods=['POST'], csrf=False)
    def api_provider_login(self, **post):
        """Provider login API with token authentication"""
        try:
            email = post.get('email')
            password = post.get('password')
            
            if not email or not password:
                return {'status': 'error', 'message': 'Email and password are required'}
            
            # Authenticate user using Odoo's authentication
            try:
                uid = request.session.authenticate(request.db, email, password)
            except Exception as auth_error:
                return {'status': 'error', 'message': 'Invalid credentials'}
            
            if uid:
                # Check if user is a provider
                provider = request.env['mch.provider'].sudo().search([
                    ('user_id', '=', uid)
                ], limit=1)
                
                if provider:
                    # Generate authentication token
                    token = secrets.token_urlsafe(32)
                    expiration_date = datetime.now() + timedelta(days=30)  # 30 days expiration
                    
                    # Store token in provider record
                    provider.sudo().write({
                        'auth_token': token,
                        'token_expiration': expiration_date,
                        'last_login': fields.Datetime.now()
                    })
                    
                    return {
                        'status': 'success',
                        'message': 'Login successful',
                        'data': {
                            'token': token,
                            'expires_at': expiration_date.isoformat(),
                            'user': {
                                'user_id': uid,
                                'provider_id': provider.id,
                                'name': provider.name,
                                'email': provider.email,
                                'facility_id': provider.facility_id.id if provider.facility_id else None,
                                'facility_name': provider.facility_id.name if provider.facility_id else None
                            }
                        }
                    }
                else:
                    return {'status': 'error', 'message': 'User is not a registered provider'}
            else:
                return {'status': 'error', 'message': 'Invalid credentials'}
                
        except Exception as e:
            _logger.error("Login API Error: %s", str(e))
            return {'status': 'error', 'message': 'Internal server error'}

    @http.route('/api/mch/provider/logout', type='json', auth="none", methods=['POST'], csrf=False)
    def api_provider_logout(self, **post):
        """Provider logout API"""
        try:
            token = post.get('token')
            if not token:
                return {'status': 'error', 'message': 'Token is required'}
            
            # Find provider by token and invalidate it
            provider = request.env['mch.provider'].sudo().search([
                ('auth_token', '=', token)
            ], limit=1)
            
            if provider:
                provider.sudo().write({
                    'auth_token': False,
                    'token_expiration': False
                })
                return {'status': 'success', 'message': 'Logout successful'}
            else:
                return {'status': 'error', 'message': 'Invalid token'}
                
        except Exception as e:
            _logger.error("Logout API Error: %s", str(e))
            return {'status': 'error', 'message': 'Internal server error'}

    # Helper method to validate token
    def _validate_token(self, token):
        """Validate authentication token"""
        if not token:
            return None
        
        provider = request.env['mch.provider'].sudo().search([
            ('auth_token', '=', token),
            ('token_expiration', '>', fields.Datetime.now())
        ], limit=1)
        
        return provider

    # Decorator for token-protected endpoints
    def token_required(func):
        """Decorator to require valid token for API endpoints"""
        def wrapper(self, **kwargs):
            try:
                # Get token from request headers or POST data
                token = request.httprequest.headers.get('Authorization') or kwargs.get('token')
                if token and token.startswith('Bearer '):
                    token = token[7:]  # Remove 'Bearer ' prefix
                
                provider = self._validate_token(token)
                if not provider:
                    return {'status': 'error', 'message': 'Invalid or expired token'}
                
                # Set the authenticated user in environment
                request.uid = provider.user_id.id
                request.env = request.env(user=provider.user_id.id)
                
                # Add provider to kwargs for use in the method
                kwargs['provider'] = provider
                return func(self, **kwargs)
                
            except Exception as e:
                _logger.error("Token validation error: %s", str(e))
                return {'status': 'error', 'message': 'Authentication failed'}
        return wrapper

    @http.route('/api/mch/test', type='http', auth="public", methods=['GET'], csrf=False)
    def api_test(self, **kw):
        """Test API endpoint"""
        return Response(
            json.dumps({'status': 'success', 'message': 'MCH API is working!'}),
            content_type='application/json'
        )

    # @http.route('/api/mch/providers', type='http', auth="public", methods=['GET'], csrf=False)
    # def api_provider_list(self, **kw):
    #     """Get list of providers (API)"""
    #     try:
    #         providers = request.env['mch.provider'].sudo().search([])
    #         provider_data = []
            
    #         for provider in providers:
    #             provider_data.append({
    #                 'id': provider.id,
    #                 'name': provider.name,
    #                 'email': provider.email,
    #                 'provider_type': provider.provider_type,
    #                 'license_number': provider.license_number,
    #                 'facility_id': provider.facility_id.id if provider.facility_id else None,
    #                 'facility_name': provider.facility_id.name if provider.facility_id else None
    #             })
            
    #         return Response(
    #             json.dumps({'status': 'success', 'data': provider_data}),
    #             content_type='application/json'
    #         )
    #     except Exception as e:
    #         _logger.error("API Error: %s", str(e))
    #         return Response(
    #             json.dumps({'status': 'error', 'message': str(e)}),
    #             content_type='application/json',
    #             status=500
    #         )

    # @http.route('/api/mch/facilities', type='http', auth="public", methods=['GET'], csrf=False)
    # def api_facility_list(self, **kw):
    #     """Get list of facilities (API)"""
    #     try:
    #         facilities = request.env['mch.facility'].sudo().search([])
    #         facility_data = []
            
    #         for facility in facilities:
    #             facility_data.append({
    #                 'id': facility.id,
    #                 'name': facility.name,
    #                 'address': facility.address,
    #                 'phone': facility.phone,
    #                 'email': facility.email,
    #                 'facility_type': facility.facility_type
    #             })
            
    #         return Response(
    #             json.dumps({'status': 'success', 'data': facility_data}),
    #             content_type='application/json'
    #         )
    #     except Exception as e:
    #         _logger.error("API Error: %s", str(e))
    #         return Response(
    #             json.dumps({'status': 'error', 'message': str(e)}),
    #             content_type='application/json',
    #             status=500
    #         )
            
    @http.route('/api/mch/provider/dashboard', type='json', auth="none", methods=['POST'], csrf=False)
    @token_required
    def api_provider_dashboard(self, **kwargs):
        """Provider dashboard data API with token authentication"""
        try:
            provider = kwargs.get('provider')
            
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
            
            vaccination_data = []
            for vac in recent_vaccinations:
                vaccination_data.append({
                    'id': vac.id,
                    'patient_name': vac.patient_id.name,
                    'vaccine_name': vac.vaccine_id.name,
                    'date_administered': vac.date_administered.strftime('%Y-%m-%d %H:%M') if vac.date_administered else None,
                    'dose': vac.dose
                })
            
            return {
                'status': 'success',
                'data': {
                    'provider': {
                        'id': provider.id,
                        'name': provider.name,
                        'facility_id': provider.facility_id.id,
                        'facility_name': provider.facility_id.name
                    },
                    'stats': {
                        'patient_count': patient_count,
                        'vaccination_today_count': vaccination_today_count,
                        'pregnant_count': pregnant_count,
                        'child_count': child_count
                    },
                    'recent_vaccinations': vaccination_data
                }
            }
            
        except Exception as e:
            _logger.error("Dashboard API Error: %s", str(e))
            return {'status': 'error', 'message': str(e)}
        

    # Protected endpoints (token required)
    @http.route('/api/mch/providers', type='http', auth="none", methods=['GET'], csrf=False)
    @token_required
    def api_provider_list(self, **kw):
        """Get list of providers (API) - Token required"""
        try:
            provider = kw.get('provider')
            
            # Only show providers from the same facility if not admin
            domain = []
            if not request.env.user.has_group('base.group_system'):
                domain = [('facility_id', '=', provider.facility_id.id)]
            
            providers = request.env['mch.provider'].sudo().search(domain)
            provider_data = []
            
            for prov in providers:
                provider_data.append({
                    'id': prov.id,
                    'name': prov.name,
                    'email': prov.email,
                    'provider_type': prov.provider_type,
                    'license_number': prov.license_number,
                    'facility_id': prov.facility_id.id if prov.facility_id else None,
                    'facility_name': prov.facility_id.name if prov.facility_id else None,
                    'is_current_user': prov.id == provider.id
                })
            
            return Response(
                json.dumps({'status': 'success', 'data': provider_data}),
                content_type='application/json'
            )
        except Exception as e:
            _logger.error("API Error: %s", str(e))
            return Response(
                json.dumps({'status': 'error', 'message': str(e)}),
                content_type='application/json',
                status=500
            )

    @http.route('/api/mch/facilities', type='http', auth="none", methods=['GET'], csrf=False)
    @token_required
    def api_facility_list(self, **kw):
        """Get list of facilities (API) - Token required"""
        try:
            provider = kw.get('provider')
            
            # For regular providers, only show their facility
            # For admin users, show all facilities
            domain = []
            if not request.env.user.has_group('base.group_system'):
                domain = [('id', '=', provider.facility_id.id)]
            
            facilities = request.env['mch.facility'].sudo().search(domain)
            facility_data = []
            
            for facility in facilities:
                facility_data.append({
                    'id': facility.id,
                    'name': facility.name,
                    'address': facility.address,
                    'phone': facility.phone,
                    'email': facility.email,
                    'facility_type': facility.facility_type,
                    'is_current_facility': facility.id == provider.facility_id.id
                })
            
            return Response(
                json.dumps({'status': 'success', 'data': facility_data}),
                content_type='application/json'
            )
        except Exception as e:
            _logger.error("API Error: %s", str(e))
            return Response(
                json.dumps({'status': 'error', 'message': str(e)}),
                content_type='application/json',
                status=500
            )

    # Add a public endpoint for facility list (if needed for signup)
    @http.route('/api/mch/public/facilities', type='http', auth="public", methods=['GET'], csrf=False)
    def api_public_facility_list(self, **kw):
        """Get public list of facilities for signup (No token required)"""
        try:
            facilities = request.env['mch.facility'].sudo().search([])
            facility_data = []
            
            for facility in facilities:
                facility_data.append({
                    'id': facility.id,
                    'name': facility.name,
                    'facility_type': facility.facility_type
                    # Don't expose sensitive information in public endpoint
                })
            
            return Response(
                json.dumps({'status': 'success', 'data': facility_data}),
                content_type='application/json'
            )
        except Exception as e:
            _logger.error("Public Facilities API Error: %s", str(e))
            return Response(
                json.dumps({'status': 'error', 'message': str(e)}),
                content_type='application/json',
                status=500
            )

    @http.route('/api/mch/provider/patients', type='json', auth="none", methods=['POST'], csrf=False)
    @token_required
    def api_patient_list(self, **kwargs):
        """Get patients list for provider's facility with token authentication"""
        try:
            provider = kwargs.get('provider')
            
            patients = request.env['mch.patient'].sudo().search([
                ('facility_id', '=', provider.facility_id.id)
            ])
            
            patient_data = []
            for patient in patients:
                patient_data.append({
                    'id': patient.id,
                    'name': patient.name,
                    'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d') if patient.date_of_birth else None,
                    'gender': patient.gender,
                    'blood_type': patient.blood_type,
                    'is_pregnant': patient.is_pregnant,
                    'is_child': patient.is_child,
                    'pregnancy_week': patient.pregnancy_week if patient.is_pregnant else None
                })
            
            return {
                'status': 'success',
                'data': patient_data
            }
            
        except Exception as e:
            _logger.error("Patient List API Error: %s", str(e))
            return {'status': 'error', 'message': str(e)}

    # Update other protected endpoints with @token_required decorator
    @http.route('/api/mch/provider/register-patient', type='json', auth="none", methods=['POST'], csrf=False)
    @token_required
    def api_register_patient(self, **kwargs):
        """Register new patient API with token authentication"""
        try:
            provider = kwargs.get('provider')
            post = kwargs
            
            # Validate required fields
            required_fields = ['name', 'date_of_birth', 'gender']
            for field in required_fields:
                if not post.get(field):
                    return {'status': 'error', 'message': f'{field} is required'}
            
            patient_vals = {
                'name': post.get('name'),
                'date_of_birth': post.get('date_of_birth'),
                'gender': post.get('gender'),
                'blood_type': post.get('blood_type'),
                'allergies': post.get('allergies'),
                'medical_history': post.get('medical_history'),
                'facility_id': provider.facility_id.id,
                'is_child': post.get('is_child', False),
            }
            
            # Handle pregnancy information
            if post.get('is_pregnant'):
                patient_vals['is_pregnant'] = True
                patient_vals['pregnancy_week'] = int(post.get('pregnancy_week', 0))
            
            # Handle child-specific fields
            if post.get('is_child'):
                patient_vals['birth_weight'] = float(post.get('birth_weight', 0))
                patient_vals['birth_height'] = float(post.get('birth_height', 0))
                if post.get('mother_id'):
                    patient_vals['mother_id'] = int(post.get('mother_id'))
            
            # Create patient
            patient = request.env['mch.patient'].sudo().create(patient_vals)
            
            return {
                'status': 'success',
                'message': 'Patient registered successfully',
                'data': {
                    'patient_id': patient.id,
                    'name': patient.name
                }
            }
            
        except Exception as e:
            _logger.error("Register Patient API Error: %s", str(e))
            return {'status': 'error', 'message': str(e)}

    # Add token refresh endpoint
    @http.route('/api/mch/provider/refresh-token', type='json', auth="none", methods=['POST'], csrf=False)
    def api_refresh_token(self, **post):
        """Refresh authentication token"""
        try:
            token = post.get('token')
            if not token:
                return {'status': 'error', 'message': 'Token is required'}
            
            provider = self._validate_token(token)
            if not provider:
                return {'status': 'error', 'message': 'Invalid or expired token'}
            
            # Generate new token
            new_token = secrets.token_urlsafe(32)
            expiration_date = datetime.now() + timedelta(days=30)
            
            provider.sudo().write({
                'auth_token': new_token,
                'token_expiration': expiration_date
            })
            
            return {
                'status': 'success',
                'message': 'Token refreshed successfully',
                'data': {
                    'token': new_token,
                    'expires_at': expiration_date.isoformat()
                }
            }
                
        except Exception as e:
            _logger.error("Token refresh error: %s", str(e))
            return {'status': 'error', 'message': 'Internal server error'}