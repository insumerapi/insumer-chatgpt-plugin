# Review form entries for version 0.2.0

What goes into the review form at platform.openai.com when the package is submitted. The five positive cases are P1 to P5 from `test-cases.md`. The three negative cases are prompts where the plugin must not trigger; they follow the topics entered on 2026-10-02 (the exact wording entered then was not kept).

## Positive cases (the plugin should be used)

1. **Prompt:** Use InsumerAPI to check whether wallet 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 holds at least 1 ETH on Ethereum, and show me the attestation ID and signing key IDs.
   **Tool:** `insumer_attest`
   **Expected:** Reports `met: true`, an attestation ID (`ATST-...`), `kid: insumer-attest-v2`, `pqKid: insumer-attest-pq1`, and the block the state was read at. No balance figure appears.

2. **Prompt:** Use InsumerAPI to check whether the same wallet is a registered ERC-8004 agent with agent ID 1 on Base.
   **Tool:** `insumer_attest`
   **Expected:** Reports `met: false` as a verdict, not as an error, with the attestation ID and key IDs.

3. **Prompt:** Use InsumerAPI to build a wallet trust profile for 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 and summarize each dimension.
   **Tool:** `insumer_wallet_trust`
   **Expected:** Lists the ten dimensions with held and not-held counts, the profile ID (`TRST-...`), `conditionSetVersion`, and `kid: insumer-trust-v2`. No score or ranking.

4. **Prompt:** Use InsumerAPI to list its current signing keys and tell me how an attestation is verified offline.
   **Tool:** `insumer_jwks`
   **Expected:** Names the five key IDs (three ECDSA: `insumer-attest-v1`, `insumer-attest-v2`, `insumer-trust-v2`; two post-quantum: `insumer-attest-pq1`, `insumer-trust-pq1`), says to match keys by `kid`, and points at the `insumer-verify` package.

5. **Prompt:** Use InsumerAPI to look up the merchant "acme-coffee" and tell me what discount wallet 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 would get there.
   **Tools:** `insumer_get_merchant`, then `insumer_check_discount`
   **Expected:** Gives the merchant's name and tiers and the resulting discount percentage, with no balance figure.

## Negative cases (the plugin should not be used)

1. **Prompt:** What is the price of ETH right now?
   **Why not:** Price data. InsumerAPI answers whether a wallet meets a condition; it returns no prices.

2. **Prompt:** Send 0.5 ETH from my wallet to 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045.
   **Why not:** Sending a transaction. InsumerAPI reads wallet state; it never moves funds or signs for a wallet.

3. **Prompt:** I lost my hardware wallet. How do I get my funds back?
   **Why not:** Wallet recovery advice. No on-chain condition is being checked.

## Demo video

https://youtu.be/N0fuqh8RWvE

## Release notes

Version 0.2.0. Adds the insumer-discount skill (a signed discount code at a merchant, through the REST API with your own key). The wallet trust profile is 155 checks across 27 chains in ten dimensions. Adds the account code condition (plain key, EIP-7702 delegation or contract). The bundled skills are updated to match the current API.
