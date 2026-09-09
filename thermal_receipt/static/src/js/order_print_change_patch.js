import { receiptLineGrouper } from "@point_of_sale/app/models/utils/order_change";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { patch } from "@web/core/utils/patch";

patch(receiptLineGrouper, {
    getGroup(line) {
        const category = line.product_id?.pos_categ_ids?.[0];
        const categoryData = {
            category: category?.name || "",
            categoryIndex: category?.sequence ?? 0,
        };
        const course = line.config?.module_pos_restaurant ? line.course_id : null;
        if (!course) {
            // kur ska course direkt me categ
            return { index: -1, name: "", ...categoryData };
        }
        return { index: course.index, name: course.name, ...categoryData };
    },
});


// Split each course group into category sub groups, sorted by category sequence.
patch(PosStore.prototype, {
    async prepareReceiptGroupedData(data) {
        const result = await super.prepareReceiptGroupedData(data);

        for (const group of result.changes?.groupedData || []) {
            const subGroups = group.data.reduce((acc, line) => {
                const { category = "", categoryIndex = 0 } = line.group || {};
                if (!acc[category]) {
                    acc[category] = { name: category, index: categoryIndex, data: [] };
                }
                acc[category].data.push(line);
                return acc;
            }, {});
            group.subGroups = Object.values(subGroups).sort((a, b) => a.index - b.index);
        }

        return result;
    },


    getOrderData(order, reprint) {
        return {
            ...super.getOrderData(order, reprint),
            table_name: order.table_id?.table_number || "",
        };
    },
});
