const titles = require('../titles');

function validateMultipartMiddleware(request, response, next) {
    const title = titles[request.titleCode];

    if (!title || !title.multipart_validator) {
        return next();
    }

    const multipartValidator = title.multipart_validator;
    const validationSchema = title.validation_schema;

    multipartValidator(request.copy, response, error => {
        if (error) {
            return next(error);
        }

        const resultData = {
            ...request.copy.body,
        };

        if (Array.isArray(request.copy.files)) {
            for (const file of request.copy.files) {
                resultData[file.fieldname] = file.buffer;
            }
        }

        const validationResult = validationSchema.validate(resultData);

        if (validationResult.error) {
            console.error('[Validation Error]', validationResult.error.details);
            return next(validationResult.error);
        }

        request.resultData = validationResult.value;

        next();
    });
}

module.exports = validateMultipartMiddleware;