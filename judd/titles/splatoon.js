const multer = require('multer');
const { joi } = require('../util');
const { SplatfestResult } = require('../models/splatfest_result');
const { Equipment } = require('../models/equipment');
const { EquipmentLast } = require('../models/equipmentLast');
const { PlayerRank } = require('../models/playerRank');

module.exports = {
    type: 'telemetry',
    result_model: {
        create: async (data) => {
            const result = await SplatfestResult.create(data);

            await Equipment.upsert({
                PId: data.PId,
                weapon: data.Weapon,
                sumpaint: data.SumPaint
            });

            await EquipmentLast.upsert({
                PId: data.PId,
                weapon: data.Weapon,
                Gear_Shoes: data.Gear_Shoes,
                Gear_Shoes_Skill0: data.Gear_Shoes_Skill0,
                Gear_Shoes_Skill1: data.Gear_Shoes_Skill1,
                Gear_Shoes_Skill2: data.Gear_Shoes_Skill2,
                Gear_Clothes: data.Gear_Clothes,
                Gear_Clothes_Skill0: data.Gear_Clothes_Skill0,
                Gear_Clothes_Skill1: data.Gear_Clothes_Skill1,
                Gear_Clothes_Skill2: data.Gear_Clothes_Skill2,
                Gear_Head: data.Gear_Head,
                Gear_Head_Skill0: data.Gear_Head_Skill0,
                Gear_Head_Skill1: data.Gear_Head_Skill1,
                Gear_Head_Skill2: data.Gear_Head_Skill2,
                Rank: data.Rank,
                Udemae: data.Udemae
            });
            const gameMode = parseInt(data.GameMode);
            
            if (gameMode !== 3 && gameMode !== 4) {
                const isWin = Number(data.IsWinGame) === 1;
                const [stats, created] = await PlayerRank.findOrCreate({
                    where: { 
                        PId: data.PId, 
                        GameMode: data.GameMode 
                    },
                    defaults: {
                        MiiName: data.MiiName,
                        Rank: data.Rank,
                        WinSum: 0,
                        LoseSum: 0,
                        RankingScore: 0
                    }
                });
                let currentWins = stats.WinSum;
                let currentLosses = stats.LoseSum;

                if (isWin) {
                    currentWins += 1;
                } else {
                    currentLosses += 1;
                }

                const totalGames = currentWins + currentLosses;

                const winRate = totalGames > 0 ? (currentWins / totalGames) : 0;
                const newRankingScore = currentWins * winRate * 10;

                await stats.update({
                    MiiName: data.MiiName,
                    Rank: data.Rank,
                    WinSum: currentWins,
                    LoseSum: currentLosses,
                    RankingScore: newRankingScore
                });
            }

            return result;
        }
    },
    validation_schema: joi.object({
        ServerEnv: joi.string(),
        PId: joi.numberstring(),
        MiiName: joi.string(),
        Model: joi.numberstring(),
        Skin: joi.numberstring(),
        EyeColor: joi.numberstring(),
        Weapon: joi.numberstring(),
        SumPaint: joi.numberstring(),
        Gear_Shoes: joi.numberstring(),
        Gear_Shoes_Skill0: joi.numberstring(),
        Gear_Shoes_Skill1: joi.numberstring(),
        Gear_Shoes_Skill2: joi.numberstring(),
        Gear_Clothes: joi.numberstring(),
        Gear_Clothes_Skill0: joi.numberstring(),
        Gear_Clothes_Skill1: joi.numberstring(),
        Gear_Clothes_Skill2: joi.numberstring(),
        Gear_Head: joi.numberstring(),
        Gear_Head_Skill0: joi.numberstring(),
        Gear_Head_Skill1: joi.numberstring(),
        Gear_Head_Skill2: joi.numberstring(),
        Rank: joi.numberstring(),
        Udemae: joi.numberstring(),
        RegularKillSum: joi.numberstring(),
        WinSum: joi.numberstring(),
        LoseSum: joi.numberstring(),
        TodaysCondition: joi.numberstring(),
        Region: joi.string(),
        Area: joi.numberstring(),
        FesID: joi.numberstring(),
        FesState: joi.numberstring(),
        FesTeam: joi.numberstring(),
        FesGrade: joi.numberstring(),
        FesPoint: joi.numberstring(),
        FesPower: joi.numberstring(),
        BestFesPower: joi.numberstring(),
        Money: joi.numberstring(),
        Shell: joi.numberstring(),
        TotalBonusShell: joi.numberstring(),
        MatchingTime: joi.numberstring(),
        IsRematch: joi.numberstring(),
        SaveDataCorrupted: joi.numberstring(),
        DisconnectedPId: joi.numberstring(),
        DisconnectedMemHash: joi.numberstring(),
        SessionID: joi.numberstring(),
        StartNetworkTime: joi.numberstring(),
        GameMode: joi.numberstring(),
        Rule: joi.numberstring(),
        Stage: joi.numberstring(),
        Team: joi.numberstring(),
        IsWinGame: joi.numberstring(),
        Kill: joi.numberstring(),
        Death: joi.numberstring(),
        Paint: joi.numberstring(),
        IsNetworkBurst: joi.numberstring(),
        BottleneckPlayerNum: joi.numberstring(),
        MaxSilenceFrame: joi.numberstring(),
        MemoryHash: joi.numberstring(),
        Paint_Alpha: joi.numberstring(),
        Paint_Bravo: joi.numberstring(),
        FaceImg: joi.binary()
    }).unknown(true).options({ presence: 'optional' }).required(),
    multipart_validator: multer().any()
};