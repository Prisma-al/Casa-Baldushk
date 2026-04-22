/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";

patch(ActionpadWidget.prototype, {
    async onClickSendOrder() {
        const order = this.pos.get_order();
        if (!order || order.is_empty()) {
            console.warn("No active order found or order is empty");
            return;
        }

        if (this.pos.config.module_pos_restaurant) {
            if (!this.clicked) {
                this.clicked = true;
                try {
                    order.is_draft = true;
                    order.sent_fiscal = false; // Don't fiscalize kitchen orders
                    await this.pos.sendOrderInPreparationUpdateLastChange(order);
                    console.log("Order sent to Kitchen Display successfully (skipping fiscalization)");
                    // Keep is_draft = true to prevent fiscalization during auto-sync
                    // Only the Validate button should set is_draft = false
                } catch (error) {
                    console.error("Failed to send order to Kitchen Display:", error);
                } finally {
                    this.clicked = false;
                }
            }
        } else {
            await order.finalize();
            console.log("Order finalized (non-restaurant)");
        }
    },
});
