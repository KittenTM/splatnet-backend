const express = require('express');
const morgan = require('morgan');
const routes = require('./routes')
const titleCodeMiddleware = require('./middleware/title-code');
const rawBodyMiddleware = require('./middleware/raw-body');
const validateBOSSDigestMiddleware = require('./middleware/validate-boss-digest');
const copyRequestStreamMiddleware = require('./middleware/copy-request-stream');
const validateMultipartMiddleware = require('./middleware/validate-multipart');
const database = require('./database');

const app = express();
app.set('trust proxy', true);
const port = process.env.JUDD_PORT || 4000;

app.use(morgan('dev'));
app.use(titleCodeMiddleware);
app.use(rawBodyMiddleware);
app.use(validateBOSSDigestMiddleware);
app.use(copyRequestStreamMiddleware);
app.use(validateMultipartMiddleware);
app.use(routes.post);

app.use((request, response) => {
    const protocol = request.protocol;
    const hostname = request.hostname;
    const opath = request.originalUrl;

    const fullUri = `${protocol}://${hostname}${opath}`;

    console.warn(`HTTP 404 at ${fullUri}`);

    response.sendStatus(404);
});

app.use((error, request, response, next) => {
    console.log(error);
    return response.status(500).send('error');
});

async function main() {
    await database.connect();

    app.listen(port, () => {
        console.log(`Server listening on http://localhost:${port}`);
    });
}

main().catch(console.error);