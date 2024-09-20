from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    gima_training_ids = fields.One2many("gima.training", "partner_id")
    gima_certifications_ids = fields.One2many("gima.certifications", "partner_id")
    is_certified_fgas = fields.Boolean(string="Certified FGAS")
    is_certified_iso_9001 = fields.Boolean(string="Certified ISO 9001")
    is_promoter = fields.Boolean(string="Financial Promoter")
    promoter_id = fields.Many2one('res.partner')
    commission_percentage = fields.Float(string="Commission Percentage")
    gima_macro_course_ids = fields.Many2many('gima.macro.course')

    def action_view_employee_certifications(self):
        certifications = self.env["gima.certifications"].search(
            [("partner_id", "in", self.child_ids.ids)]
        )
        return {
            "name": "Certifications Found",
            "res_model": "gima.certifications",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "domain": [("id", "in", certifications.ids)],
            "context": {"create": True, "edit": True}
        }

    def action_view_employees_training(self):
        trainings = self.env["gima.training"].search(
            [("partner_id", "in", self.child_ids.ids)]
        )
        return {
            "name": "Employees Trainings",
            "res_model": "gima.training",
            "type": "ir.actions.act_window",
            "view_id": self.env.ref("gima_partner.view_employee_training_tree_custom").id,
            "view_mode": "tree",
            "domain": [("id", "in", trainings.ids)],
        }
