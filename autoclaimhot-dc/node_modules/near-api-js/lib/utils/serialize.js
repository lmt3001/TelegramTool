"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.base_decode = exports.base_encode = exports.deserialize = exports.serialize = void 0;
var borsh_1 = require("borsh");
Object.defineProperty(exports, "serialize", { enumerable: true, get: function () { return borsh_1.serialize; } });
Object.defineProperty(exports, "deserialize", { enumerable: true, get: function () { return borsh_1.deserialize; } });
var utils_1 = require("@near-js/utils");
Object.defineProperty(exports, "base_encode", { enumerable: true, get: function () { return utils_1.baseEncode; } });
Object.defineProperty(exports, "base_decode", { enumerable: true, get: function () { return utils_1.baseDecode; } });
