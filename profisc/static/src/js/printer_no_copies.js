/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

const originalPrintReceipts = PosStore.prototype.printReceipts;

function delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

patch(PosStore.prototype, {
    async printReceipts(order, printer, key, value, isNew = false, diningModeUpdate = false) {
        console.log("=== printReceipts PATCH TRIGGERED ===");
        console.log("Receipt type:", key);
        console.log("Printer:", printer);
        console.log("Order:", order?.name);

        let printed = false;

        const copies = key === "New" ? 3 : 1;
        console.log("Copies to print:", copies);

        for (let i = 0; i < copies; i++) {
            console.log(`Printing copy ${i + 1} / ${copies}`);

            printed = await originalPrintReceipts.call(
                this,
                order,
                printer,
                key,
                value,
                isNew,
                diningModeUpdate
            );

            console.log(`Result of copy ${i + 1}:`, printed);

            if (!printed) {
                console.warn("Printing failed, stopping further copies");
                break;
            }

            if (i < copies - 1) {
                console.log("Waiting before next copy...");
                await delay(300);
            }
        }

        console.log("Final print result:", printed);
        console.log("=== END printReceipts PATCH ===");

        return printed;
    },
});