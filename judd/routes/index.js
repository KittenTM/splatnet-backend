const router = require('express').Router();
const titles = require('../titles');

router.post('/post', async (request, response, next) => {
    const title = titles[request.titleCode];

    if (!title) {
        console.warn(`[Blocked] POST request with unknown title code: ${request.titleCode}`);
        return response.status(404).send('Not Found');
    }

    const ResultTypeModel = title.result_model;

    try {
        const result = await ResultTypeModel.create({
            type: title.type,
            bossUniqueId: request.headers['x-boss-uniqueid'],
            bossDigest: request.headers['x-boss-digest'],
            ...request.resultData 
        });

        console.log(`\n--- ${title.type.toUpperCase()} RESULT SAVED ---`);
        console.log(`User: ${result.MiiName || 'Unknown'}`);
        console.log('----------------------------------\n');
        
    } catch (error) {
        console.error('[Database Error]', error.message);
        return next(error);
    }

    return response.send('success');
});

module.exports = {
    post: router
};