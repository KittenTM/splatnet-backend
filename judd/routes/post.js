const router = require('express').Router();
const titles = require('../titles');

router.post('/post', async (request, response, next) => {
    const title = titles[request.titleCode];

    if (!title) {
        console.error(`Title config not found for code: ${request.titleCode}`);
        return response.status(500).send('error: title not configured');
    }

    const resultType = title.type;
    const ResultTypeModel = title.result_model;

    try {
        const result = await ResultTypeModel.create({
            type: resultType,
            bossUniqueId: request.headers['x-boss-uniqueid'],
            bossDigest: request.headers['x-boss-digest'],
            ...request.resultData
        });
        console.log(`[Database] Saved ${resultType} result for ID: ${result.bossUniqueId}`);
        
    } catch (error) {
        console.error('Database Save Error:', error);
        return next(error);
    }

    return response.send('success');
});

module.exports = router;