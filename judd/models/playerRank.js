const { DataTypes } = require('sequelize');
const { connection } = require('../database');

const PlayerRank = connection.define('PlayerRank', {
    PId: {
        type: DataTypes.BIGINT,
        primaryKey: true,
        allowNull: false
    },
    GameMode: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        allowNull: false
    },
    MiiName: {
        type: DataTypes.STRING,
        allowNull: true
    },
    Rank: {
        type: DataTypes.INTEGER,
        defaultValue: 0
    },
    WinSum: {
        type: DataTypes.INTEGER,
        defaultValue: 0
    },
    LoseSum: {
        type: DataTypes.INTEGER,
        defaultValue: 0
    },
    RankingScore: {
        type: DataTypes.FLOAT,
        defaultValue: 0.0
    }
}, {
    tableName: 'player_ranks',
    timestamps: true
});

module.exports = { PlayerRank };