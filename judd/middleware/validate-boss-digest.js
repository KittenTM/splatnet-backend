const crypto = require('crypto');

function validateBOSSDigestMiddleware(request, response, next) {
    // prevents viewing it in a browser to fucking up the process lmfao
    if (request.method === 'GET') {
        return response.status(404).send('Not Found');
    }

    try {
        // try to catch undefined, previously was making everything die
        if (!request.rawBody) {
            throw new Error('rawBody is undefined');
        }

        const calculatedHash = crypto.createHash('sha1').update(request.rawBody).digest('hex');
        const expectedHash = request.headers['x-boss-digest'];

		//catch all other errors
        if (calculatedHash !== expectedHash) {
            console.warn(`[Digest Mismatch] Expected: ${expectedHash}, Calculated: ${calculatedHash}`);
            return response.status(403).send('Provided BOSS digest does not match the calculated hash');
        }

        next();
    } catch (error) {
        console.error('[Digest Middleware Error]:', error.message);
        return response.status(500).send('Internal Server Error');
    }
}

module.exports = validateBOSSDigestMiddleware;