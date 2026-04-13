const { ethers } = require("hardhat");

async function main() {
  console.log("Deploying LLMVerificationV2 (hash-only + IPFS) to Sepolia...");

  const network = await ethers.provider.getNetwork();
  if (network.chainId !== 11155111n) {
    console.error(`Wrong network: ${network.name} (Chain ID: ${network.chainId}). Expected Sepolia.`);
    process.exit(1);
  }

  const [deployer] = await ethers.getSigners();
  console.log(`Deployer: ${deployer.address}`);

  const balance = await ethers.provider.getBalance(deployer.address);
  console.log(`Balance: ${ethers.formatEther(balance)} ETH`);

  if (parseFloat(ethers.formatEther(balance)) < 0.01) {
    console.warn("Low balance. Get Sepolia ETH from https://sepoliafaucet.com/");
  }

  const Factory = await ethers.getContractFactory("LLMVerificationV2");
  console.log("Deploying contract...");
  const contract = await Factory.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log(`\nLLMVerificationV2 deployed at: ${address}`);
  console.log(`Explorer: https://sepolia.etherscan.io/address/${address}`);
  console.log(`\nSet this in your .env:`);
  console.log(`CONTRACT_ADDRESS_V2=${address}`);
  console.log(`\nVerify on Etherscan:`);
  console.log(`npx hardhat verify --network sepolia ${address}`);

  return { address, network: "sepolia" };
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Deployment failed:", error);
    process.exit(1);
  });
