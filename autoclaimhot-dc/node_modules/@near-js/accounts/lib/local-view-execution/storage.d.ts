import { BlockHash, BlockReference } from '@near-js/types';
import { ContractState } from './types';
export interface StorageData {
    blockHeight: number;
    blockTimestamp: number;
    contractCode: string;
    contractState: ContractState;
}
export interface StorageOptions {
    max: number;
}
export declare class Storage {
    private readonly cache;
    private static MAX_ELEMENTS;
    private blockHeights;
    constructor(options?: StorageOptions);
    load(blockRef: BlockReference): StorageData | undefined;
    save(blockHash: BlockHash, { blockHeight, blockTimestamp, contractCode, contractState }: StorageData): void;
}
//# sourceMappingURL=storage.d.ts.map