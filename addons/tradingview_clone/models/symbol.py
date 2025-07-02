from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging, re, time, requests
from datetime import datetime

_logger = logging.getLogger(__name__)

class TradingViewSymbol(models.Model):
    _name = 'tradingview.symbol'
    _description = 'Financial Symbol'
    _order = 'name asc'
    
    name = fields.Char(string='Full Name', required=True)
    symbol = fields.Char(string='Symbol', required=True)
    slug = fields.Char(string='URL Slug', compute='_compute_slug', store=True)
    exchange = fields.Char(string='Exchange')
    region = fields.Char(string='Region')
    currency = fields.Char(string='Currency')
    sector = fields.Char(string='Sector')
    industry = fields.Char(string='Industry')
    isin = fields.Char(string='ISIN')
    active = fields.Boolean(string='Active', default=True)
    type = fields.Selection([
        ('stock', 'Stock'),
        ('crypto', 'Cryptocurrency'),
        ('forex', 'Forex'),
        ('commodity', 'Commodity'),
        ('index', 'Index'),
    ], string='Type', default='stock')
    last_updated = fields.Datetime(string='Last Updated')
    forum_id = fields.Many2one('forum.forum', string='Discussion Forum')

    latest_ohlc_open = fields.Float(compute='_compute_latest_ohlc')
    latest_ohlc_close = fields.Float(compute='_compute_latest_ohlc')
    latest_ohlc_volume = fields.Float(compute='_compute_latest_ohlc')
    latest_ohlc_time = fields.Datetime(compute='_compute_latest_ohlc')

    rsi = fields.Float(compute='_compute_latest_indicators')
    macd = fields.Float(compute='_compute_latest_indicators')
    sma = fields.Float(compute='_compute_latest_indicators')
    ema = fields.Float(compute='_compute_latest_indicators')

    def _compute_latest_ohlc(self):
        for rec in self:
            ohlc = self.env['tradingview.ohlc'].search([
                ('symbol_id', '=', rec.id)
            ], order='timestamp desc', limit=1)
            rec.latest_ohlc_open = ohlc.open if ohlc else 0.0
            rec.latest_ohlc_close = ohlc.close if ohlc else 0.0
            rec.latest_ohlc_volume = ohlc.volume if ohlc else 0.0
            rec.latest_ohlc_time = ohlc.timestamp if ohlc else False

    def _compute_latest_indicators(self):
        for rec in self:
            Indicator = self.env['tradingview.technical']
            rec.rsi = Indicator._get_latest_indicator(rec.id, 'RSI')
            rec.macd = Indicator._get_latest_indicator(rec.id, 'MACD')
            rec.sma = Indicator._get_latest_indicator(rec.id, 'SMA')
            rec.ema = Indicator._get_latest_indicator(rec.id, 'EMA')

    
    @api.depends('symbol')
    def _compute_slug(self):
        for record in self:
            if record.symbol:
                record.slug = re.sub(r'[^a-z0-9]+', '-', record.symbol.lower()).strip('-')

    @api.model
    def sync_symbols_from_api(self, batch_size=100):
        """Sync symbols from external API in batches (additions & removals)"""
        Symbol = self.env['tradingview.symbol'].with_context(prefetch_fields=False)
        SyncLog = self.env['tradingview.sync_log']
        api_name = 'TwelveData'
        start_time = fields.Datetime.now()
        log_vals = {
            'api_name': api_name,
            'run_time': start_time,
            'last_run': start_time,
        }

        try:
            api_key = self.env['ir.config_parameter'].sudo().get_param('tradingview_clone.twelvedata_api_key') or 'dc80f85b8e7a4c909bb21d9574dec605'
            if not api_key:
                raise ValidationError(_('TwelveData API key is not configured'))

            url = f"https://api.twelvedata.com/stocks?apikey={api_key}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            symbols_data = data.get('data', [])
            api_symbols = {s.get('symbol') for s in symbols_data if s.get('symbol')}
            db_symbols = {rec.symbol for rec in Symbol.search([])}

            # Add in batches
            new_symbols = [
                {
                    'name': symbol_data.get('name'),
                    'symbol': symbol_data.get('symbol'),
                    'exchange': symbol_data.get('exchange'),
                    'currency': symbol_data.get('currency'),
                    'type': 'stock',
                }
                for symbol_data in symbols_data
                if symbol_data.get('symbol') and symbol_data.get('symbol') not in db_symbols
            ]

            for i in range(0, len(new_symbols), batch_size):
                Symbol.create(new_symbols[i:i + batch_size])
                time.sleep(0.01)

            # Remove obsolete
            obsolete_symbols = db_symbols - api_symbols
            if obsolete_symbols:
                Symbol.search([('symbol', 'in', list(obsolete_symbols))]).unlink()

            log_vals.update({
                'status': 'success',
                'duration_seconds': (fields.Datetime.now() - start_time).total_seconds(),
                'error_message': f"Added {len(new_symbols)}, removed {len(obsolete_symbols)}",
            })

        except Exception as e:
            log_vals.update({
                'status': 'failure',
                'error_message': str(e),
            })
            raise

        finally:
            SyncLog.create(log_vals)


    def create_forum(self):
        """Create forum for symbol discussion"""
        Forum = self.env['forum.forum']
        for symbol in self:
            if not symbol.forum_id:
                forum = Forum.create({
                    'name': f"{symbol.symbol} Discussion",
                    'description': f"Discussion forum for {symbol.name} ({symbol.symbol})",
                })
                symbol.forum_id = forum.id
        return True