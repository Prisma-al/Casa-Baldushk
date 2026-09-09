import { receiptLineGrouper } from "@point_of_sale/app/models/utils/order_change";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { patch } from "@web/core/utils/patch";

patch(receiptLineGrouper, {
    getGroup(line) {
        const course =
            line.config?.module_pos_restaurant && line.course_id ? line.course_id.name : "";
        const category = line.product_id?.pos_categ_ids?.[0];
        if (!category) {
            return { ...super.getGroup(line), course };
        }
        return { index: category.sequence ?? 0, name: category.name, course };
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
