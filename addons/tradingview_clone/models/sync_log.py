from odoo import models, fields, api, _
from datetime import datetime

class TradingViewSyncLog(models.Model):
    _name = 'tradingview.sync_log'
    _description = 'API Synchronization Log'
    _order = 'last_run desc'
    
    api_name = fields.Char(string='API Name', required=True)
    last_run = fields.Datetime(string='Last Run', required=True, default=fields.Datetime.now)
    status = fields.Selection([
        ('success', 'Success'),
        ('failure', 'Failure'),
    ], string='Status', required=True)
    error_message = fields.Text(string='Error Message')
    run_time = fields.Datetime(string="Run Time", default=fields.Datetime.now) 
    duration_seconds = fields.Float(string='Duration (seconds)')
    
    def cleanup_old_logs(self, days=30):
        """Cleanup logs older than specified days"""
        cutoff_date = fields.Datetime.to_string(datetime.now() - timedelta(days=days))
        old_logs = self.search([('last_run', '<', cutoff_date)])
        old_logs.unlink()
        return True