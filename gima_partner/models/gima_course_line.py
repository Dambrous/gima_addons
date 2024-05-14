from odoo import fields, models


class GimaCourseLine(models.Model):
    _name = "gima.course.line"

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    course_id = fields.Many2one('gima.course', string='Course', required=True)

