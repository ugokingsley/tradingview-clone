from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import requests, logging, re, time


class TradingViewTechnical(models.Model):
    _name = 'tradingview.technical'
    _description = 'Technical Indicator Data'
    _order = 'timestamp desc'

    symbol_id = fields.Many2one('tradingview.symbol', string='Symbol', required=True, ondelete='cascade')
    indicator = fields.Char(string='Indicator', required=True)
    value = fields.Float(string='Value', required=True)
    timestamp = fields.Datetime(string='Timestamp', required=True)

    _sql_constraints = [
        ('symbol_indicator_timestamp_uniq', 'unique(symbol_id, indicator, timestamp)',
         'Technical indicator for this symbol, type and timestamp already exists!'),
    ]

    @api.model
    def _get_latest_indicator(self, symbol_id, indicator):
        rec = self.search([
            ('symbol_id', '=', symbol_id),
            ('indicator', '=', indicator)
        ], order='timestamp desc', limit=1)
        return rec.value if rec else 0.0

    @api.model
    def sync_technical_indicators(self):
        SyncLog = self.env['tradingview.sync_log']
        api_name = 'TwelveData - Indicators'
        start_time = datetime.now()
        log_vals = {
            'api_name': api_name,
            'run_time': start_time,
            'last_run': start_time,
        }

        try:
            api_key = self.env['ir.config_parameter'].sudo().get_param('tradingview_clone.twelvedata_api_key')
            if not api_key:
                raise ValidationError(_('TwelveData API key is not configured'))

            symbols = self.env['tradingview.symbol'].search([('active', '=', True)])

            for symbol in symbols:
                for ind in ['RSI', 'MACD', 'SMA', 'EMA', 'BBANDS']:
                    url = f"https://api.twelvedata.com/{ind.lower()}?symbol={symbol.symbol}&interval=1day&apikey={api_key}"
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    data = response.json().get("values", [])

                    for item in data:
                        timestamp = fields.Datetime.to_datetime(item.get("datetime"))
                        value = float(item.get(ind.lower(), 0)) if ind != 'BBANDS' else float(item.get("lower_band", 0))

                        if not self.search([
                            ('symbol_id', '=', symbol.id),
                            ('indicator', '=', ind),
                            ('timestamp', '=', timestamp)
                        ]):
                            self.create({
                                'symbol_id': symbol.id,
                                'indicator': ind,
                                'value': value,
                                'timestamp': timestamp,
                            })

            log_vals.update({
                'status': 'success',
                'duration_seconds': (fields.Datetime.now() - start_time).total_seconds(),
                'error_message': f"Synced indicators for {len(symbols)} symbols.",
            })
        except Exception as e:
            _logger.exception("Indicator sync failed")
            log_vals.update({
                'status': 'failure',
                'error_message': str(e),
            })
            raise

        finally:
            SyncLog.create(log_vals)