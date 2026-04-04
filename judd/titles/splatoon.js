const multer = require('multer');
const { joi } = require('../util');
const { SplatfestResult } = require('../models/splatfest_result');
const { Equipment } = require('../models/equipment');
const { EquipmentLast } = require('../models/equipmentLast');
const { PlayerRank } = require('../models/playerRank');
const MAX_INT32 = 2147483647;

module.exports = {
    type: 'telemetry',
    result_model: {
        create: async (data) => {
            const sanitizedData = { ...data };
            
            const rankValue = parseInt(data.Rank);
            if (isNaN(rankValue) || rankValue > MAX_INT32 || rankValue < 0) {
                sanitizedData.Rank = 0;
            }

            if (parseInt(data.SessionID) > MAX_INT32) sanitizedData.SessionID = 0;

            const result = await SplatfestResult.create(sanitizedData);

            await Equipment.upsert({
                PId: sanitizedData.PId,
                weapon: sanitizedData.Weapon,
                sumpaint: sanitizedData.SumPaint
            });

            await EquipmentLast.upsert({
                PId: sanitizedData.PId,
                weapon: sanitizedData.Weapon,
                Gear_Shoes: sanitizedData.Gear_Shoes,
                Gear_Shoes_Skill0: sanitizedData.Gear_Shoes_Skill0,
                Gear_Shoes_Skill1: sanitizedData.Gear_Shoes_Skill1,
                Gear_Shoes_Skill2: sanitizedData.Gear_Shoes_Skill2,
                Gear_Clothes: sanitizedData.Gear_Clothes,
                Gear_Clothes_Skill0: sanitizedData.Gear_Clothes_Skill0,
                Gear_Clothes_Skill1: sanitizedData.Gear_Clothes_Skill1,
                Gear_Clothes_Skill2: sanitizedData.Gear_Clothes_Skill2,
                Gear_Head: sanitizedData.Gear_Head,
                Gear_Head_Skill0: sanitizedData.Gear_Head_Skill0,
                Gear_Head_Skill1: sanitizedData.Gear_Head_Skill1,
                Gear_Head_Skill2: sanitizedData.Gear_Head_Skill2,
                Rank: sanitizedData.Rank,
                Udemae: sanitizedData.Udemae
            });

            const gameMode = parseInt(sanitizedData.GameMode);
            
            if (gameMode !== 3 && gameMode !== 4) {
                const isWin = Number(sanitizedData.IsWinGame) === 1;
                const [stats, created] = await PlayerRank.findOrCreate({
                    where: { 
                        PId: sanitizedData.PId, 
                        GameMode: sanitizedData.GameMode 
                    },
                    defaults: {
                        MiiName: sanitizedData.MiiName,
                        Rank: sanitizedData.Rank,
                        FesPower: parseFloat(sanitizedData.FesPower) || 0,
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
                    MiiName: sanitizedData.MiiName,
                    Rank: sanitizedData.Rank,
                    FesPower: parseFloat(sanitizedData.FesPower) || 0,
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
        //swaps Paint_TEAM for RemainCount_TEAM.
        //Paint_TEAM is used in turf, RemainCount is used in Ranked
        Paint_Alpha: joi.numberstring(),
        Paint_Bravo: joi.numberstring(),
        RemainCount_Alpha: joi.numberstring(),
        RemainCount_Bravo: joi.numberstring(),
        FaceImg: joi.binary()
    }).unknown(true).options({ presence: 'optional' }).required(),
    multipart_validator: multer().any()
};