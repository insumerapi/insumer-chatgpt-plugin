# Review form entries for version 0.2.0

What is saved in the review form at platform.openai.com for the 0.2.0 draft (read back from the portal on 2026-10-13). The form keeps its entries across a cancelled review and a new upload. Three positive cases were edited that day: case 1 (expected output), case 3 (ten dimensions) and case 5 (a store that is in the public directory). The three negative cases and the video link are the 2026-10-02 originals, unchanged.

## Positive cases (the plugin should be used)

1. **Prompt:** Use InsumerAPI to check whether wallet 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 holds at least 1 ETH on Ethereum, and show me the attestation ID and signing key IDs.
   **Tool:** `insumer_attest`
   **Expected:** Reports `met: true`, an attestation ID (`ATST-...`), `kid: insumer-attest-v2`, `pqKid: insumer-attest-pq1`. No balance figure appears.

2. **Prompt:** Use InsumerAPI to check whether the same wallet is a registered ERC-8004 agent with agent ID 1 on Base.
   **Tool:** `insumer_attest`
   **Expected:** Reports `met: false` as a verdict, not as an error, with the attestation ID and key IDs.

3. **Prompt:** Use InsumerAPI to build a wallet trust profile for 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 and summarize each dimension.
   **Tool:** `insumer_wallet_trust`
   **Expected:** Lists the ten dimensions with held and not-held counts, the profile ID (`TRST-...`), `conditionSetVersion`, and `kid: insumer-trust-v2`. No score or ranking.

4. **Prompt:** Use InsumerAPI to list its current signing keys and tell me how an attestation is verified offline.
   **Tool:** `insumer_jwks`
   **Expected:** Names the five key IDs (three ECDSA: `insumer-attest-v1`, `insumer-attest-v2`, `insumer-trust-v2`; two post-quantum: `insumer-attest-pq1`, `insumer-trust-pq1`), says to match keys by `kid`, and points at the `insumer-verify` package.

5. **Prompt:** Use InsumerAPI to look up the merchant "skyemeta-demo-store" and tell me what discount wallet 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 would get there.
   **Tools:** `insumer_get_merchant`, then `insumer_check_discount`
   **Expected:** Gives the merchant's name (Skye Meta Demo Store) and tiers and the resulting discount percentage: 5% for a wallet that has not proven control, 10% if it does. No balance figure appears.

## Negative cases (the plugin should not be used)

1. **Scenario:** Price question: the user wants a market price, which InsumerAPI does not provide. The plugin should not be invoked; a web search or no tool is correct.
   **Prompt:** What is the current price of ETH in USD?

2. **Scenario:** Transaction request: the user wants to send funds. InsumerAPI reads wallet state and never sends transactions, so the plugin should not be invoked.
   **Prompt:** Send 0.5 ETH from my wallet to 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045.

3. **Scenario:** Non-crypto use of the word wallet: the user is asking about a physical wallet, not a blockchain address. The plugin should not be invoked.
   **Prompt:** I lost my wallet on the train yesterday. What should I do first, cancel my cards or file a police report?

## Demo video

https://youtu.be/N0fuqh8RWvE

## Release notes

0.2.0: first release. Connects to the hosted InsumerAPI MCP server (api.insumermodel.com/mcp, no account or key) with ten tools: signing keys, condition attestation, compliance templates, wallet trust profiles (single and batch), the merchant and token directories, a discount check, and discount-code validation. Seven skills are included; six cover the same work through the REST API with your own key, including discount codes. Every signed result is signed twice, with ES256 and with a post-quantum ML-DSA-65 signature, and is verifiable offline with insumer-verify. The shared server is rate limited per day; when the limit is reached, signed-result tools are declined until 00:00 UTC.
