import { KeyPair, keyStores, connect, Near } from "near-api-js";
import { parseSeedPhrase } from "near-seed-phrase";
import BigNumber from "bignumber.js";

export const mainnetConfig = {
  networkId: "mainnet",
  nodeUrl: 'https://rpc.mainnet.near.org',
  walletUrl: "https://wallet.mainnet.near.org",
  helperUrl: "https://helper.mainnet.near.org",
};

import { acc } from "./account2.js";

const near = new Near(mainnetConfig);

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

const sendNear = async (senderAccountId, senderSeedPhrase, recipientAccountId, amount) => {
  try {
    const senderAccount = await getAccount(senderAccountId, senderSeedPhrase);

    const amountYocto = new BigNumber(amount).multipliedBy(1e24).toFixed();

    const result = await senderAccount.sendMoney(recipientAccountId, amountYocto);

    console.log(`Gửi ${amount} NEAR từ ${senderAccountId} tới ${recipientAccountId} thành công. Transaction ID: ${result.transaction.hash}`);
  } catch (error) {
    console.error(`Lỗi khi gửi NEAR từ ${senderAccountId} tới ${recipientAccountId}: ${error.message}`);
  }
};

const processSendingNear = async () => {
  const senderAccountId = "example.near"; 
  const senderSeedPhrase = "seed phrase";
  const amountToSend = 0.02; //so near can gui

  for (const account of acc) {
    const [recipientAccountId, ,] = account.split("|");
    await sendNear(senderAccountId, senderSeedPhrase, recipientAccountId, amountToSend);
  }
};

processSendingNear();
