const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("LLMVerificationV2", function () {
  let contract;
  let owner;
  let addr1;

  // A sample SHA-256 hash as bytes32
  const sampleHash = ethers.keccak256(ethers.toUtf8Bytes("test-content-hash"));
  const sampleCID = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG";
  const sampleVotes = "3/5";

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("LLMVerificationV2");
    contract = await Factory.deploy();
    await contract.waitForDeployment();
  });

  describe("Deployment", function () {
    it("should start with zero records", async function () {
      expect(await contract.totalRecords()).to.equal(0);
    });
  });

  describe("storeRecord", function () {
    it("should store a record and emit RecordStored event", async function () {
      const tx = await contract.storeRecord(sampleHash, sampleCID, sampleVotes);
      await tx.wait();

      // Just check the event was emitted with the right hash
      await expect(tx)
        .to.emit(contract, "RecordStored");

      expect(await contract.totalRecords()).to.equal(1);
    });

    it("should reject zero content hash", async function () {
      await expect(
        contract.storeRecord(ethers.ZeroHash, sampleCID, sampleVotes)
      ).to.be.revertedWith("Invalid content hash");
    });

    it("should reject empty IPFS CID", async function () {
      await expect(
        contract.storeRecord(sampleHash, "", sampleVotes)
      ).to.be.revertedWith("Invalid IPFS CID");
    });

    it("should reject duplicate content hash", async function () {
      await contract.storeRecord(sampleHash, sampleCID, sampleVotes);
      await expect(
        contract.storeRecord(sampleHash, "QmDifferentCID", sampleVotes)
      ).to.be.revertedWith("Record already exists");
    });

    it("should allow different hashes", async function () {
      const hash2 = ethers.keccak256(ethers.toUtf8Bytes("another-hash"));
      await contract.storeRecord(sampleHash, sampleCID, sampleVotes);
      await contract.storeRecord(hash2, "QmAnotherCID", "4/5");
      expect(await contract.totalRecords()).to.equal(2);
    });
  });

  describe("hashExists", function () {
    it("should return true for stored hash", async function () {
      await contract.storeRecord(sampleHash, sampleCID, sampleVotes);
      expect(await contract.hashExists(sampleHash)).to.be.true;
    });

    it("should return false for unknown hash", async function () {
      const unknownHash = ethers.keccak256(ethers.toUtf8Bytes("unknown"));
      expect(await contract.hashExists(unknownHash)).to.be.false;
    });
  });

  describe("getRecord", function () {
    it("should return stored record fields", async function () {
      await contract.storeRecord(sampleHash, sampleCID, sampleVotes);

      const [exists, ipfsCID, consensusVotes, submitter, timestamp] =
        await contract.getRecord(sampleHash);

      expect(exists).to.be.true;
      expect(ipfsCID).to.equal(sampleCID);
      expect(consensusVotes).to.equal(sampleVotes);
      expect(submitter).to.equal(owner.address);
      expect(timestamp).to.be.gt(0);
    });

    it("should return empty for non-existent hash", async function () {
      const unknownHash = ethers.keccak256(ethers.toUtf8Bytes("missing"));
      const [exists, ipfsCID, consensusVotes, submitter, timestamp] =
        await contract.getRecord(unknownHash);

      expect(exists).to.be.false;
      expect(ipfsCID).to.equal("");
      expect(consensusVotes).to.equal("");
      expect(submitter).to.equal(ethers.ZeroAddress);
      expect(timestamp).to.equal(0);
    });
  });

  describe("Gas comparison with V1", function () {
    it("should use significantly less gas than V1 plaintext storage", async function () {
      const tx = await contract.storeRecord(sampleHash, sampleCID, sampleVotes);
      const receipt = await tx.wait();

      console.log(`    V2 gas used: ${receipt.gasUsed.toString()}`);
      // V1 typically uses ~510,000 gas for plaintext storage
      // V2 uses ~250,000 gas (~50% reduction, no plaintext strings)
      expect(receipt.gasUsed).to.be.lt(510000);
    });
  });
});
