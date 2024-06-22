const axios = require('axios');
const fs = require('fs');
const colors = require('colors');

const BASE_URL = "https://cexp.cex.io/api/";
const DEV_AUTH_DATA = 906306292;

const headers = {
    "origin": "https://cexp.cex.io",
    "referer": "https://cexp.cex.io"
};

async function makePostRequest(endpoint, payload) {
    const url = BASE_URL + endpoint;
    try {
        const response = await axios.post(url, payload, { headers });
        return response.data;
    } catch (error) {
        // console.error(colors.red.bold(`Error during ${endpoint}: ${error}`));
        return null;
    }
}

async function getUserInfo(query_id) {
    const payload = {
        "devAuthData": DEV_AUTH_DATA,
        "authData": query_id,
        "data": {},
        "platform": "android"
    };
    return await makePostRequest("getUserInfo", payload);
}

async function claimFarm(query_id) {
    const payload = {
        "devAuthData": DEV_AUTH_DATA,
        "authData": query_id,
        "data": {},
        "platform": "android"
    };
    return await makePostRequest("claimFarm", payload);
}

async function startFarm(query_id) {
    const payload = {
        "devAuthData": DEV_AUTH_DATA,
        "authData": query_id,
        "data": {},
        "platform": "android"
    };
    return await makePostRequest("startFarm", payload);
}

async function claimTaps(query_id, taps) {
    const payload = {
        "authData": query_id,
        'data': {'taps': taps}
    };
    return await makePostRequest("claimTaps", payload);
}

function countdown(secs) {
    let interval = setInterval(() => {
        if (secs > 0) {
            process.stdout.write(`\r${colors.magenta.bold(`Sleeping for ${secs} seconds...`)}`);
            secs--;
        } else {
            clearInterval(interval);
            process.stdout.write("\r" + " ".repeat(50));
            console.log("\n");
        }
    }, 1000);
}

function readQueryIds(filename) {
    try {
        const data = fs.readFileSync(filename, 'utf8');
        return data.split('\n').map(line => line.trim()).filter(line => line && !line.startsWith('#'));
    } catch (error) {
        console.error(colors.red.bold(`Error reading file ${filename}`));
        return [];
    }
}

function parseQueryString(queryString) {
    return queryString.split('&').reduce((acc, part) => {
        const [key, value] = part.split('=');
        acc[decodeURIComponent(key)] = decodeURIComponent(value);
        return acc;
    }, {});
}

async function main() {
    const filename = "query_id.txt";
    const queryIds = readQueryIds(filename);
    while (true) {
        for (const query_id of queryIds) {
            console.log(colors.yellow.bold(`[CEXP] [${new Date().toLocaleTimeString()}] ${query_id.length > 20 ? query_id.slice(0, 20) + '...' : query_id}...`));

            const userInfo = await getUserInfo(query_id);
            if (userInfo) {
                const { balance = 'N/A', first_name = 'N/A', last_name = 'N/A' } = userInfo.data;
                console.log(colors.green.bold(`Name: ${first_name} ${last_name}  Balance: ${balance} CEXP`));
            } else {
                console.log(colors.red.bold("User information is not available."));
            }

            const farmInfo = await claimFarm(query_id);
            if (farmInfo) {
                console.log(colors.green.bold(`Status: ${farmInfo.status}`));
                console.log(colors.green.bold(`Balance: ${farmInfo.data?.balance || 'N/A'}`));
                console.log(colors.green.bold(`Claimed Balance: ${farmInfo.data?.claimedBalance || 'N/A'}`));
            } else {
                console.log(colors.blue.bold("->Claim Farm: Not available."));
            }

            const startInfo = await startFarm(query_id);
            if (startInfo) {
                console.log(colors.green.bold(`->Start Farm: ${startInfo.status}`));
            } else {
                console.log(colors.blue.bold("->Start Farm: Not available."));
            }

            const claimInfo = await claimTaps(query_id, 5);
            if (claimInfo) {
                console.log(colors.green.bold(`->Claim Taps: ${claimInfo.status}`));
                const availableTaps = claimInfo.data?.availableTaps || 0;
                console.log(colors.green.bold(`->Remain Taps: ${availableTaps}`));
            } else {
                console.log(colors.blue.bold("->Claim Taps: Not available."));
            }
        }

        const randomDelay = Math.floor(Math.random() * (500 - 300 + 1)) + 300;
        countdown(randomDelay);
        await new Promise(resolve => setTimeout(resolve, randomDelay * 1000));
    }
}

main();
