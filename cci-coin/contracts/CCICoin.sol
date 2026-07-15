// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title CCICoin
 * @dev ERC-20 token for CCI Coin Enterprise Platform
 * @notice This contract implements the CCI Coin token with a fixed supply of 1 billion tokens
 */
contract CCICoin is ERC20, Ownable {
    uint256 public constant TOTAL_SUPPLY = 1_000_000_000 * 10**18;

    /**
     * @dev Constructor that mints the entire token supply to the deployer
     * @param initialOwner Address that will receive the total supply and become the contract owner
     */
    constructor(address initialOwner) ERC20("CCI Coin", "CCI") Ownable(initialOwner) {
        _mint(initialOwner, TOTAL_SUPPLY);
    }

    /**
     * @dev Returns the number of decimals used for token amounts
     * @return uint8 Number of decimals (18 - standard ERC-20)
     */
    function decimals() public pure override returns (uint8) {
        return 18;
    }
}
