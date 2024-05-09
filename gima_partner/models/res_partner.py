from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    gima_training_ids = fields.One2many("gima.training", "partner_id")
    gima_certifications_ids = fields.One2many("gima.certifications", "partner_id")
    is_certified_fgas = fields.Boolean(string="Certified FGAS")
    is_certified_iso_9001 = fields.Boolean(string="Certified ISO 9001")

    @api.onchange('gima_certifications_ids')
    def _onchange_certification(self):
        for certification in self.gima_certifications_ids:
            if certification.type in ['fgas_individual_licence', 'fgas_company_licence'] and certification.state in (
            'valid', 'expiring'):
                self.is_certified_fgas = True
                break
        else:
            self.is_certified_fgas = False

    @api.onchange('gima_certifications_ids')
    def _onchange_certification(self):
        for certification in self.gima_certifications_ids:
            if certification.type == '9001_company_licence' and certification.state in (
                    'valid', 'expiring'):
                self.is_certified_iso_9001 = True
                break
        else:
            self.is_certified_iso_9001 = False

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
