from odoo import fields, models


class GimaMacroCertification(models.Model):
    _name = "gima.macro.certification"

    name = fields.Char(string='Name', required=True)
    code = fields.Char()
