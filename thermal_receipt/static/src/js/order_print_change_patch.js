import { PosStore } from "@point_of_sale/app/services/pos_store";
import { patch } from "@web/core/utils/patch";

// The preparation ("kitchen") receipt is grouped by course, which is what
// pos_restaurant's own receiptLineGrouper already does -- nothing to override.
//
// The receipt template is rendered with `data` only, so the table number has to
// be put there explicitly.
patch(PosStore.prototype, {
    getOrderData(order, reprint) {
        return {
            ...super.getOrderData(order, reprint),
            table_name: order.table_id?.table_number || "",
        };
    },
});
