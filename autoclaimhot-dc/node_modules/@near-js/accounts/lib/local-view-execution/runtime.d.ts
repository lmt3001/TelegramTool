/// <reference types="node" />
import { ContractState } from './types';
interface RuntimeCtx {
    contractId: string;
    contractState: ContractState;
    blockHeight: number;
    blockTimestamp: number;
    methodArgs: string;
}
interface RuntimeConstructorArgs extends RuntimeCtx {
    contractCode: string;
}
export declare class Runtime {
    context: RuntimeCtx;
    wasm: Buffer;
    memory: WebAssembly.Memory;
    registers: Record<string, any>;
    logs: any[];
    result: Buffer;
    constructor({ contractCode, ...context }: RuntimeConstructorArgs);
    private readUTF16CStr;
    private readUTF8CStr;
    private storageRead;
    private prepareWASM;
    private getRegisterLength;
    private readFromRegister;
    private getCurrentAccountId;
    private inputMethodArgs;
    private getBlockHeight;
    private getBlockTimestamp;
    private sha256;
    private returnValue;
    private panic;
    private abort;
    private appendToLog;
    private readStorage;
    private hasStorageKey;
    private getHostImports;
    execute(methodName: string): Promise<{
        result: Buffer;
        logs: any[];
    }>;
}
export {};
//# sourceMappingURL=runtime.d.ts.map