// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Minimal registry to store document/transaction fingerprints (hashes).
// Do NOT store personal data or full documents.
contract AriaryRegistry {
    event Recorded(bytes32 indexed hash, address indexed sender, uint256 timestamp);

    mapping(bytes32 => bool) public exists;

    function record(bytes32 h) external {
        require(!exists[h], "Already recorded");
        exists[h] = true;
        emit Recorded(h, msg.sender, block.timestamp);
    }

    function verify(bytes32 h) external view returns (bool) {
        return exists[h];
    }
}
