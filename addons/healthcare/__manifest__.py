# -*- coding: utf-8 -*-
{
    'name': "healthcare",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'contacts',
        'mail',
        'calendar',
        'stock',
        'product',
        'sms',
        'website',
        'portal',
    ],

    # always loaded
    # 'data': [

    #     'security/security_groups.xml',
    #     'security/record_rules.xml',
    #     'security/ir.model.access.csv',
    #     'views/facility_views.xml',
    #     'views/patient_views.xml',
    #     'views/provider_views.xml',
    #     'views/consultation_views.xml',
    #     'views/diagnosis_views.xml',
    #     'views/testing_views.xml',
    #     'views/prescription_views.xml',
    #     'views/fulfillment_views.xml',
    #     'views/vaccination_views.xml',
    #     'views/mch_vaccination_campaign_views.xml',
    #     'views/mch_campaign_fulfillment_views.xml',
    #     'views/report_views.xml',
    #     'views/website_templates.xml',
        
    #     'data/vaccine_data.xml',
    #     'data/vaccination_schedule_data.xml',
    #     'data/ir_cron.xml',  

    #     'views/menu.xml',
    #     'views/website_menus.xml',
    #     'views/actions.xml',
    # ],

    'data': [
        # --- Security ---
        'security/security_groups.xml',
        'security/record_rules.xml',
        'security/ir.model.access.csv',

        # --- Core Menus & Actions (Load Early) ---
        'views/menu.xml',
        'views/actions.xml',

        # --- Core Models Views ---
        'views/facility_views.xml',
        'views/patient_views.xml',
        'views/provider_views.xml',
        'views/consultation_views.xml',
        'views/diagnosis_views.xml',
        'views/testing_views.xml',
        'views/prescription_views.xml',
        'views/fulfillment_views.xml',
        'views/vaccination_views.xml',

        # --- MCH Related Views ---
        'views/mch_vaccination_campaign_views.xml',
        'views/mch_campaign_fulfillment_views.xml',

        # --- Reports and Website ---
        'views/report_views.xml',
        'views/website_templates.xml',
        'views/website_menus.xml',

        # --- Data Files ---
        'data/vaccine_data.xml',
        'data/vaccination_schedule_data.xml',
        'data/ir_cron.xml',
    ],

    'controllers': ['controllers/controllers.py'],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
