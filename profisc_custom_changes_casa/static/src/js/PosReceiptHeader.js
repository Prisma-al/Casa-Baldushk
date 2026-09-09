import { patch } from '@web/core/utils/patch';
import { PosOrder } from '@point_of_sale/app/models/pos_order';

patch(PosOrder.prototype,{
    export_for_printing(){
        // therrasim funksionalitetin e plote me super
        const result = super.export_for_printing(...arguments);

        // shtojme table name meqe lidhet direkt me orderin
        if (this.table_id){
            result.table_name = this.table_id.name;
        }
        // nese param se ka table_id
        else if(this.table) {
            result.table_name = this.table.name;
        }

        return result;
    }
})