from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_vaccine = fields.Boolean(string="Is Vaccine")