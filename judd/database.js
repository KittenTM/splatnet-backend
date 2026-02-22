const { Sequelize } = require('sequelize');

const connection_string = process.env.DB_URL;
const options = {
    dialect: 'postgres',
    logging: false,
    pool: { max: 5, min: 0, acquire: 30000, idle: 10000 }
};

const sequelize = new Sequelize(connection_string, options);

module.exports = {
    connection: sequelize,
    connect
};

require('./models/result');
require('./models/splatfest_result');

async function connect() {
    try {
        await sequelize.authenticate();
        console.log('PostgreSQL connected.');

        await sequelize.sync();
        console.log('PostgreSQL synchronized');
    } catch (error) {
        console.error('PostgreSQL connection error:', error);
        process.exit(1);
    }
}