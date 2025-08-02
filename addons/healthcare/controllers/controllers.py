# -*- coding: utf-8 -*-
# from odoo import http


# class Healthcare(http.Controller):
#     @http.route('/healthcare/healthcare', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/healthcare/healthcare/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('healthcare.listing', {
#             'root': '/healthcare/healthcare',
#             'objects': http.request.env['healthcare.healthcare'].search([]),
#         })

#     @http.route('/healthcare/healthcare/objects/<model("healthcare.healthcare"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('healthcare.object', {
#             'object': obj
#         })

