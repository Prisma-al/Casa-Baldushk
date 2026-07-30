import { PosStore } from "@point_of_sale/app/services/pos_store";
import { patch } from "@web/core/utils/patch";
import { CommunityIotPrinter } from "@pos_community_iot/js/community_iot_printer";

/**
 * Two separate hooks, because Odoo prints kitchen tickets and customer receipts
 * through different objects:
 *
 *   createPrinter()          -> one printer per pos.printer record (kitchen).
 *                               Core handles category routing and the Order
 *                               button from there.
 *                               NOTE: camelCase. Odoo 18 called this
 *                               create_printer; it was renamed in 19.
 *   afterProcessServerData() -> hardwareProxy.printer, which is what
 *                               PosPrinterService.print() uses for the customer
 *                               receipt ("Print Receipt"). Same place core
 *                               attaches the Epson receipt printer.
 */
patch(PosStore.prototype, {
    /** Kitchen / order printers. */
    createPrinter(config) {
        if (config.printer_type !== "community_iot") {
            return super.createPrinter(...arguments);
        }
        return new CommunityIotPrinter({
            queueJob: (image) =>
                this.data.call("pos.printer", "create_iot_print_job", [
                    [config.id],
                    image.base64,
                    image.width,
                    image.height,
                ]),
        });
    },

    /** Customer receipt printer. */
    async afterProcessServerData() {
        const result = await super.afterProcessServerData(...arguments);

        if (this.config.community_iot_receipt_device_id) {
            this.hardwareProxy.printer = new CommunityIotPrinter({
                queueJob: (image) => {
                    const order = this.getOrder();
                    return this.data.call("pos.config", "create_iot_receipt_job", [
                        [this.config.id],
                        image.base64,
                        image.width,
                        image.height,
                        order?.name || order?.pos_reference || "",
                        order?.id && typeof order.id === "number" ? order.id : false,
                    ]);
                },
            });
        }

        return result;
    },
});
