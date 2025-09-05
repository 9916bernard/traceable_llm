const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("LLMVerification", function () {
  let llmVerification;
  let owner;
  let addr1;
  let addr2;

  beforeEach(async function () {
    // 계정 가져오기
    [owner, addr1, addr2] = await ethers.getSigners();

    // 컨트랙트 배포
    const LLMVerification = await ethers.getContractFactory("LLMVerification");
    llmVerification = await LLMVerification.deploy();
    await llmVerification.waitForDeployment();
  });

  describe("배포", function () {
    it("올바른 소유자로 배포되어야 함", async function () {
      expect(await llmVerification.owner()).to.equal(owner.address);
    });

    it("초기 통계가 0이어야 함", async function () {
      const stats = await llmVerification.getStats();
      expect(stats[0]).to.equal(0); // totalHashes
      expect(stats[1]).to.equal(0); // totalVerifications
    });
  });

  describe("해시 저장", function () {
    const testHash = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456";
    const testTimestamp = Math.floor(Date.now() / 1000);

    it("유효한 해시를 저장할 수 있어야 함", async function () {
      await expect(llmVerification.storeHash(testHash, testTimestamp))
        .to.emit(llmVerification, "HashStored")
        .withArgs(testHash, testTimestamp, owner.address, await ethers.provider.getBlockNumber());

      const stats = await llmVerification.getStats();
      expect(stats[0]).to.equal(1);
    });

    it("해시 존재 여부를 확인할 수 있어야 함", async function () {
      await llmVerification.storeHash(testHash, testTimestamp);
      
      const exists = await llmVerification.hashExists(testHash);
      expect(exists).to.be.true;
    });

    it("해시 정보를 조회할 수 있어야 함", async function () {
      await llmVerification.storeHash(testHash, testTimestamp);
      
      const record = await llmVerification.getHashRecord(testHash);
      expect(record.hash).to.equal(testHash);
      expect(record.timestamp).to.equal(testTimestamp);
      expect(record.submitter).to.equal(owner.address);
      expect(record.exists).to.be.true;
    });

    it("중복 해시 저장을 방지해야 함", async function () {
      await llmVerification.storeHash(testHash, testTimestamp);
      
      await expect(
        llmVerification.storeHash(testHash, testTimestamp + 100)
      ).to.be.revertedWith("Hash already exists");
    });

    it("잘못된 길이의 해시를 거부해야 함", async function () {
      const invalidHash = "invalid";
      
      await expect(
        llmVerification.storeHash(invalidHash, testTimestamp)
      ).to.be.revertedWith("Invalid hash length");
    });

    it("잘못된 타임스탬프를 거부해야 함", async function () {
      await expect(
        llmVerification.storeHash(testHash, 0)
      ).to.be.revertedWith("Invalid timestamp");
    });
  });

  describe("해시 검증", function () {
    const testHash = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456";
    const testTimestamp = Math.floor(Date.now() / 1000);

    beforeEach(async function () {
      await llmVerification.storeHash(testHash, testTimestamp);
    });

    it("존재하는 해시를 검증할 수 있어야 함", async function () {
      const [exists, timestamp, submitter] = await llmVerification.verifyHash(testHash);
      
      expect(exists).to.be.true;
      expect(timestamp).to.equal(testTimestamp);
      expect(submitter).to.equal(owner.address);
    });

    it("존재하지 않는 해시 검증 시 false를 반환해야 함", async function () {
      const nonExistentHash = "b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567";
      
      const [exists, timestamp, submitter] = await llmVerification.verifyHash(nonExistentHash);
      
      expect(exists).to.be.false;
      expect(timestamp).to.equal(0);
      expect(submitter).to.equal(ethers.ZeroAddress);
    });
  });

  describe("해시 목록 조회", function () {
    const hashes = [
      "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
      "b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567",
      "c3d4e5f6789012345678901234567890abcdef1234567890abcdef12345678"
    ];

    beforeEach(async function () {
      for (let i = 0; i < hashes.length; i++) {
        await llmVerification.storeHash(hashes[i], Math.floor(Date.now() / 1000) + i);
      }
    });

    it("제출된 해시 목록을 조회할 수 있어야 함", async function () {
      const [retrievedHashes, total] = await llmVerification.getSubmittedHashes(0, 10);
      
      expect(total).to.equal(3);
      expect(retrievedHashes.length).to.equal(3);
      expect(retrievedHashes[0]).to.equal(hashes[0]);
      expect(retrievedHashes[1]).to.equal(hashes[1]);
      expect(retrievedHashes[2]).to.equal(hashes[2]);
    });

    it("페이지네이션으로 해시 목록을 조회할 수 있어야 함", async function () {
      const [retrievedHashes, total] = await llmVerification.getSubmittedHashes(1, 2);
      
      expect(total).to.equal(3);
      expect(retrievedHashes.length).to.equal(2);
      expect(retrievedHashes[0]).to.equal(hashes[1]);
      expect(retrievedHashes[1]).to.equal(hashes[2]);
    });

    it("범위를 벗어난 페이지네이션 요청을 처리해야 함", async function () {
      const [retrievedHashes, total] = await llmVerification.getSubmittedHashes(10, 5);
      
      expect(total).to.equal(3);
      expect(retrievedHashes.length).to.equal(0);
    });
  });

  describe("소유자 기능", function () {
    it("소유자만 출금할 수 있어야 함", async function () {
      // 컨트랙트에 ETH 전송
      await owner.sendTransaction({
        to: await llmVerification.getAddress(),
        value: ethers.parseEther("1.0")
      });

      const initialBalance = await ethers.provider.getBalance(owner.address);
      
      await llmVerification.withdraw(ethers.parseEther("0.5"));
      
      const finalBalance = await ethers.provider.getBalance(owner.address);
      expect(finalBalance).to.be.gt(initialBalance);
    });

    it("비소유자는 출금할 수 없어야 함", async function () {
      await expect(
        llmVerification.connect(addr1).withdraw(ethers.parseEther("0.1"))
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });

    it("소유권을 이전할 수 있어야 함", async function () {
      await llmVerification.transferOwnership(addr1.address);
      expect(await llmVerification.owner()).to.equal(addr1.address);
    });

    it("비소유자는 소유권을 이전할 수 없어야 함", async function () {
      await expect(
        llmVerification.connect(addr1).transferOwnership(addr2.address)
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });
  });

  describe("ETH 수신", function () {
    it("컨트랙트가 ETH를 수신할 수 있어야 함", async function () {
      const amount = ethers.parseEther("1.0");
      
      await expect(
        owner.sendTransaction({
          to: await llmVerification.getAddress(),
          value: amount
        })
      ).to.not.be.reverted;

      const balance = await ethers.provider.getBalance(await llmVerification.getAddress());
      expect(balance).to.equal(amount);
    });
  });

  describe("통계", function () {
    it("통계 정보를 올바르게 반환해야 함", async function () {
      const testHash = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456";
      const testTimestamp = Math.floor(Date.now() / 1000);

      await llmVerification.storeHash(testHash, testTimestamp);
      
      const stats = await llmVerification.getStats();
      expect(stats[0]).to.equal(1); // totalHashes
      expect(stats[1]).to.equal(0); // totalVerifications
    });
  });
});
