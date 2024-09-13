
import { WalletAdapterNetwork } from  "@solana/wallet-adapter-base"
import { SolflareWalletAdapter } from "@solana/wallet-adapter-solflare"
import { greeter } from "./thing.ts"
import { clusterApiUrl } from "@solana/web3"

async function main() : Promise<String> {
    let net = WalletAdapterNetwork.Devnet
    let adapter: SolflareWalletAdapter = await new SolflareWalletAdapter({network: net})

    let conn = await adapter.connect()
    let identity = await adapter.publicKey;

    // let c =  await adapter.connect()

    console.log(identity)
    document.body.innerHTML += `<b>${identity}</b>`
    greeter()

    return `connected to ${identity}`
}

window.onload = () => {
    main().then(console.log)
}