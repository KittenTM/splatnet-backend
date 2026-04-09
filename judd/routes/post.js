const router = require('express').Router();
const rateLimit = require('express-rate-limit');
const titles = require('../titles');
const { WebhookClient, EmbedBuilder } = require('discord.js');
const axios = require('axios'); 
const lookup = require('./ids.json');
const blacklist = require('./blacklist.json');

const webhookClient = new WebhookClient({ url: process.env.WEBHOOK_URL });

const postLimiter = rateLimit({
    windowMs: 30 * 1000,
    max: 1,
    statusCode: 500,
    message: 'ratelimited chi!!! slow ur roll bud',
    standardHeaders: true,
    legacyHeaders: false,
    validate: { trustProxy: false },
});

router.post('/post', postLimiter, async (request, response, next) => {
    const title = titles[request.titleCode];

    if (!title) {
        console.warn(`[Blocked] POST request with unknown title code: ${request.titleCode}`);
        return response.status(404).send('Not Found');
    }

    const ResultTypeModel = title.result_model;
    const data = request.resultData || {};
    const pid = data.PId || 'N/A';
    const miiName = data.MiiName || 'N/A';

    try {
        let isPidValid = true;
        try {
            const spfnCheck = await axios.get(`https://account.spfn.net/api/v2/users/${pid}/mii`);
            if (typeof spfnCheck.data === 'string' && spfnCheck.data.includes('<code>0008</code>')) {
                isPidValid = false;
            }
        } catch (err) {
            isPidValid = false;
        }

        if (!isPidValid) {
            const invalidPidEmbed = new EmbedBuilder()
                .setTitle(":warning: | Invalid Telemetry received")
                .setDescription("## PID is not a valid SPFN ID\nThis submission has been BLOCKED!")
                .setColor(15158332)
                .addFields(
                    { name: "PID", value: `${pid}`, inline: true },
                    { name: "Mii Name", value: `${miiName}`, inline: true }
                );

            await webhookClient.send({ embeds: [invalidPidEmbed] });
            return response.status(500).send('Invalid PID... fuck off mate stop sending it');
        }

        const result = await ResultTypeModel.create({
            type: title.type,
            bossUniqueId: request.headers['x-boss-uniqueid'],
            bossDigest: request.headers['x-boss-digest'],
            ...request.resultData 
        });
        const offenses = [];
        if ((blacklist.weapons || []).includes(Number(data.Weapon))) offenses.push("weapon");
        if ((blacklist.clothes || []).includes(Number(data.Gear_Clothes))) offenses.push("clothes");
        if ((blacklist.rules || []).includes(Number(data.Rule))) offenses.push("rule");
        if (offenses.length > 0) {
            const sWep = offenses.includes("weapon") ? "⭐ " : "";
            const sClt = offenses.includes("clothes") ? "⭐ " : "";
            const sRul = offenses.includes("rule") ? "⭐ " : "";

            const embed = new EmbedBuilder()
                .setTitle(":warning:  | Invalid Telemetry received")
                .setDescription(`## Offending information detected in: ${offenses.join(', ')}`)
                .setFields(
                    {
                        name: "User Information:",
                        value: `-# ID in db/results: ${result.id || 'N/A'}`,
                        inline: false
                    },
                    { name: "PID", value: `${data.PId || 'N/A'}`, inline: true },
                    { name: "Mii Name", value: `${data.MiiName || 'N/A'}`, inline: true },
                    { name: "Weapon", value: `${sWep}${lookup.weapons_main[data.Weapon] || data.Weapon || 'N/A'}`, inline: true },
                    { name: "Headgear", value: `${lookup.headgear[data.Gear_Head] || data.Gear_Head || 'N/A'}`, inline: true },
                    { name: "Clothes", value: `${sClt}${lookup.clothes[data.Gear_Clothes] || data.Gear_Clothes || 'N/A'}`, inline: true },
                    { name: "Shoes", value: `${lookup.shoes[data.Gear_Shoes] || data.Gear_Shoes || 'N/A'}`, inline: true },
                    { name: "Match Information:", value: " ", inline: false },
                    { name: "Match Type", value: `${lookup.modes[data.GameMode] || 'N/A'}`, inline: true },
                    { name: "Rule", value: `${sRul}${lookup.rules[data.Rule] || data.Rule || 'N/A'}`, inline: true },
                    { name: "Stage", value: `${lookup.maps[data.Stage] || 'N/A'}`, inline: true },
                    { name: "Session ID", value: `${data.SessionID || 'N/A'}`, inline: true },
                    { name: "Team:", value: `${data.Team || 'N/A'}`, inline: true },
                    { name: " ", value: " ", inline: true },
                    { name: "Team Alpha Paint", value: `${data.Paint_Alpha || 'N/A'}`, inline: true },
                    { name: "Team Bravo Paint", value: `${data.Paint_Bravo || 'N/A'}`, inline: true }
                );

            webhookClient.send({ embeds: [embed] }).catch(err => console.error('Webhook Error:', err));
        }
        
    } catch (error) {
        console.error('[Database Error]', error.message);
        return next(error);
    }

    return response.send('success');
});

module.exports = router;