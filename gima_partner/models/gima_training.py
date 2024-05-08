from odoo import fields, models, api


class GimaTraining(models.Model):
    _name = "gima.training"

    name = fields.Char(string="Name", compute="_compute_gima_course", store=True)
    partner_id = fields.Many2one("res.partner", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    location = fields.Char(string="Location", required=True)
    course_id = fields.Many2one("gima.course", required=True)
    type_course_id = fields.Selection(
        string="Macro Group Course", related="course_id.course_type"
    )
    duration = fields.Integer(string="Duration", related="course_id.duration")
    type_duration = fields.Selection(
        string="Duration Type", related="course_id.type_duration"
    )
    certificate_course_attachment = fields.Binary(
        string="Certificate Course Attachment"
    )
    state = fields.Selection(
        [("valid", "Valid"), ("expiring", "Expiring"), ("expired", "Expired")]
    )

    @api.depends("partner_id", "course_id")
    def _compute_gima_course(self):
        for training in self:
            if training.partner_id and training.course_id:
                training.name = (
                    training.course_id.name + ": " + training.partner_id.name
                )
