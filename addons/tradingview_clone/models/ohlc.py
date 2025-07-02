from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import requests, logging, re, time

_logger = logging.getLogger(__name__)

class TradingViewOHLC(models.Model):
    _name = 'tradingview.ohlc'
    _description = 'OHLC Price Data'
    _order = 'timestamp desc'

    symbol_id = fields.Many2one('tradingview.symbol', string='Symbol', required=True, ondelete='cascade')
    timestamp = fields.Datetime(string='Timestamp', required=True)
    open = fields.Float(string='Open Price')
    high = fields.Float(string='High Price')
    low = fields.Float(string='Low Price')
    close = fields.Float(string='Close Price')
    volume = fields.Float(string='Volume')

    _sql_constraints = [
        ('symbol_timestamp_uniq', 'unique(symbol_id, timestamp)', 'OHLC data for this symbol and timestamp already exists!'),
    ]

    @api.model
    def sync_ohlc_data(self):
        SyncLog = self.env['tradingview.sync_log']
        api_name = 'TwelveData - OHLC'
        start_time = fields.Datetime.now()
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
                url = f"https://api.twelvedata.com/time_series?symbol={symbol.symbol}&interval=1day&apikey={api_key}&outputsize=50"
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                data = response.json().get("values", [])

                for item in data:
                    timestamp = fields.Datetime.to_datetime(item.get("datetime"))
                    if not self.search([('symbol_id', '=', symbol.id), ('timestamp', '=', timestamp)]):
                        self.create({
                            'symbol_id': symbol.id,
                            'timestamp': timestamp,
                            'open': float(item.get("open", 0)),
                            'high': float(item.get("high", 0)),
                            'low': float(item.get("low", 0)),
                            'close': float(item.get("close", 0)),
                            'volume': float(item.get("volume", 0)),
                        })

            log_vals.update({
                'status': 'success',
                'duration_seconds': (fields.Datetime.now() - start_time).total_seconds(),
                'error_message': f"Synced OHLC for {len(symbols)} symbols.",
            })
        except Exception as e:
            _logger.exception("OHLC sync failed")
            log_vals.update({
                'status': 'failure',
                'error_message': str(e),
            })
            raise

        finally:
            SyncLog.create(log_vals)