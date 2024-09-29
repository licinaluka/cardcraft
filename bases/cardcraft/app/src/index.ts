
import bs58 from "bs58"
import { Buffer } from 'buffer'
import { WalletAdapterNetwork, BaseMessageSignerWalletAdapter } from "@solana/wallet-adapter-base"
import { SolflareWalletAdapter } from "@solana/wallet-adapter-solflare"
import { clusterApiUrl } from "@solana/web3"
import { Connection, LAMPORTS_PER_SOL, PublicKey, SystemProgram, Transaction } from "@solana/web3.js"

import { greeter } from "./thing.ts"

type AuthnChallenge {
    cid: number
    message: string
}

class Purse {
    wallet?: BaseMessageSignerWalletAdapter

    btn: Element | null

    constructor() {
        this.btn = document.querySelector("#connection")
    }

    /** */
    async connect(net?: WalletAdapterNetwork = WalletAdapterNetwork.Devnet): Promise<void> {
        this.wallet = await new SolflareWalletAdapter({ network: net })
        await this.wallet.connect()

        if (this.btn) {
            this.btn.setAttribute("onclick", "window.purse.signIn()")
            this.btn.innerHTML = "sign in o/"
        }
    }

    /** */
    identity(): PublicKey | null {
        if (!this.wallet) {
            throw 'Wallet not connected!'
        }

        return this.wallet?.publicKey;
    }

    /** */
    async sign(message: string): Promise<string> {
        let b: Uint8Array = bs58.decode(message)
        let signed: Uint8Array | undefined = await this.wallet?.signMessage(b)
        if (!signed) {
            throw 'Failed to sign message!'
        }

        return bs58.encode(signed)
    }

    /** 
    *
    */
    async signIn() {
        // exchange nonces with the server
        let nonce = bs58.encode(crypto.getRandomValues(new Uint8Array(Array.from({ length: 12 }))))

        // obtain login challenge
        let resp = await fetch(
            '/api/part/game/authn/challenge',
            {
                credentials: "same-origin",
                method: 'POST',
                body: JSON.stringify({
                    nonce: nonce,
                    key: this.identity()
                }),
                headers: {
                    "Content-type": "application/json"
                }
            }
        )

        // check if already logged in
        if (resp.status == 302) {
            return null
        }

        let challenge: AuthnChallenge = await resp.json()

        // sign login challenge
        let signature: string = await this.sign(challenge.message)

        // send back to server, set-cookie response header will assign a session
        await fetch(
            '/api/part/game/authn',
            {
                credentials: "same-origin",
                method: 'POST',
                body: JSON.stringify({
                    nonce: nonce,
                    challenge: challenge.cid,
                    signature: signature
                }),
                headers: {
                    "Content-type": "application/json"
                }
            }
        )

        if (this.btn) {
            let trunc: string = this.identity()?.toString().substring(0, 7)
            this.btn.innerHTML = `${trunc}...`
        }
    }

    /** */
    async pot(escrow: string, lamports: number): Promise<string> {
        await this.connect()

        console.log(lamports)

        let temp = this.identity()
        if (!temp) {
            throw 'Wallet not connected!'
        }

        let identity: PublicKey = temp
        let connection: Connection = new Connection("https://api.devnet.solana.com", "confirmed")
        let txSigField: Element | null = document.querySelector('input[name=txsig')

        if (!txSigField) {
            throw 'Cannot find txsig field!'
        }

        try {
            const transaction = new Transaction()
            const sendSolInstruction = SystemProgram.transfer({
                fromPubkey: identity,
                toPubkey: new PublicKey(escrow),
                lamports: lamports,
            })

            transaction.add(sendSolInstruction)

            let signature: string | undefined = await this.wallet?.sendTransaction(transaction, connection)
            document.cookie = `'txsig=${signature};max-age=60`

            txSigField.value = signature
        } catch (error) {
            console.error("Transaction failed", error);
        }

    }
}

globalThis.Buffer = Buffer
window.purse = new Purse()