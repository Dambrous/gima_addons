from odoo import fields, models, api


class GimaTraining(models.Model):
    _name = "gima.training"

    name = fields.Char(string="Name", compute="_compute_gima_course", store=True)
    partner_id = fields.Many2one("res.partner", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    expiration_date = fields.Date(string="Expiration Date", required=True)
    location = fields.Selection(string="Location",  related="course_id.course_location", required=True)
    course_id = fields.Many2one("gima.course", required=True)
    type_course_id = fields.Many2one(
        'gima.macro.course', string="Macro Group Course", related="course_id.course_type_id"
    )
    duration = fields.Integer(string="Duration", related="course_id.duration")
    type_duration = fields.Selection(
        string="Duration Type", related="course_id.type_duration"
    )
    certificate_course_attachment_ids = fields.Many2many("ir.attachment", string="Attachments")
    state = fields.Selection(
        [("valid", "Valid"), ("expiring", "Expiring"), ("expired", "Expired"), ("waiting", "Waiting")]
    )
    product_price = fields.Float(string="Product Price")
    promoter_id = fields.Many2one("res.partner", related="partner_id.parent_id.promoter_id", string="Promoter")

    @api.depends("partner_id", "course_id")
    def _compute_gima_course(self):
        for training in self:
            if training.partner_id and training.course_id:
                training.name = (
                    training.course_id.name + ": " + training.partner_id.name
                )

    @api.onchange('course_id')
    def _onchange_course_id(self):
        if self.course_id:
            self.product_price = self.course_id.product_price
        else:
            self.product_price = 0.0
