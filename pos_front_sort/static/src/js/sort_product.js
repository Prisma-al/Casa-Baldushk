/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";


// helper qe te shohim a eshte produkti favorite or jo
function isFavorite(product) {
    return Boolean(product.pos_is_favorite ?? product.raw?.pos_is_favorite);
}

function compareProducts(productA, productB) {
    // number e ben qe vlera bool te dale jo si true/false por si 1/0
    // kjo ben qe te shohim nese diferenca eshte pozitive apo negative qe do na ndihmoje ne renditje
    const favoriteDiff = Number(isFavorite(productB)) - Number(isFavorite(productA));
    if (favoriteDiff) {
        return favoriteDiff;
    }

    const nameA = productA.display_name || productA.name || "";
    const nameB = productB.display_name || productB.name || "";
    // localCompare krahaso 2 stringje alfabetikisht qe na ndihmo n orderin e produkteve
    return nameA.localeCompare(nameB);
}

// ne product screen jane produktet prndj bejme patch ketu
patch(ProductScreen.prototype, {
    // ky get-i ben render produktet
    get productsToDisplay() {
        let list = [];

        // produktet nga searchi i userit
        if (this.searchWord !== "") {
            if (!this._searchTriggered) {
                this.pos.setSelectedCategory(0);
                this._searchTriggered = true;
            }
            list = this.addMainProductsToDisplay(this.getProductsBySearchWord(this.searchWord));
        } else {
            this._searchTriggered = false;
            if (this.pos.selectedCategory?.id) {
                list = this.getProductsByCategory(this.pos.selectedCategory);
            } else {
                list = this.products;
            }
        }

        if (!list || list.length === 0) {
            return [];
        }

        const excludedProductIds = [
            this.pos.config.tip_product_id?.id,
            ...this.pos.hiddenProductIds,
            ...(this.pos.session._pos_special_products_ids || []),
        ];

        const filteredProducts = list.filter(
            (product) => !excludedProductIds.includes(product.id) && product.canBeDisplayed
        );

        // change how the products are ordered
        // slice-in ia kam shtu per performanc
        return filteredProducts.sort(compareProducts).slice(0, 100);
    },
});
