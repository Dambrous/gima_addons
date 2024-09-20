from odoo import fields, models, api
from datetime import datetime, timedelta


class GimaCertifications(models.Model):
    _name = "gima.certifications"

    partner_id = fields.Many2one("res.partner")
    type_certification_id = fields.Many2one(
        'gima.macro.certification', string="Type Certification", required=True
    )
    # SOLO PATENTINO/9001/FGAS AZIEDNDALE
    # FACCIO IL PATENTINO A GIUGNO, OGNI ANNO DEVO RINNOVARLO PAGANDO(APAVE)
    certificate_number = fields.Char(string="Certificate Number")
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    state = fields.Selection(
        [("valid", "Valid"), ("expiring", "Expiring"), ("expired", "Expired"), ("waiting", "Waiting")]
    )
    date_of_issue = fields.Date(string="Date of issue")
    maintenance_date = fields.Date(string="Date maintenance")
    expiration_date = fields.Date(string="Date expiration")

    @api.model
    def update_certification_status(self):
        today = fields.Date.today()
        expiration_threshold = today + timedelta(days=120)

        today_str = fields.Date.to_string(today)
        expiration_threshold_str = fields.Date.to_string(expiration_threshold)

        # Update status to 'expiring'
        expiring_records = self.env['gima.certifications'].search([
            ('state', '=', 'valid'),
            ('expiration_date', '<=', expiration_threshold_str),
            ('expiration_date', '>=', today_str)
        ])
        expiring_records.write({'state': 'expiring'})

        # Update status to 'expired'
        scaduto_records = self.env['gima.certifications'].search([
            ('state', 'in', ['valid', 'expiring']),
            ('expiration_date', '<=', today_str)
        ])
        scaduto_records.write({'state': 'expired'})
