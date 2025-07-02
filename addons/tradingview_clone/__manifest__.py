# -*- coding: utf-8 -*-
{
    'name': "tradingview_clone",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "InstaCódigo",
    'website': "https://www.instacodigo.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Financial',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'web',
        'website',
        'website_forum',
        'mail',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sync_log_views.xml',
        'views/tradingview_symbol_views.xml',
        'views/tradingview_ohlc.xml',
        'views/tradingview_technical.xml',
        'data/cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

