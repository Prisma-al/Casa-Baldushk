/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

const originalPrintReceipts = PosStore.prototype.printReceipts;

patch(PosStore.prototype, {
    async printReceipts(order, printer, key, value, isNew = false, diningModeUpdate = false) {
        let printed = false;

        for (let i = 0; i < 3; i++) {
            printed = await originalPrintReceipts.call(
                this,
                order,
                printer,
                key,
                value,
                isNew,
                diningModeUpdate
            );
        }

        return printed;
    },
});