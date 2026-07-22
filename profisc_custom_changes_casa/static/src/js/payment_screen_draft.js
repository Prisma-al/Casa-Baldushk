import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(PaymentScreen.prototype, {
    async onClickDraft() {
        const order = this.currentOrder;

        if (!order || !order.lines.length) {
            this.dialog.add(AlertDialog, {
                title: _t("Porosi boshe"),
                body: _t("Nuk mund të ruash një porosi bosh."),
            });
            return;
        }

        try {
            order.is_draft = true;

            await this.pos.syncAllOrders({ orders: [order] });

            this.pos.removeOrder(order);
            this.pos.add_new_order?.() ?? this.pos.addNewOrder?.();

            this.pos.showScreen("ProductScreen");

            this.notification.add(_t("Porosia u ruajt si draft."), {
                type: "success",
            });
        } catch (error) {
            console.error("Error në ruajtjen e draftit", error);
            order.is_draft = false;
            this.dialog.add(AlertDialog, {
                title: _t("Error"),
                body: _t(
                    "Porosia nuk mund të ruhej si draft. Ju lutem provoni përsëri."
                ),
            });
        }
    },
});
