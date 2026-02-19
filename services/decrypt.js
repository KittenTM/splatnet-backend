const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const BOSS_AES_KEY = process.env.BOSS_AES_KEY;
const BOSS_HMAC_KEY = process.env.BOSS_HMAC_KEY;

async function run() {
    try {
        if (!BOSS_AES_KEY || !BOSS_HMAC_KEY) {
            process.stderr.write("decrypt: missing environment keys\n");
            process.exit(1);
        }

        const data = fs.readFileSync(process.argv[2]);

        const IV = Buffer.concat([
            data.subarray(0x0C, 0x18),
            Buffer.from([0x00, 0x00, 0x00, 0x01])
        ]);

        const decipher = crypto.createDecipheriv('aes-128-ctr', Buffer.from(BOSS_AES_KEY, 'hex'), IV);
        const decrypted = Buffer.concat([decipher.update(data.subarray(0x20)), decipher.final()]);

        const hmac = decrypted.subarray(0, 0x20);
        const content = decrypted.subarray(0x20);

        const calculatedHmac = crypto.createHmac('sha256', Buffer.from(BOSS_HMAC_KEY, 'hex'))
            .update(content)
            .digest();

        if (!calculatedHmac.equals(hmac)) {
            process.stderr.write("Console HMAC check failed. Is the key correct?\n");
            process.exit(1);
        }

        process.stdout.write(content);
    } catch (err) {
        process.stderr.write(`decrypt.js: ${err.message}\n`);
        process.exit(1);
    }
}

run();