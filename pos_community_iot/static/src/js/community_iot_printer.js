import { EpsonPrinter } from "@point_of_sale/app/utils/printer/epson_printer";

/**
 * Prints POS tickets by queueing them as community_iot_box jobs.
 *
 * Flow (BasePrinter drives the first two steps):
 *   receipt HTML -> canvas -> processCanvas() -> sendPrintingJob()
 *
 * We extend EpsonPrinter purely to inherit canvasToRaster(), which does the
 * grayscale conversion and Floyd-Steinberg dithering. That is the hard part and
 * it is already well tested in core, so nothing here re-implements it.
 *
 * We send a 1-bit bitmap, so the printed ticket looks exactly like the POS
 * receipt and accented characters need no printer codepage at all.
 *
 * The class knows nothing about Odoo models: whoever builds it supplies a
 * `queueJob` callback. That keeps the same class usable for both kitchen
 * tickets (pos.printer) and customer receipts (pos.config).
 */
export class CommunityIotPrinter extends EpsonPrinter {
    /**
     * @param {Object} options
     * @param {Function} options.queueJob  ({base64, width, height}) => Promise<{job_id}>
     */
    setup({ queueJob }) {
        super.setup(...arguments);
        this.queueJob = queueJob;
    }

    /**
     * @override
     * Turn the rendered canvas into a base64 1-bit bitmap.
     */
    processCanvas(canvas) {
        // Inherited: returns a string of "0"/"1", one character per pixel.
        const bits = this.canvasToRaster(canvas);
        return {
            base64: packRasterRows(bits, canvas.width, canvas.height),
            width: canvas.width,
            height: canvas.height,
        };
    }

    /**
     * @override
     * Queue the job in Odoo. The agent prints it a moment later.
     */
    async sendPrintingJob(image) {
        try {
            const result = await this.queueJob(image);
            return { result: Boolean(result && result.job_id) };
        } catch (error) {
            // Returning false makes BasePrinter surface the failure to the
            // cashier rather than silently dropping the ticket.
            console.error("Community IoT: could not queue print job", error);
            return { result: false, printerErrorCode: "QUEUE_FAILED" };
        }
    }

    /**
     * @override
     * Cash drawer pulses are not implemented yet; warn rather than crash.
     */
    openCashbox() {
        console.warn("Community IoT: openCashbox is not implemented");
    }
}

/**
 * Pack a "0"/"1" pixel string into bytes, 8 pixels per byte, MSB first,
 * padding each row to a whole byte.
 *
 * Row alignment matters: ESC/POS GS v 0 expects every row to start on a byte
 * boundary, so rows must not bleed into each other when the width is not a
 * multiple of 8.
 */
export function packRasterRows(bits, width, height) {
    const bytesPerRow = Math.ceil(width / 8);
    const bytes = new Uint8Array(bytesPerRow * height);

    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            if (bits[y * width + x] === "1") {
                // 1 = black pixel
                bytes[y * bytesPerRow + (x >> 3)] |= 0x80 >> (x & 7);
            }
        }
    }

    let binary = "";
    for (const byte of bytes) {
        binary += String.fromCharCode(byte);
    }
    return btoa(binary);
}
