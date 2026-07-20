import { receiptLineGrouper } from "@point_of_sale/app/models/utils/order_change";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { patch } from "@web/core/utils/patch";

// Group the lines of a preparation ("kitchen") receipt by POS category. Falls
// back to the standard grouping (by course, when pos_restaurant is installed) se kshu e ka odoo 19
// for products that have no POS category.
patch(receiptLineGrouper, {
    getGroup(line) {
        const category = line.product_id?.pos_categ_ids?.[0];
        if (!category) {
            return super.getGroup(line);
        }
        return { index: category.sequence ?? 0, name: category.name };
    },
});

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
