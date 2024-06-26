import { Near, NearConfig } from './near';
export interface ConnectConfig extends NearConfig {
    /**
     * Initialize an {@link InMemoryKeyStore} by reading the file at keyPath.
     */
    keyPath?: string;
}
/**
 * Initialize connection to Near network.
 * @param config The configuration object for connecting to NEAR Protocol.
 * @returns A Promise that resolves to a `Near` object representing the connection.
 *
 * @example
 * ```js
 * const connectionConfig = {
 *   networkId: 'testnet',
 *   nodeUrl: 'https://rpc.testnet.near.org',
 *   walletUrl: 'https://wallet.testnet.near.org',
 *   helperUrl: 'https://helper.testnet.near.org',
 *   keyStore: new InMemoryKeyStore(),
 *   deps: { keyStore: new BrowserLocalStorageKeyStore() },
 *   logger: true,
 *   keyPath: '/path/to/account-key.json',
 *   masterAccount: 'master-account.near',
 * };
 *
 * const nearConnection = await connect(connectionConfig);
 * console.log(nearConnection); // Near object representing the connection
 * ```
 */
export declare function connect(config: ConnectConfig): Promise<Near>;
