from odoo import models, fields, api

class VaccinationHistoryReport(models.AbstractModel):
    _name = 'report.maternal_child_health.vaccination_history_report'
    _description = 'Vaccination History Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        patients = self.env['mch.patient'].browse(docids)
        
        return {
            'doc_ids': docids,
            'doc_model': 'mch.patient',
            'docs': patients,
            'get_vaccination_history': self._get_vaccination_history,
        }
    
    def _get_vaccination_history(self, patient):
        return {
            'administered': patient.vaccination_ids.sorted(key=lambda r: r.date_administered),
            'pending': self._get_pending_vaccinations(patient),
        }
    
    def _get_pending_vaccinations(self, patient):
        if not patient.is_child or not patient.date_of_birth:
            return []
            
        age_days = (fields.Date.today() - patient.date_of_birth).days
        schedules = self.env['mch.vaccine.schedule'].search([
            ('min_age_days', '<=', age_days),
            ('max_age_days', '>=', age_days),
        ])
        
        administered_vaccines = patient.vaccination_ids.mapped('vaccine_id')
        pending = schedules.filtered(lambda s: s.vaccine_id not in administered_vaccines)
        
        return pending.mapped('vaccine_id')