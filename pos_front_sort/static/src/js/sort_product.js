import { PosStore } from "@point_of_sale/app/services/pos_store";
import { patch } from "@web/core/utils/patch";


patch(PosStore.prototype, {
    orderProductBySequenceAndFav(products) {
        return products.sort((productA, productB) => {
            // Number() turns the booleans into 1/0 so the difference tells us
            // which of the two products comes first.
            const favoriteDiff = Number(productB.is_favorite) - Number(productA.is_favorite);
            if (favoriteDiff) {
                return favoriteDiff;
            }
            return (productA.name || "").localeCompare(productB.name || "");
        });
    },
});
