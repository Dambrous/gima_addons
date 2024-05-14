from odoo import fields, models


class GimaCourse(models.Model):
    _name = "gima.course"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Course Code")
    course_type_id = fields.Many2one("gima.macro.course", string="Course Type", required=True)
    duration = fields.Integer(string="Duration", required=True)
    type_duration = fields.Selection(
        [("hours", "Hours"), ("days", "Days")], string="Type Duration", required=True
    )
    course_icon = fields.Image()
    course_location = fields.Selection([
        ("elearning", "Elearning"),
        ("online_with_teacher", "Online classroom with teacher"),
        ("mixed", "Mix Teacher/Online"),
    ],
        required=True, )
    hours_online_without_teacher = fields.Integer()
    hours_with_teacher = fields.Integer()
    sales_price = fields.Float(string="Sales Price")
    product_id = fields.Many2one("product.product", string="Product")
    product_price = fields.Float(related="product_id.list_price", readonly=False)
