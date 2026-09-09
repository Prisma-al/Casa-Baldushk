import { patch } from '@web/core/utils/patch';
import { PosOrder } from '@point_of_sale/app/models/pos_order';

patch(PosOrder.prototype,{
    export_for_printing(baseUrl, headerData){
        // therrasim funksionalitetin e plote me super
        const result = super.export_for_printing(...arguments);
        // marrim tavolinen nga funksion ose nga vete fusha ne model
        const table = this.getTable() || this.table_id;

        // shtojme table name meqe lidhet direkt me orderin
        if (table){
            result.headerData.table_no = table.table_number || table.name || '';
        }

        return result;
    }
})