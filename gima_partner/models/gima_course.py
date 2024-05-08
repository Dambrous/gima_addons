from odoo import fields, models


class GimaCourse(models.Model):
    _name = "gima.course"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Course Code", required=True)
    course_type = fields.Selection([
        ('work_safety', 'Work Safety Courses'),
        ('equipment_safety', 'Equipment and Construction Site Safety Courses'),
        ('ecm', 'ECM Courses'),
        ('haccp', 'HACCP Courses'),
        ('privacy', 'Privacy Courses')
    ], string='Course Type', required=True)
    duration = fields.Integer(string="Duration", required=True)
    type_duration = fields.Selection([('hours', 'Hours'), ('days', 'Days')], string="Type Duration", required=True)
    course_icon = fields.Image()
