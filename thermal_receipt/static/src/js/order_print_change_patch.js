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
        console.log("🧾 getPrintingChanges called! Order:", order, "Dining Update:", diningModeUpdate);

        const categoryMap = {}; // ✅ Use this to group products by category

        const orderlines = this.thermalReceiptChangedLines || [];
        if (orderlines.length) {
            console.log("🛒 Products in this print change:");

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

                console.log("Produkti-> ", product);

                // ✅ Group products by category
                if (!categoryMap[categoryName]) {
                    categoryMap[categoryName] = [];
                }

                categoryMap[categoryName].push({
                    name: productName,
                    qty: quantity,
                    price: line.get_display_price?.() || line.price || 0,
                });

                console.log(`Product ${index + 1}:`, {
                    name: productName,
                    qty: quantity,
                    price: line.price,
                    total: line.get_display_price?.(),
                    category: categoryName,
                });
            });
        } else {
            console.log("⚠️ No changed order lines found for this receipt.");
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
            categories_with_products: categoryMap // ✅ Grouped data
        };

        console.log("🧾 Receipt render env (printingData):", printingData);
        return printingData;
    },
});
