# Security Policy

## Supported versions

Security fixes are applied to the latest tagged release.

## Reporting a vulnerability

Please use GitHub private vulnerability reporting for
`Iu1ky/paper-digger`. Do not include unpublished manuscripts, credentials,
private datasets, or other sensitive research material in a public issue.

Include the affected version, host agent, installation method, reproduction
steps, impact, and any proposed mitigation. Maintainers will acknowledge a
complete report as soon as practical.

## Execution model

Skills may instruct a host agent to run local commands, read research files, or
use optional network services. Paper Digger does not pre-approve shell tools in
skill frontmatter. Users should inspect installed skills and retain their host's
normal permission prompts.
