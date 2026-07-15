const hre = require("hardhat");

async function main() {
  const contractAddress = process.env.CONTRACT_ADDRESS;
  const ownerAddress = process.env.OWNER_ADDRESS;

  if (!contractAddress || !ownerAddress) {
    console.error("❌ Error: CONTRACT_ADDRESS and OWNER_ADDRESS must be set in .env");
    console.log("\nExample:");
    console.log("CONTRACT_ADDRESS=0x...");
    console.log("OWNER_ADDRESS=0x...");
    process.exit(1);
  }

  console.log("Verifying contract at:", contractAddress);
  console.log("With constructor args:", ownerAddress);

  try {
    await hre.run("verify:verify", {
      address: contractAddress,
      constructorArguments: [ownerAddress],
    });
    console.log("✅ Contract verified successfully!");
  } catch (error) {
    if (error.message.includes("Already Verified")) {
      console.log("✅ Contract is already verified!");
    } else {
      console.error("❌ Verification failed:", error.message);
      process.exit(1);
    }
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
