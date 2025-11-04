const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Sepolia Testnet에 LLM Verification Contract 배포를 시작합니다...");

  // 네트워크 확인
  const network = await ethers.provider.getNetwork();
  if (network.chainId !== 11155111n) {
    console.error("❌ 이 스크립트는 Sepolia testnet (Chain ID: 11155111)에서만 실행할 수 있습니다.");
    console.error(`현재 네트워크: ${network.name} (Chain ID: ${network.chainId})`);
    process.exit(1);
  }

  // 배포자 정보
  const [deployer] = await ethers.getSigners();
  console.log(`👤 배포자 주소: ${deployer.address}`);
  
  // 배포자 잔액 확인
  const balance = await ethers.provider.getBalance(deployer.address);
  const balanceInEth = ethers.formatEther(balance);
  console.log(`💰 배포자 잔액: ${balanceInEth} ETH`);
  
  // 최소 잔액 확인 (0.01 ETH)
  if (parseFloat(balanceInEth) < 0.01) {
    console.warn("⚠️  잔액이 부족할 수 있습니다. Sepolia faucet에서 ETH를 받으세요:");
    console.warn("   - https://sepoliafaucet.com/");
    console.warn("   - https://faucet.sepolia.dev/");
    console.warn("   - https://sepolia-faucet.pk910.de/");
  }

  // 컨트랙트 팩토리 가져오기
  const LLMVerification = await ethers.getContractFactory("LLMVerification");

  // 컨트랙트 배포
  console.log("\n📝 컨트랙트를 Sepolia에 배포하는 중...");
  const llmVerification = await LLMVerification.deploy();

  // 배포 완료 대기
  await llmVerification.waitForDeployment();

  const contractAddress = await llmVerification.getAddress();
  console.log("\n✅ LLM Verification Contract가 Sepolia에 성공적으로 배포되었습니다!");
  console.log(`📍 컨트랙트 주소: ${contractAddress}`);

  // 네트워크 정보 출력
  console.log(`🌐 네트워크: Sepolia Testnet (Chain ID: ${network.chainId})`);

  // 컨트랙트 초기 상태 확인
  console.log("\n📊 컨트랙트 초기 상태:");
  const stats = await llmVerification.getStats();
  console.log(`   - 총 해시 개수: ${stats[0]}`);
  console.log(`   - 총 검증 횟수: ${stats[1]}`);
  console.log(`   - 컨트랙트 잔액: ${ethers.formatEther(stats[2])} ETH`);

  // 환경 변수 설정 안내
  console.log("\n🔧 다음 환경 변수를 설정해주세요:");
  console.log(`CONTRACT_ADDRESS=${contractAddress}`);
  console.log(`NETWORK_CHAIN_ID=${network.chainId}`);

  // Etherscan 검증 명령어
  console.log("\n🔍 Etherscan 검증을 위해 다음 명령어를 실행하세요:");
  console.log(`npx hardhat verify --network sepolia ${contractAddress}`);

  // Sepolia 전용 정보
  console.log("\n🌐 Sepolia Testnet 정보:");
  console.log(`   - Explorer: https://sepolia.etherscan.io/address/${contractAddress}`);
  console.log("   - Faucet: https://sepoliafaucet.com/");
  console.log("   - 네트워크 이름: Sepolia");
  console.log("   - RPC URL: https://sepolia.infura.io/v3/YOUR_PROJECT_ID");

  // 테스트 안내
  console.log("\n🧪 테스트 방법:");
  console.log("1. 컨트랙트에 해시 저장:");
  console.log(`   await llmVerification.storeHash("test-hash-123", ${Math.floor(Date.now() / 1000)})`);
  console.log("2. 해시 검증:");
  console.log('   await llmVerification.verifyHash("test-hash-123")');

  return {
    contractAddress,
    network: "sepolia",
    chainId: network.chainId.toString(),
    deployer: deployer.address,
    explorerUrl: `https://sepolia.etherscan.io/address/${contractAddress}`
  };
}

// 에러 처리
main()
  .then((result) => {
    console.log("\n🎉 Sepolia 배포가 완료되었습니다!");
    console.log(`🔗 컨트랙트 확인: ${result.explorerUrl}`);
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n❌ Sepolia 배포 중 오류가 발생했습니다:");
    console.error(error);
    process.exit(1);
  });
