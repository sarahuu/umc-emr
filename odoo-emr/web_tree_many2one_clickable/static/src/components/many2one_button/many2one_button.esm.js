/* Copyright ... (same as yours)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(ListRenderer.prototype, {
    setup() {
        this.actionService = useService("action");
        super.setup(...arguments);
    },

    async onClickRelationalButton(record, column, ev) {
        ev.stopPropagation();
        const field = record.fields[column.name];
        const value = record.data[column.name];

        let resModel, resId;

        if (field.type === "many2one" && value) {
            resId = value[0];
            resModel = field.relation;
        } else if (field.type === "reference" && value) {
            resModel = value.resModel;
            resId = value.resId;
        }

        if (resModel && resId) {
            return this.actionService.doAction({
                type: "ir.actions.act_window",
                res_model: resModel,
                res_id: resId,
                views: [[false, "form"]],
                target: "new",
                additionalContext: column.context || {},
            });
        }
    },
});
