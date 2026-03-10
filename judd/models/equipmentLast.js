const { DataTypes } = require('sequelize');
const { connection } = require('../database');

const EquipmentLast = connection.define('EquipmentLast', {
    PId: { 
        type: DataTypes.BIGINT,
        allowNull: false,
        unique: true
    },
    weapon: { type: DataTypes.INTEGER },
    // shoes
    Gear_Shoes: { type: DataTypes.INTEGER },
    Gear_Shoes_Skill0: { type: DataTypes.INTEGER },
    Gear_Shoes_Skill1: { type: DataTypes.INTEGER },
    Gear_Shoes_Skill2: { type: DataTypes.INTEGER },
    // clothes
    Gear_Clothes: { type: DataTypes.INTEGER },
    Gear_Clothes_Skill0: { type: DataTypes.INTEGER },
    Gear_Clothes_Skill1: { type: DataTypes.INTEGER },
    Gear_Clothes_Skill2: { type: DataTypes.INTEGER },
    // hat
    Gear_Head: { type: DataTypes.INTEGER },
    Gear_Head_Skill0: { type: DataTypes.INTEGER },
    Gear_Head_Skill1: { type: DataTypes.INTEGER },
    Gear_Head_Skill2: { type: DataTypes.INTEGER },
    // levels
    Rank: { type: DataTypes.INTEGER },
    Udemae: { type: DataTypes.INTEGER }
}, {
    tableName: 'equipment_last',
    timestamps: true
});

module.exports = { EquipmentLast };