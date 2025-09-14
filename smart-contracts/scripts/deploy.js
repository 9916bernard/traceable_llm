const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 LLM Verification Contract 배포를 시작합니다...");

  // 컨트랙트 팩토리 가져오기
  const LLMVerification = await ethers.getContractFactory("LLMVerification");

  // 컨트랙트 배포
  console.log("📝 컨트랙트를 배포하는 중...");
  const llmVerification = await LLMVerification.deploy();

  // 배포 완료 대기
  await llmVerification.waitForDeployment();

  const contractAddress = await llmVerification.getAddress();
  console.log("✅ LLM Verification Contract가 성공적으로 배포되었습니다!");
  console.log(`📍 컨트랙트 주소: ${contractAddress}`);

  // 네트워크 정보 출력
  const network = await ethers.provider.getNetwork();
  console.log(`🌐 네트워크: ${network.name} (Chain ID: ${network.chainId})`);

  // 배포자 정보
  const [deployer] = await ethers.getSigners();
  console.log(`👤 배포자: ${deployer.address}`);

  // 배포자 잔액
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log(`💰 배포자 잔액: ${ethers.formatEther(balance)} ETH`);

  // 컨트랙트 초기 상태 확인
  console.log("\n📊 컨트랙트 초기 상태:");
  const stats = await llmVerification.getStats();
  console.log(`   - 총 해시 개수: ${stats[0]}`);
  console.log(`   - 총 검증 횟수: ${stats[1]}`);
  console.log(`   - 컨트랙트 잔액: ${ethers.formatEther(stats[2])} ETH`);

  // 환경 변수 파일 생성 안내
  console.log("\n🔧 다음 환경 변수를 설정해주세요:");
  console.log(`CONTRACT_ADDRESS=${contractAddress}`);
  console.log(`NETWORK_CHAIN_ID=${network.chainId}`);

  // Etherscan 검증 안내 (테스트넷인 경우)
  if (network.chainId === 11155111n || network.chainId === 5n) {
    console.log("\n🔍 Etherscan 검증을 위해 다음 명령어를 실행하세요:");
    console.log(`npx hardhat verify --network ${network.name} ${contractAddress}`);
    
    // Sepolia testnet 전용 안내
    if (network.chainId === 11155111n) {
      console.log("\n🌐 Sepolia Testnet 정보:");
      console.log("   - Explorer: https://sepolia.etherscan.io");
      console.log(`   - Contract: https://sepolia.etherscan.io/address/${contractAddress}`);
      console.log("   - Faucet: https://sepoliafaucet.com/ 또는 https://faucet.sepolia.dev/");
    }
  }

  return {
    contractAddress,
    network: network.name,
    chainId: network.chainId.toString(),
    deployer: deployer.address,
  };
}

// 에러 처리
main()
  .then((result) => {
    console.log("\n🎉 배포가 완료되었습니다!");
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n❌ 배포 중 오류가 발생했습니다:");
    console.error(error);
    process.exit(1);
  });
