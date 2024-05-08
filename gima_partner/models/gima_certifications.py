from odoo import fields, models


class GimaCertifications(models.Model):
    _name = "gima.certifications"

    partner_id = fields.Many2one("res.partner")
    type = fields.Selection(
        [
            ("fgas_individual_licence", "F-GAS Individual Licence"),
            ("fgas_company_licence", "F-GAS Company Licence"),
            ("9001_company_licence", "Company Certification 9001"),
        ],
        required=True,
        string="Type Certification",
    )
    certificate_attachment = fields.Binary(string="Certificate Attachment")
    # SOLO PATENTINO/9001/FGAS AZIEDNDALE
    # FACCIO IL PATENTINO A GIUGNO, OGNI ANNO DEVO RINNOVARLO PAGANDO(APAVE)
    certificate_number = fields.Char(string="Certificate Number")
    attachment_ids = fields.Many2many("ir.attachment", string="Attachments")
    state = fields.Selection(
        [("valid", "Valid"), ("expiring", "Expiring"), ("expired", "Expired")]
    )
    date_of_issue = fields.Date(string="Date of issue")
    maintenance_date = fields.Date(string="Date maintenance")
    expiration_date = fields.Date(string="Date expiration")
