import { KeyPair, keyStores, connect, Near } from "near-api-js";
import { parseSeedPhrase } from "near-seed-phrase";
import { Twisters } from "twisters";
import BigNumber from "bignumber.js";

export const mainnetConfig = {
  networkId: "mainnet",
  nodeUrl: 'https://rpc.mainnet.near.org',
  walletUrl: "https://wallet.mainnet.near.org",
  helperUrl: "https://helper.mainnet.near.org",
};

import { acc } from "./account.js";

const near = new Near(mainnetConfig);
const twisters = new Twisters();

const getAccount = async (accountId, seedPhrase) => {
  try {
    const keyStore = new keyStores.InMemoryKeyStore();
    const { secretKey } = parseSeedPhrase(seedPhrase);
    const keyPair = KeyPair.fromString(secretKey);
    await keyStore.setKey(mainnetConfig.networkId, accountId, keyPair);

    const connectionConfig = { deps: { keyStore }, ...mainnetConfig };
    const accountConnection = await connect(connectionConfig);
    return await accountConnection.account(accountId);
  } catch (error) {
    throw new Error(`Lỗi đọc tài khoản: ${error.message}`);
  }
};

const getNearBalance = async (accountId, seedPhrase) => {
  const account = await getAccount(accountId, seedPhrase);
  const Nearbalance = await account.getAccountBalance();
  return new BigNumber(Nearbalance.total).dividedBy(1e24);
};

const getRandomMinutes = (min, max) => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

const mineAndUpdate = async (accountId, seedPhrase, delayInHours) => {
  try {
    const NearBalanceUser = await getNearBalance(accountId, seedPhrase);

    twisters.put(accountId, {
      text: `Account ID : ${accountId}\nNear Balance : ${NearBalanceUser}\nTrạng thái : Claiming...`,
    });

    let transactionHash = null;
    while (!transactionHash) {
      try {
        const account = await getAccount(accountId, seedPhrase);
        const callContract = await account.functionCall({
          contractId: "game.hot.tg",
          methodName: "claim",
          args: {},
        });

        transactionHash = callContract.transaction.hash;

        twisters.put(accountId, {
          text: `Account ID : ${accountId}\nNear Balance : ${NearBalanceUser}\nTrạng thái : Claimed ${callContract.transaction.hash}...`,
        });
        await delay(5000);
        twisters.put(accountId, { active: false, removed: true, text: `Account ID : ${accountId}\nNear Balance : ${NearBalanceUser}\nTrạng thái : Claimed ${callContract.transaction.hash}...` });
      } catch (contractError) {
        twisters.put(accountId, { text: `Account ID : ${accountId}\nNear Balance : ${NearBalanceUser}\nTrạng thái : ${contractError.message}...` });
        await delay(5000);
      }
    }


    const randomMinutes = getRandomMinutes(5, 60);
    const totalDelay = delayInHours * 3600 * 1000 + randomMinutes * 60 * 1000;

    twisters.put(accountId, {
      text: `Account ID : ${accountId}\nNear Balance : ${NearBalanceUser}\nTrạng thái : Claim sau ${delayInHours} giờ ${randomMinutes} phút...`,
    });
    await delay(totalDelay);
  } catch (error) {
    twisters.put(accountId, {
      text: `Account ID : ${accountId}\nNear Balance : Error ${error.message}...`,
    });
    await delay(5000);
  }
};


const processAccount = async (accountId, seedPhrase, delayInHours) => {
  while (true) {
    await mineAndUpdate(accountId, seedPhrase, delayInHours);
  }
};

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

(async () => {
  const allPromise = acc.map((account) => {
    const [accountId, seedPhrase, delayInHours] = account.split("|");
    return processAccount(accountId, seedPhrase, parseFloat(delayInHours));
  });

  await Promise.all(allPromise);
})();
