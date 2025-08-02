from odoo import models, fields, api
from datetime import datetime, timedelta

class MissedAppointmentsReport(models.AbstractModel):
    _name = 'report.maternal_child_health.missed_appointments_report'
    _description = 'Missed Appointments Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        facilities = self.env['mch.facility'].browse(docids) if docids else self.env['mch.facility'].search([])
        
        return {
            'doc_ids': facilities.ids,
            'doc_model': 'mch.facility',
            'docs': facilities,
            'get_missed_appointments': self._get_missed_appointments,
        }
    
    def _get_missed_appointments(self, facility, days=30):
        date_from = fields.Date.today() - timedelta(days=days)
        
        consultations = self.env['mch.consultation'].search([
            ('facility_id', '=', facility.id),
            ('date', '>=', date_from),
            ('state', '=', 'draft'),
        ])
        
        return consultations