const express = require('express');
const app = express();
const postRoutes = require('./post');

app.use('/', postRoutes.post);