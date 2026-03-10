const { DataTypes } = require('sequelize');
const { connection } = require('../database');

const Equipment = connection.define('Equipment', {
    PId: { 
        type: DataTypes.BIGINT,
        allowNull: false
    },
    weapon: { 
        type: DataTypes.INTEGER 
    },
    sumpaint: { 
        type: DataTypes.INTEGER 
    }
}, {
    tableName: 'equipment',
    timestamps: true
});

module.exports = { Equipment };