const { DataTypes } = require('sequelize');
const { connection } = require('../database');

const Result = connection.define('Result', {
    type: {
        type: DataTypes.STRING,
        allowNull: true
    },
    bossUniqueId: {
        type: DataTypes.STRING,
        allowNull: true
    },
    bossDigest: {
        type: DataTypes.STRING,
        allowNull: true
    }
}, {
    tableName: 'results',
    timestamps: true
});

module.exports = {
    Result
};