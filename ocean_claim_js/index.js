var request = require('request');
const crypto = require('crypto-js');
const sui = require("@mysten/sui.js");
const colors = require('colors');
const fs = require('fs');
const Ed25519Keypair = sui.Ed25519Keypair
const JsonRpcProvider = sui.JsonRpcProvider
const RawSigner = sui.RawSigner
const TransactionBlock = sui.TransactionBlock
const Connection = sui.Connection

const contractAddress = "0x2c68443db9e8c813b194010c11040a3ce59f47e4eb97a2ec805371505dad7459"
const So = "0x4846a1f1030deffd9dea59016402d832588cf7e0c27b9e4c1a63d2b5e152873a"
const oceanCt = "0xa8816d3a6e3136e86bc2873b1f94a15cadc8af2703c075f2d546c2ae367f4df9::ocean::OCEAN" 
const walletKeys = fs.readFileSync('wallets.txt', 'utf-8')
  .split('\n')
  .map(line => line.trim())
  .filter(Boolean);

const connection = new Connection({
  fullnode: 'https://fullnode.mainnet.sui.io',
  faucet: 'https://faucet.testnet.sui.io/gas',
});
const provider = new JsonRpcProvider(connection);

function sleep(millis) {
  return new Promise(resolve => setTimeout(resolve, millis));
}
function shortenKey(key) {
  const start = key.slice(0, 4);
  const end = key.slice(-4);
  return `${start}...${end}`;
}
async function getChange(key) {
  const txn = await provider.getTransactionBlock({
    digest: key,
    options: {
      showEffects: false,
      showInput: false,
      showEvents: false,
      showObjectChanges: true,
      showBalanceChanges: true,
    },
  });
  let change = txn["balanceChanges"]
  const totalAmount = change
    .filter(item => item.coinType === oceanCt)
    .reduce((sum, item) => sum + parseInt(item.amount, 10), 0);
  return totalAmount/1000000000
}

async function main() {   
  for (var i = 0; i < walletKeys.length; i++) {
    const key = walletKeys[i];      
    const keypair = Ed25519Keypair.deriveKeypair(key, `m/44'/784'/0'/0'/0'`);
    console.log(`================Bắt đầu đọc ví ${shortenKey(key)}===================`.yellow.bold);
    
    const signer = new RawSigner(keypair, provider);
    const suiAdd = keypair.getPublicKey().toSuiAddress();
    console.log(`->Sui Address: ${suiAdd}`);
    
    try {
      const tx = new TransactionBlock();
      let a = tx.object(So);
      let d = tx.object("0x6");
      tx.moveCall({
        target: `${contractAddress}::game::claim`,
        arguments: [a, d],
        typeArguments: []
      });
      console.log('->Bắt đầu claim, chờ đợi...');
      
      const result = await signer.signAndExecuteTransactionBlock({ transactionBlock: tx, requestType: "WaitForLocalExecution" });
      
      await sleep(5000);
      let amount = await getChange(result["digest"]);
      const currentDate = new Date();
      const dateNow = currentDate.toISOString();
      console.log(`->${suiAdd} đã claim: ${dateNow}, Balance: ${amount}`.green.bold);
    } catch (error) {
      console.error(`->Claim Error, chưa đến giờ: ${suiAdd}\n`.blue.bold);
    }
  }
}


const countDown = async (seconds) => {
  const milliseconds = seconds * 1000;
  let remainingTime = milliseconds;

  while (remainingTime > 0) {
    process.stdout.write(`\rClaim again in ${remainingTime / 1000} seconds`.magenta.bold);
    await sleep(1000); // Đợi 1 giây
    remainingTime -= 1000;
  }

  process.stdout.write(`\rClaim again in 0 seconds\n`.magenta.bold);
  // Thực hiện công việc gì đó sau khi đếm ngược kết thúc
};

async function run() {
  while (true) { 
    try {
      await main();
    } catch (error) {
      console.error('Lỗi trong quá trình thực hiện:', error);
    }
    const nghingoi =  10*60 ; // 2 giờ * 60 phút * 60 giây * 1000 ms
	await countDown(nghingoi);
    //await sleep(nghingoi);
  }
}

run()


  

