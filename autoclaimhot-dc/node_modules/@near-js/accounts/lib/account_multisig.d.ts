import { Action } from '@near-js/transactions';
import { FinalExecutionOutcome } from '@near-js/types';
import { Account, SignAndSendTransactionOptions } from './account';
import { Connection } from './connection';
import { MultisigStateStatus } from './types';
declare enum MultisigCodeStatus {
    INVALID_CODE = 0,
    VALID_CODE = 1,
    UNKNOWN_CODE = 2
}
export declare class AccountMultisig extends Account {
    storage: any;
    onAddRequestResult: (any: any) => any;
    /**
     * Constructs an instance of the `AccountMultisig` class.
     * @param connection The NEAR connection object.
     * @param accountId The NEAR account ID.
     * @param options Additional options for the multisig account.
     * @param options.storage Storage to store data related to multisig operations.
     * @param options.onAddRequestResult Callback function to handle the result of adding a request.
     */
    constructor(connection: Connection, accountId: string, options: any);
    /**
     * Sign and send a transaction with the multisig account as the sender.
     * @param receiverId - The NEAR account ID of the transaction receiver.
     * @param actions - The list of actions to be included in the transaction.
     * @returns {Promise<FinalExecutionOutcome>} A promise that resolves to the final execution outcome of the transaction.
     */
    signAndSendTransactionWithAccount(receiverId: string, actions: Action[]): Promise<FinalExecutionOutcome>;
    /**
     * Sign and send a multisig transaction to add a request and confirm it.
     * @param options Options for the multisig transaction.
     * @param options.receiverId The NEAR account ID of the transaction receiver.
     * @param options.actions The list of actions to be included in the transaction.
     * @returns {Promise<FinalExecutionOutcome>} A promise that resolves to the final execution outcome of the transaction.
     */
    signAndSendTransaction({ receiverId, actions }: SignAndSendTransactionOptions): Promise<FinalExecutionOutcome>;
    /**
     * This method submits a canary transaction that is expected to always fail in order to determine whether the contract currently has valid multisig state
     * and whether it is initialized. The canary transaction attempts to delete a request at index u32_max and will go through if a request exists at that index.
     * a u32_max + 1 and -1 value cannot be used for the canary due to expected u32 error thrown before deserialization attempt.
     * @param contractBytes The bytecode of the multisig contract.
     * @returns {Promise<{ codeStatus: MultisigCodeStatus; stateStatus: MultisigStateStatus }>} A promise that resolves to the status of the code and state.
     */
    checkMultisigCodeAndStateStatus(contractBytes?: Uint8Array): Promise<{
        codeStatus: MultisigCodeStatus;
        stateStatus: MultisigStateStatus;
    }>;
    /**
     * Delete a multisig request by its ID.
     * @param request_id The ID of the multisig request to be deleted.
     * @returns {Promise<FinalExecutionOutcome>} A promise that resolves to the final execution outcome of the deletion.
     */
    deleteRequest(request_id: any): Promise<FinalExecutionOutcome>;
    /**
     * Delete all multisig requests associated with the account.
     * @returns {Promise<void>} A promise that resolves when all requests are deleted.
     */
    deleteAllRequests(): Promise<void>;
    /**
     * Delete unconfirmed multisig requests associated with the account.
     * @returns {Promise<void>} A promise that resolves when unconfirmed requests are deleted.
     */
    deleteUnconfirmedRequests(): Promise<void>;
    getRequestIds(): Promise<string[]>;
    getRequest(): any;
    setRequest(data: any): any;
}
export {};
//# sourceMappingURL=account_multisig.d.ts.map