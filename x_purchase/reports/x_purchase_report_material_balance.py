# -*- coding: utf-8 -*-

from odoo import models, api


class ReportPurchaseMaterialBalance(models.AbstractModel):
    _name = 'report.x_purchase.report_material_balance'
    _description = 'Purchase Material Balance'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.order'].browse(docids)
        dbsource = self.env.ref("base_external_dbsource_mysql.ZurmoCRM")

        material_balance_items = {}
        for purchase_order in docs:

            query = "SHOW TABLES"
            execute_params = {}
            metadata = True

            expect = query, execute_params, metadata
            material_balance_items = dbsource.execute_mysql(*expect)

        return {
            'doc_ids': docids,
            'doc_model': 'purchase.order',
            'docs': docs,
            'data': material_balance_items,
        }
