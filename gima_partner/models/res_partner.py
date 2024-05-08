from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    gima_training_ids = fields.One2many("gima.training", "partner_id")
    gima_certifications_ids = fields.One2many("gima.certifications", "partner_id")

    def action_view_certifications(self):
        certifications = self.env["gima.certifications"].search(
            [("partner_id", "in", self.child_ids.ids)]
        )
        return {
            "name": "Certifications Found",
            "res_model": "gima.certifications",
            "type": "ir.actions.act_window",
            "view_id": self.env.ref("gima_partner.view_certifications_tree_custom").id,
            "view_mode": "tree",
            "domain": [("id", "in", certifications.ids)],
        }
