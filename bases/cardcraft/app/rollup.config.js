import typescript from "@rollup/plugin-typescript";
import nodePolyfills from "rollup-plugin-polyfill-node"
import { nodeResolve } from "@rollup/plugin-node-resolve"
import commonjs from "@rollup/plugin-commonjs";
import json from "@rollup/plugin-json";

export default {
    input: "./src/index.ts",
    external: [
        // "fs"
    ],
    output: {
        file: "./resources/app/bundle.js",
        format: "iife",
        name: "thingthing",
        inlineDynamicImports: true,
        globals: {
            "fs": "require$$0$3",
            "path": "require$$0$2",
            "http": "http",
            "https": "https",
            "stream": "Stream$1",
        }
    },
    plugins: [
        typescript(),
        // nodePolyfills({ include: [] }),
        nodeResolve({
            browser: true,
            preferBuiltins: false
        }),
        commonjs(),
        json()
    ]
}