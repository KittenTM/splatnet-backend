const titles = require('../titles');

function titleCodeMiddleware(request, response, next) {
    request.titleCode = 'wup-agmj'; 

    if (!titles[request.titleCode]) {
        console.error(`Titles Available: ${Object.keys(titles)}`);
        return next(`No valid title config set for title code ${request.titleCode}`);
    }

    next();
}

module.exports = titleCodeMiddleware;