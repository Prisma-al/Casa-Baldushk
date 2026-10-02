import { ProductTemplate } from "@point_of_sale/app/models/product_template";
import { patch } from "@web/core/utils/patch";

// marrim linjat qe bohen skip
patch(ProductTemplate.prototype, {
    get parentPosCategIds() {
        const categIds = super.parentPosCategIds;
        const skipped = categIds.some(
            (id) => this.models["pos.category"].get(id)?.skip_preparation
        );
        return skipped ? [] : categIds;
    },
});
