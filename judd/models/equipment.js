const { DataTypes } = require('sequelize');
const { connection } = require('../database');

const Equipment = connection.define('Equipment', {
    PId: { 
        type: DataTypes.BIGINT,
        allowNull: false,
        unique: 'unique_player_weapon'
    },
    weapon: { 
        type: DataTypes.INTEGER,
        allowNull: false,
        unique: 'unique_player_weapon'
    },
    sumpaint: { 
        type: DataTypes.INTEGER 
    }
}, {
    tableName: 'equipment',
    timestamps: true,
    indexes: [
        {
            unique: true,
            fields: ['PId', 'weapon']
        }
    ]
});

module.exports = { Equipment };