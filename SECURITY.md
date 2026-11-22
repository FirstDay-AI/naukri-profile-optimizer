# Security policy

## Supported versions

Security fixes go into the latest release only.

## Reporting a problem

Please **do not open a public issue** for a security problem. Email
**team@firstdayai.in** with:

- what the problem is and what someone could do with it;
- steps to reproduce, or a proof of concept;
- the version (`naukri-optimizer --version`).

We aim to reply within 3 working days and will tell you when a fix is out. We are
happy to credit you in the release notes if you'd like.

## What is in scope

- Anything that could expose a user's API key, or send it anywhere other than
  the AI provider the user chose.
- Anything that makes `naukri-optimizer check` reach the network (it should
  never do so).
- Ways a crafted profile file could run code or make the CLI write files it
  shouldn't.
- Prompt injection through profile fields that changes what the AI rewrite does
  in a harmful way.

The hosted version at firstdayai.in is a separate service; report problems
with it to the same address.
