// Fleet NFT Contract (TEP-62)
// For T4-T5 ships only. T1-T3 remain off-chain.
//
// Collection contract that mints NFT items for eligible ships.
// Each NFT represents ownership of a high-tier ship.

import "@stdlib/ownable";

struct NftItemData {
    index: Int;
    collection: Address;
    owner: Address;
    content: Cell;
}

contract FleetNFT with Ownable {
    nextItemIndex: Int as nextItemIndex;
    collectionContent: Cell as collectionContent;
    commonContentPrefix: Cell as commonContentPrefix;
    royaltyParams: Cell as royaltyParams;
    owner: Address as owner;

    const ROYALTY_PERCENT: Int = 3; // 3% royalty to creator

    init(owner: Address, collectionContent: Cell, commonContentPrefix: Cell) {
        self.nextItemIndex = 0;
        self.owner = owner;
        self.collectionContent = collectionContent;
        self.commonContentPrefix = commonContentPrefix;
    }

    // Mint a new Fleet NFT (T4-T5 ship)
    receive(msg: MintFleetNFT) {
        let itemIndex: Int = self.nextItemIndex;
        self.nextItemIndex = itemIndex + 1;

        // Deploy new NFT item contract
        let nftItem: Address = deployNFTItem(
            index: itemIndex,
            owner: msg.owner,
            content: msg.shipContent
        );
    }

    receive("get_collection_data") {
        self.reply(NftCollectionData {
            nextItemIndex: self.nextItemIndex,
            collectionContent: self.collectionContent,
            owner: self.owner,
        });
    }

    receive("get_nft_address_by_index") {
        // Returns address of NFT item by index
    }
}
