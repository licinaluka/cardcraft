# Project Leo

cardcraft as a working title.

A trading card game builder as a service (TCGBaaS) platform that helps trading card game designers on Solana solve - at least - problems of
- game implementation details
- content customization
- gameplay customization
- software development and distribution

---

## Revenues for the MVP

- match pot
- card/NFT trading
- selling game history storage

---

## Potential revenues once past MVP stage
- physical card/accessory production, distribution, and authenticity/nonce verification
- B2B or open-core model where designers self-host & self-manage their own systems, receive software updates
- match betting

---

## Technologies and scope implications

To keep MVP scope small enough, the following patterns are employed

- polylith software architecture
  - monorepo development workflow
  - keeps complex systems manageable
  - allows for much simpler automated testing & CI/CD
- capistrano/fabric based deployment automation
  - from code to target in a matter of seconds
- python
  - large talent pool, capable language
  - Anchor code written in seahorse
  - *can be compiled and released as a proprietary binary
- HTMX for 
  - dynamic webapps without overhead
  - *can be turned into native mobile apps via hyperview
  - REST APIs for custom frontends is a matter of responding with JSON instead of HTML
- document database
  - implementing custom game rules
  - data is easier to handle if data structures and types are restricted application-side
  - fewer limits on amount of data stored (read: game histories)
  
