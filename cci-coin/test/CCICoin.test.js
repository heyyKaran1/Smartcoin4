const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CCICoin", function () {
  let cciCoin;
  let owner;
  let addr1;
  let addr2;
  const TOTAL_SUPPLY = ethers.parseUnits("1000000000", 18);

  beforeEach(async function () {
    [owner, addr1, addr2] = await ethers.getSigners();

    const CCICoin = await ethers.getContractFactory("CCICoin");
    cciCoin = await CCICoin.deploy(owner.address);
    await cciCoin.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should set the correct name and symbol", async function () {
      expect(await cciCoin.name()).to.equal("CCI Coin");
      expect(await cciCoin.symbol()).to.equal("CCI");
    });

    it("Should have 18 decimals", async function () {
      expect(await cciCoin.decimals()).to.equal(18);
    });

    it("Should mint total supply to deployer", async function () {
      const ownerBalance = await cciCoin.balanceOf(owner.address);
      expect(ownerBalance).to.equal(TOTAL_SUPPLY);
    });

    it("Should have correct total supply", async function () {
      expect(await cciCoin.totalSupply()).to.equal(TOTAL_SUPPLY);
    });

    it("Should set the correct owner", async function () {
      expect(await cciCoin.owner()).to.equal(owner.address);
    });
  });

  describe("Transactions", function () {
    it("Should transfer tokens between accounts", async function () {
      const transferAmount = ethers.parseUnits("100", 18);

      await cciCoin.transfer(addr1.address, transferAmount);
      expect(await cciCoin.balanceOf(addr1.address)).to.equal(transferAmount);

      await cciCoin.connect(addr1).transfer(addr2.address, transferAmount);
      expect(await cciCoin.balanceOf(addr2.address)).to.equal(transferAmount);
      expect(await cciCoin.balanceOf(addr1.address)).to.equal(0);
    });

    it("Should fail if sender doesn't have enough tokens", async function () {
      const initialOwnerBalance = await cciCoin.balanceOf(owner.address);
      const excessiveAmount = initialOwnerBalance + ethers.parseUnits("1", 18);

      await expect(
        cciCoin.connect(addr1).transfer(owner.address, excessiveAmount)
      ).to.be.reverted;

      expect(await cciCoin.balanceOf(owner.address)).to.equal(initialOwnerBalance);
    });

    it("Should update balances after transfers", async function () {
      const initialOwnerBalance = await cciCoin.balanceOf(owner.address);
      const transferAmount1 = ethers.parseUnits("100", 18);
      const transferAmount2 = ethers.parseUnits("50", 18);

      await cciCoin.transfer(addr1.address, transferAmount1);
      await cciCoin.transfer(addr2.address, transferAmount2);

      const finalOwnerBalance = await cciCoin.balanceOf(owner.address);
      expect(finalOwnerBalance).to.equal(initialOwnerBalance - transferAmount1 - transferAmount2);

      expect(await cciCoin.balanceOf(addr1.address)).to.equal(transferAmount1);
      expect(await cciCoin.balanceOf(addr2.address)).to.equal(transferAmount2);
    });
  });

  describe("Allowances", function () {
    it("Should approve tokens for delegated transfer", async function () {
      const approveAmount = ethers.parseUnits("100", 18);

      await cciCoin.approve(addr1.address, approveAmount);
      expect(await cciCoin.allowance(owner.address, addr1.address)).to.equal(approveAmount);
    });

    it("Should allow delegated transfers with transferFrom", async function () {
      const approveAmount = ethers.parseUnits("100", 18);
      const transferAmount = ethers.parseUnits("50", 18);

      await cciCoin.approve(addr1.address, approveAmount);
      await cciCoin.connect(addr1).transferFrom(owner.address, addr2.address, transferAmount);

      expect(await cciCoin.balanceOf(addr2.address)).to.equal(transferAmount);
      expect(await cciCoin.allowance(owner.address, addr1.address)).to.equal(approveAmount - transferAmount);
    });

    it("Should fail transferFrom without sufficient allowance", async function () {
      const transferAmount = ethers.parseUnits("100", 18);

      await expect(
        cciCoin.connect(addr1).transferFrom(owner.address, addr2.address, transferAmount)
      ).to.be.reverted;
    });

    it("Should fail transferFrom exceeding allowance", async function () {
      const approveAmount = ethers.parseUnits("50", 18);
      const transferAmount = ethers.parseUnits("100", 18);

      await cciCoin.approve(addr1.address, approveAmount);

      await expect(
        cciCoin.connect(addr1).transferFrom(owner.address, addr2.address, transferAmount)
      ).to.be.reverted;
    });
  });

  describe("Ownership", function () {
    it("Should allow owner to transfer ownership", async function () {
      await cciCoin.transferOwnership(addr1.address);
      expect(await cciCoin.owner()).to.equal(addr1.address);
    });

    it("Should prevent non-owners from transferring ownership", async function () {
      await expect(
        cciCoin.connect(addr1).transferOwnership(addr2.address)
      ).to.be.reverted;
    });

    it("Should allow owner to renounce ownership", async function () {
      await cciCoin.renounceOwnership();
      expect(await cciCoin.owner()).to.equal(ethers.ZeroAddress);
    });
  });
});
