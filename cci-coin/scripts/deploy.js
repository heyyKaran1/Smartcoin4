const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();

  console.log("Deploying CCI Coin with account:", deployer.address);
  console.log("Account balance:", (await hre.ethers.provider.getBalance(deployer.address)).toString());

  const CCICoin = await hre.ethers.getContractFactory("CCICoin");
  const cciCoin = await CCICoin.deploy(deployer.address);

  await cciCoin.waitForDeployment();

  const contractAddress = await cciCoin.getAddress();

  console.log("\n✅ CCI Coin deployed successfully!");
  console.log("📍 Contract Address:", contractAddress);
  console.log("🪙 Token Name:", await cciCoin.name());
  console.log("🔤 Symbol:", await cciCoin.symbol());
  console.log("💰 Total Supply:", hre.ethers.formatUnits(await cciCoin.totalSupply(), 18), "CCI");
  console.log("👤 Owner:", await cciCoin.owner());
  console.log("\n📋 Save this contract address for frontend integration!");
  console.log("\nNetwork:", hre.network.name);

  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("\nWaiting for block confirmations...");
    await cciCoin.deploymentTransaction().wait(6);
    console.log("\n✅ Contract verified on blockchain");
    console.log("\n📝 To verify on block explorer, run:");
    console.log(`npx hardhat verify --network ${hre.network.name} ${contractAddress} "${deployer.address}"`);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
