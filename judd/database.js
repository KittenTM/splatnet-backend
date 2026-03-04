const { Sequelize } = require('sequelize');

const sequelize = new Sequelize(process.env.DB_URL, {
    dialect: 'postgres',
    logging: false,
    pool: { max: 5, min: 0, acquire: 30000, idle: 10000 }
});

async function connect() {
    try {
        await sequelize.authenticate();
        console.log('PostgreSQL connected.');
        await sequelize.sync({ force: true });
        console.log('PostgreSQL synchronized');
    } catch (error) {
        console.error('PostgreSQL connection error:', error);
        process.exit(1);
    }
}

module.exports = {
    connection: sequelize,
    connect
};