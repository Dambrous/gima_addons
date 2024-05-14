from odoo import fields, models


class GimaMacroCourse(models.Model):
    _name = "gima.macro.course"

    name = fields.Char(string='Name')
