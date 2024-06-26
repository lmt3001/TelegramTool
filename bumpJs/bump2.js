const axios = require('axios');
const fs = require('fs');
const path = require('path');

const idsFilePath = path.join(__dirname, 'id.txt');
const telegramIds = fs.readFileSync(idsFilePath, 'utf8').trim().split('\n');

const authUrl = 'https://api.mmbump.pro/v1/auth';
const authHeaders = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://mmbump.pro',
    'Referer': 'https://mmbump.pro/',
    'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?1',
    'Sec-Ch-Ua-Platform': '"Android"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
};

const finishFarmingIfNeeded = async (farmingData, farmingHeaders) => {
    const currentTime = Math.floor(Date.now() / 1000);
    if (farmingData.session.status === 'inProgress' && currentTime > farmingData.session.moon_time) {
        try {
            const rdTapCount = Math.floor(Math.random() * (150000 - 50000 + 1)) + 50000;
            const finishUrl = 'https://api.mmbump.pro/v1/farming/finish';
            const finishPayload = { tapCount: rdTapCount };

            const finishResponse = await axios.post(finishUrl, finishPayload, { headers: farmingHeaders });

            if (finishResponse.status === 200) {
                console.log('Đã hoàn thành farming');

                const farmingStartUrl = 'https://api.mmbump.pro/v1/farming/start';
                const farmingStartPayload = { status: 'inProgress' };

                const startResponse = await axios.post(farmingStartUrl, farmingStartPayload, { headers: farmingHeaders });

                if (startResponse.status === 200) {
                    console.log('Bắt đầu farming...');
                } else {
                    console.error('Lỗi khi bắt đầu farming:', startResponse.data);
                }
            } else {
                console.error('Lỗi khi hoàn thành farming:', finishResponse.data);
            }
        } catch (error) {
            console.error('Lỗi khi hoàn thành farming:', error.message);
            if (error.response) {
                console.error('Response data:', JSON.stringify(error.response.data, null, 2));
            }
        }
    } else {
        console.log('Đang trong trạng thái farming');
    }
};

const xuly = async (telegramId) => {
    const authPayload = `telegram_id=${telegramId}`;

    try {
        const authResponse = await axios.post(authUrl, authPayload, { headers: authHeaders });
        if (authResponse.status === 200) {
            const hash = authResponse.data.hash;

            const farmingUrl = 'https://api.mmbump.pro/v1/farming';
            const farmingHeaders = {
                ...authHeaders,
                'Authorization': hash
            };

            let farmingData;
            let attempts = 0;
            const maxAttempts = 5;

            while (attempts < maxAttempts) {
                const farmingResponse = await axios.get(farmingUrl, { headers: farmingHeaders });
                if (farmingResponse.status === 200) {
                    farmingData = farmingResponse.data;
                    if (farmingData.telegram_id !== undefined && farmingData.balance !== undefined) {
                        break;
                    }
                }
                attempts++;
                console.log(`Thử lại lần ${attempts} để lấy dữ liệu farming...`);
            }

            if (farmingData && farmingData.telegram_id !== undefined && farmingData.balance !== undefined) {
                console.log('====================Dân Cày Airdrop====================');
                console.log('ID:', farmingData.telegram_id);
                console.log('Balance:', farmingData.balance);
                console.log('=======================Cao Bang========================');
                const currentTime = Math.floor(Date.now() / 1000);

                try {
                    if (farmingData.day_grant_first === null || (currentTime - farmingData.day_grant_first) >= 86400) {
                        const grantDayClaimUrl = 'https://api.mmbump.pro/v1/grant-day/claim';
                        await axios.post(grantDayClaimUrl, {}, { headers: farmingHeaders });
                        console.log('Điểm danh hàng ngày');
                    } else {
                        console.log('Đã điểm danh hàng ngày');
                    }
                } catch (grantError) {
                    if (grantError.response && grantError.response.status === 400) {
                        console.log('Đã điểm danh hàng ngày');
                    } else {
                        throw grantError;
                    }
                }

                if (farmingData.session.status === 'await') {
                    const farmingStartUrl = 'https://api.mmbump.pro/v1/farming/start';
                    const farmingStartPayload = { status: 'inProgress' };
                    await axios.post(farmingStartUrl, farmingStartPayload, { headers: farmingHeaders });
                    console.log('Bắt đầu farming...');
                } else if (farmingData.session.status === 'inProgress' && farmingData.session.moon_time > currentTime) {
                    console.log('Đang trong trạng thái farming');
                } else {
                    await finishFarmingIfNeeded(farmingData, farmingHeaders);
                }
            } else {
                console.error('Không thể lấy dữ liệu farming hợp lệ sau nhiều lần thử');
            }
        } else {
            throw new Error('Không thể xác thực');
        }
    } catch (error) {
        console.error('Lỗi rồi:', error);
    }
};

const animatedLoading = (durationInMilliseconds) => {
    const frames = ["|", "/", "-", "\\"];
    const endTime = Date.now() + durationInMilliseconds;
    return new Promise(resolve => {
        const interval = setInterval(() => {
            const remainingTime = Math.floor((endTime - Date.now()) / 1000);
            const frame = frames[Math.floor(Date.now() / 250) % frames.length];
            process.stdout.write(`\rChờ đợi lần yêu cầu tiếp theo ${frame} - Còn lại ${remainingTime} giây...`);
            if (Date.now() >= endTime) {
                clearInterval(interval);
                process.stdout.write("\rĐang chờ yêu cầu tiếp theo được hoàn thành.\n");
                resolve();
            }
        }, 250);
    });
};

const main = async () => {
    while (true) {
        for (let i = 0; i < telegramIds.length; i++) {
            const telegramId = telegramIds[i].trim();
            await xuly(telegramId);
        }
        await animatedLoading(6 * 60 * 60 * 1000);
    }
};

main();
