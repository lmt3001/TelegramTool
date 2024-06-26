const WebSocket = require('ws');
const fs = require('fs');
const colors = require('colors');
const { setTimeout } = require('timers/promises');
const { randomInt } = require('crypto');
const axios = require('axios');
const { HttpsProxyAgent } = require('https-proxy-agent');

class Battle {
    constructor() {
        this.url = 'https://api-clicker.pixelverse.xyz/api/users';

        const config = JSON.parse(fs.readFileSync('./config.json', 'utf-8'));
        this.secret = config.secret;
        this.tgId = config.tgId;
        this.initData = config.initData;
        this.websocket = null;
        this.battleId = "";
        this.superHit = false;
        this.strike = {
            defense: false,
            attack: false
        };
        this.stop_event = false;
        this.rateLimitDelay = 1000;
    }

    async sendHit() {
        while (!this.stop_event) {
            if (this.superHit) {
                await setTimeout(130);
                continue;
            }

            const content = [
                "HIT",
                {
                    battleId: this.battleId
                }
            ];
            try {
                this.websocket.send(`42${JSON.stringify(content)}`);
            } catch {
                return;
            }
            await setTimeout(100); // Reduced delay
        }
    }


    async handleMessage(data) {
        const message = data.toString();

        if (message.startsWith('42')) {
            const parsedData = JSON.parse(message.slice(2));
            switch (parsedData[0]) {
                case "HIT":
                    process.stdout.write(`\r[ Fight ]: ${this.player1.name} (${parsedData[1].player1.energy}) - (${parsedData[1].player2.energy}) ${this.player2.name}`.yellow.bold);
                    break;
                case "SET_SUPER_HIT_PREPARE":
                    this.superHit = true;
                    break;
                case "SET_SUPER_HIT_ATTACK_ZONE":
                    this.websocket.send(`42${JSON.stringify(["SET_SUPER_HIT_ATTACK_ZONE", { battleId: this.battleId, zone: 2 }])}`);
                    this.strike.attack = true;
                    break;
                case "SET_SUPER_HIT_DEFEND_ZONE":
                    this.websocket.send(`42${JSON.stringify(["SET_SUPER_HIT_DEFEND_ZONE", { battleId: this.battleId, zone: 1 }])}`);
                    this.strike.defense = true;
                    break;
                case "SUPER_HIT_ROUND_RESULT":
                    this.superHit = false;
                    this.strike = { defense: false, attack: false };
                    break;
                case "ERROR":
                    if (parsedData[1].error === 'Not so fast! Too many requests') {
                        console.log('Hitting too fast, slowing down a bit...');
                        await setTimeout(this.rateLimitDelay);
                    }
                    break;
                case "ENEMY_LEAVED":
                    break;
                case "END":
                    await setTimeout(3000);
                    console.log('');
                    const resultMessage = `[ Fight ]: [ Result ] ${parsedData[1].result} | [ Reward ] ${parsedData[1].reward} Coins`;
                    if (parsedData[1].result === "WIN") {
                        console.log(resultMessage.green.bold);
                    } else {
                        console.log(resultMessage.red.bold);
                    }
                    this.stop_event = true;
                    break;
                default:
                    console.error('Unhandled message type:', parsedData[0]);
                    break;
            }

            if ((this.strike.attack && !this.strike.defense) || (this.strike.defense && !this.strike.attack)) {
                await new Promise((resolve) => this.websocket.once('message', resolve));
                await new Promise((resolve) => this.websocket.once('message', resolve));
            }
            if (this.strike.attack && this.strike.defense) {
                await new Promise((resolve) => this.websocket.once('message', resolve));
                this.websocket.send("3");
                await new Promise((resolve) => this.websocket.once('message', resolve));
                this.superHit = false;
            }
        }
    }

    async listenerMsg() {
        while (!this.stop_event) {
            try {
                const data = await new Promise((resolve, reject) => {
                    this.websocket.once('message', resolve);
                    this.websocket.once('error', reject);
                });
                await this.handleMessage(data);
            } catch (err) {
                console.error('Error:', err);
                this.stop_event = true;
            }
        }
    }

    connect() {
        return new Promise((resolve, reject) => {
            const uri = "wss://api-clicker.pixelverse.xyz/socket.io/?EIO=4&transport=websocket";
            const websocket = new WebSocket(uri);
            websocket.setMaxListeners(0);

            websocket.on('open', async () => {
                this.websocket = websocket;
                await new Promise((resolve) => websocket.once('message', resolve));
                const content = {
                    "tg-id": this.tgId,
                    "secret": this.secret,
                    "initData": this.initData
                };

                websocket.send(`40${JSON.stringify(content)}`);
                await new Promise((resolve) => websocket.once('message', resolve));

                const data = await new Promise((resolve) => websocket.once('message', resolve));
                const parsedData = JSON.parse(data.toString().slice(2));
                this.battleId = parsedData[1].battleId;
                this.player1 = {
                    name: parsedData[1].player1.username
                };
                this.player2 = {
                    name: parsedData[1].player2.username
                };

                console.log(`[ Fight ] : Battle between ${parsedData[1].player1.username} - ${parsedData[1].player2.username}`);

                for (let i = 5; i > 0; i--) {
                    process.stdout.write(`\r[ Fight ]: Battle starts in ${i} seconds`);
                    await setTimeout(1000);
                }
                process.stdout.clearLine();
                //console.log('');

                const listenerMsgTask = this.listenerMsg();
                const hitTask = this.sendHit();

                await Promise.all([listenerMsgTask, hitTask]);

                console.log('');
                resolve();
            });

            websocket.on('error', (err) => {
                console.error('WebSocket error:', err);
                reject(err);
            });

            websocket.on('close', (code, reason) => {
                console.log(`\nWebSocket closed: ${code}, reason: ${reason}`);
                this.stop_event = true;
                if (code === 1000 || code === 1005) {
                    resolve();
                } else {
                    reject(new Error(`\nWebSocket closed: ${code}, reason: ${reason}`));
                }
            });
        });
    }
}

const startNewBattle = async () => {
    const battle = new Battle();
    await battle.connect();
};

const config = JSON.parse(fs.readFileSync('./config.json', 'utf-8'));
queryData = config.initData;
const getUserData = async (queryData) => {
    const url = 'https://api-clicker.pixelverse.xyz/api/users';
    headers['initdata'] = queryData;
    try {
        const response = await axios.get(url,  {headers});
        return response.data;
    } catch (error) {
        console.error(`Lỗi rồi: ${error.message}`);
        return null;
    }
};
const headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://sexyzbot.pxlvrs.io',
    'priority': 'u=1, i',
    'referer': 'https://sexyzbot.pxlvrs.io/',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
};

const battleLoop = async () => {
    while (true) {
        const userResponse = await getUserData(queryData);
        if (userResponse) {
            const username = userResponse.username || "Không có tên người dùng";
            const clicksCount = userResponse.clicksCount.toLocaleString('id-ID');
            console.log(`->User: ${username} Balance: ${clicksCount}`.blue.bold);
        }
        console.log('->Starting a new battle...');
        try {
            await startNewBattle();
            console.log('Battle ended. Starting a new battle in 5 seconds...');
            console.log('========================================================');
        } catch (err) {
            console.error('Error in battle:', err);
            console.log('Retrying in 5 seconds...');
        }
        await setTimeout(5000);
    }
};

battleLoop();
