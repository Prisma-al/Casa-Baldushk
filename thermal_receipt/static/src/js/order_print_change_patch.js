/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

console.log("📦 POS OrderChangeReceipt Patch Loaded!");

patch(PosStore.prototype, {
    async getRenderedReceipt(order, title, lines, fullReceipt = false, diningModeUpdate) {
        const previousChangedLines = this.thermalReceiptChangedLines;
        this.thermalReceiptChangedLines = lines || [];
        try {
            return await super.getRenderedReceipt(
                order,
                title,
                lines,
                fullReceipt,
                diningModeUpdate
            );
        } finally {
            this.thermalReceiptChangedLines = previousChangedLines;
        }
    },

    getPrintingChanges(order, diningModeUpdate) {
        const categoryMap = {};

        const orderlines = this.thermalReceiptChangedLines || [];
        if (orderlines.length) {
            orderlines.forEach((line, index) => {
                const product =
                    typeof line.product_id === "object"
                        ? line.product_id
                        : this.models?.["product.product"]?.get?.(line.product_id);
                const category =
                    product?.pos_categ_ids?.[0] ||
                    this.models?.["pos.category"]?.get?.(line.pos_categ_id);
                const productName =
                    line.display_name ||
                    line.name ||
                    line.full_product_name ||
                    line.get_full_product_name?.();
                const quantity = line.quantity ?? line.get_quantity?.() ?? 0;
                const categoryName = category?.name || "Uncategorized";


                if (!categoryMap[categoryName]) {
                    categoryMap[categoryName] = [];
                }

                categoryMap[categoryName].push({
                    name: productName,
                    qty: quantity,
                    price: line.get_display_price?.() || line.price || 0,
                    note: line.customer_note || line.note || line.get_customer_note?.() || "",
                });

            });
        }

        const printingData = {
            table_name: order?.table_id ? order.table_id.table_number : "",
            config_name: order?.config?.name || "",
            tracking_number: order?.tracking_number || "",
            takeaway: order?.config?.takeaway && order?.takeaway || false,
            employee_name: order?.employee_id?.name || order?.user_id?.name || "",
            order_note: order?.general_note || "",
            diningModeUpdate: diningModeUpdate || [],
            order_number: order?.pos_reference || order?.name || "",
            changes: order?.get_change ? order.get_change() : 0,
            categories_with_products: categoryMap
        };

        console.log("Receipt render env (printingData):", printingData);
        return printingData;
    },
});
