# Verification record

## Public application

- URL: https://q7m2x9va.vercel.app
- Vercel deployment: `dpl_4FjDzp3fpzvNJneTpyJ9JxGhkQRZ`, production, READY.
- Application source commit used for deployment: `538d96d` (local); equivalent application files are in the public repository.
- Build log reported completion in 14 seconds.
- Unauthenticated HTTP 200 verified for root, health, day, month, provenance, CSV and OpenAPI documentation.
- Live monthly results matched the local snapshot: 744 pairs, MAE 2038.9126 MW at 09:00 GMT.
- Browser checks passed: desktop navigation, actuals toggle, afternoon cutoff recalculation, February boundary, 25-line audit CSV and mobile layout without page overflow. No JavaScript exceptions observed.
- No error/fatal runtime logs were returned by the post-deployment query. This is a bounded smoke check, not continuous monitoring.

## GitHub and Docker

- Public source: https://github.com/vidyaaaas/q7m2x9va
- CI evidence: https://github.com/vidyaaaas/q7m2x9va/actions/runs/40279053311
- Result: SUCCESS.
- Passed steps: 13 Python tests, snapshot hash/grid/coverage validation, npm install, frontend production build, Docker image build, container startup and HTTP health probe.
- The Docker image was tested on GitHub's Ubuntu runner; Docker is not installed on the authoring Windows computer.

## Scope of claims

The public site uses the submitted data and analysis code. No trading, customer-portfolio optimisation, out-of-sample risk calibration or financial savings have been validated. Full-month error metrics are retrospective. All screenshots show the real application with Elexon data.
