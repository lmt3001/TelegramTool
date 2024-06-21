const axios = require('axios');
const fs = require('fs');
const { DateTime } = require('luxon');

const loginUrl = 'https://gemzcoin.us-east-1.replicant.gc-internal.net/gemzcoin/v2.20.6/loginOrCreate';
const headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
    'cache-control': 'no-cache',
    'content-type': 'text/plain',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site'
};

function taoSid() {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let sid = '';
    for (let i = 0; i < 9; i++) {
        sid += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return sid;
}

function readQueryId(filename) {
    const lines = fs.readFileSync(filename, 'utf8').split('\n').filter(line => line.trim() && !line.startsWith('#'));
    return lines;
}

function convertQueryId(queryId) {
    const queryParams = new URLSearchParams(queryId);
    const userInfo = queryParams.get('user');
    if (userInfo) {
        const userData = decodeURIComponent(userInfo);
        const userIdMatch = /"id":(\d+)/.exec(userData);
        const userId = userIdMatch ? userIdMatch[1] : null;
        return userId;
    } else {
        console.log('Cannot convert query_id');
        return null;
    }
}

function extractInfo(queryString) {
    const parsedParams = new URLSearchParams(queryString);
    const queryId = parsedParams.get('query_id');
    const userInfo = decodeURIComponent(parsedParams.get('user'));
    const authDate = parsedParams.get('auth_date');
    const hashValue = parsedParams.get('hash');
    const userInfoObj = JSON.parse(userInfo);
    const userId = userInfoObj.id;
    const firstName = userInfoObj.first_name;
    const lastName = userInfoObj.last_name;
    const username = userInfoObj.username;
    const languageCode = userInfoObj.language_code;
    const allowsWriteToPm = userInfoObj.allows_write_to_pm;
    const formattedOutput = `
        auth_date=${authDate}\n
        hash=${hashValue}\n
        query_id=${queryId}\n
        user=%7B%22id%22%3A${userId}%2C%22first_name%22%3A%22${firstName}%22%2C%22last_name%22%3A%22${lastName}%22%2C%22username%22%3A%22${username}%22%2C%22language_code%22%3A%22${languageCode}%22%2C%22allows_write_to_pm%22%3A${allowsWriteToPm}%7D`;
    return formattedOutput;
}

async function getUserInfo(session, authData, userId) {
    const payload1 = {
        sid: taoSid(),
        id: userId,
        auth: authData
    };
    try {
        const response = await session.post(loginUrl, payload1, { headers });
        if (response.data.data && response.data.data.state) {
            const { username = 'N/A', balance = 'N/A', energy = 'N/A', rev = 'N/A', token = 'N/A' } = response.data.data.state;
            return { username, balance, energy, rev, token };
        } else {
            console.log('Data is None');
            return { username: null, balance: null, energy: null, rev: null, token: null };
        }
    } catch (error) {
        console.error(`Error fetching profile: ${error.message}`);
        return { username: null, balance: null, energy: null, rev: null, token: null };
    }
}

async function claim(session, userId, rev, token, queueLength) {
    const queue = Array.from({ length: queueLength }, () => ({
        fn: 'tap',
        async: false,
        meta: { now: Date.now() }
    }));
    const payload2 = {
        abTestsDynamicConfig: {
            "0002_invite_drawer": { active: true, rollOut: 1 },
            "0003_invite_url": { active: true, rollOut: 1 },
            "0004_invite_copy": { active: true, rollOut: 1 },
            "0010_localization": { active: true, rollOut: 1 },
            "0006_daily_reward": { active: false, rollOut: 0 },
            "0011_earn_page_buttons": { active: true, rollOut: 1 },
            "0005_invite_message": { active: true, rollOut: 1 },
            "0008_retention_with_points": { active: true, rollOut: 1 },
            "0018_earn_page_button_2_friends": { active: true, rollOut: 1 },
            "0012_rewards_summary": { active: true, rollOut: 1 },
            "0022_localization": { active: true, rollOut: 1 },
            "0023_earn_page_button_connect_wallet": { active: true, rollOut: 1 },
            "0016_throttling": { active: true, rollOut: 1 },
            "0024_rewards_summary2": { active: true, rollOut: 1 },
            "0016_throttling_v2": { active: true, rollOut: 1 },
            "0014_gift_airdrop": { active: true, rollOut: 1 }
        },
        queue,
        rev,
        requestedProfileIds: [],
        consistentFetchIds: [],
        sid: taoSid(),
        clientRandomSeed: 0,
        crqid: taoSid(),
        id: userId,
        auth: token
    };
    try {
        const response = await session.post('https://gemzcoin.us-east-1.replicant.gc-internal.net/gemzcoin/v2.18.0/replicate', payload2, { headers });
        if (response.data.data) {
            const timeUpdate = response.data.t || 'N/A';
            return timeUpdate;
        } else {
            console.log('Claim response data is None');
            return null;
        }
    } catch (error) {
        console.error(`Error claiming: ${error.message}`);
        return null;
    }
}

function countdown(secs) {
    return new Promise(resolve => {
        let interval = setInterval(() => {
            process.stdout.write(`\rSleeping for ${secs} seconds...`);
            secs--;
            if (secs < 0) {
                clearInterval(interval);
                process.stdout.write('\r                \r\n\n');
                resolve();
            }
        }, 1000);
    });
}

async function main() {
    const filename = 'query.txt';
    const queryIds = readQueryId(filename);
    let i = 1;

    while (true) {
        for (let currentQueryIndex = 0; currentQueryIndex < queryIds.length; currentQueryIndex++) {
            const queryId = queryIds[currentQueryIndex];
if (currentQueryIndex === 0 && i !== 1) {
                i = 1;
            }

            console.log(`Token: ${queryId.substring(0, 30)}...`);

            const userId = convertQueryId(queryId);
            const authData = extractInfo(queryId);

            while (true) {
                try {
                    const { username, balance, energy, rev, token } = await getUserInfo(session, authData, userId);

                    if (username) {
                        const queueLength = Math.floor(Math.random() * (60 - 30 + 1) + 30);
                        const timeUpdate = await claim(session, userId, rev, token, queueLength);

                        if (timeUpdate) {
                            console.log(`[GEMZ${i}] [${DateTime.fromMillis(timeUpdate).toFormat('HH:mm:ss')}] Username: ${username} Balance: ${balance} Energy: ${energy}`);
                        }

                        // Nếu energy < 30, thoát vòng lặp
                        if (energy < 30) {
                            break;
                        }
                    } else {
                        console.log('Username or Balance or Energy is None');
                    }
                } catch (error) {
                    console.error(`Error: ${error.message}`);
                    break;
                }

                // Chờ 0.5 giây trước khi tiếp tục vòng lặp
                await new Promise(resolve => setTimeout(resolve, 500));
            }

            i++;
        }

        const randomDelay = Math.floor(Math.random() * (120 - 50 + 1) + 50);
        await countdown(randomDelay);
    }
}

main().catch(error => console.error(`Main error: ${error.message}`));