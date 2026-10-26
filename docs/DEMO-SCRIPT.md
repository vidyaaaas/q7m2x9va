# Two-part demo script

The accompanying video uses synthetic narration and screenshots of the working application. Review before uploading as an unlisted YouTube video. Vercel production deployment is verified at https://q7m2x9va.vercel.app. Public repository: https://github.com/vidyaaaas/q7m2x9va. Unlisted video: https://youtu.be/n-ZiWoceHgw.

## 1. CLIENT OVERVIEW â€” Tomorrow, with perspective.

Welcome to Windward, a pilot for the Great Britain day-ahead electricity procurement desk. The product answers two questions. What wind forecast was available when we had to decide? And how wrong were comparable forecasts in January? This walkthrough uses real Elexon data, not simulated values. The first part presents the client experience. The second explains the implementation for a technical reviewer. The narration is AI generated. The application is publicly deployed on Vercel, and its source is available in a public GitHub repository. The application and repository links are included in the video description and README.

## 2. CLIENT OVERVIEW â€” A decision you can replay.

On the decision desk, choose a January decision date and a cutoff. Here, the decision is January fifteenth at nine a.m. GMT, for delivery on January sixteenth. The forecast shows about one hundred and ninety gigawatt hours of wind energy over the delivery day, with average output near seven thousand nine hundred and thirty megawatts. Every plotted point uses the latest publication strictly before the cutoff. The oldest selected forecast is one and a half hours old at decision time. This makes the distinction between target time and publication time visible, rather than hiding it inside an attractive chart.

## 3. CLIENT OVERVIEW â€” See the difference. Keep the evidence.

Realised actuals are hidden by default. Turning them on adds a separate comparison line, explicitly marked as hindsight. It shows where wind delivered above or below what the desk could have expected. The audit table links each delivery hour to its selected publication time and forecast lead time. Export audit CSV preserves that evidence, including the decision cutoff, forecast, actual and signed error. The chart is hourly because that is the resolution of the January forecast data. The two half-hour actual values are averaged, with both required before an hour is scored.

## 4. CLIENT OVERVIEW â€” Quantify the miss, not just the trend.

The accuracy view evaluates all seven hundred and forty-four delivery hours associated with January decisions. At nine a.m., mean absolute error is two thousand and thirty-nine megawatts. Root mean squared error is two thousand five hundred and five, highlighting the effect of larger misses. Bias is positive one thousand seven hundred and forty-eight megawatts, meaning forecasts exceeded observed generation on average. Weighted absolute percentage error is eighteen point one percent. Daily bars and hourly bias help the analyst find the days and delivery periods that deserve investigation. Each daily score can be opened back on the decision desk.

## 5. CLIENT OVERVIEW â€” Useful evidence. Honest boundaries.

At the afternoon cutoff, mean absolute error falls to about one thousand nine hundred and four megawatts, six point six percent lower for this month. This is a historical comparison, not a guaranteed improvement. Full-month statistics and the displayed ninetieth percentile are retrospective; they were not known at each January decision. National wind error also cannot determine this client's purchase volume without its demand, contracts and other supply. The pilot provides trustworthy visibility and measurable error. The next phase would connect the portfolio and validate uncertainty over a longer history before making procurement recommendations.

## 6. TECHNICAL REVIEW â€” Small architecture. Explicit boundaries.

For the technical review, start with the architecture. An offline Python importer retrieves only WINDFOR and FUELHH WIND from Elexon, in bounded daily requests with retries. It saves the real rows and a manifest containing request URLs, retrieval time and SHA two fifty-six hashes. Pure Python analysis functions operate on that snapshot. FastAPI exposes daily, monthly, CSV and provenance endpoints. React renders the three views. There is no runtime dependency on Elexon availability and no API key in the browser. A fixed month of public data does not need a database, so the snapshot keeps the pilot easy to reproduce and review.

## 7. TECHNICAL REVIEW â€” The cutoff is the core invariant.

The core rule is in backend analysis dot py. For each target hour, select the greatest publication time strictly before the cutoff. A publication exactly at the cutoff is excluded because the pilot does not assume instantaneous receipt and execution. Later publications never replace the selected vintage. January refers to decision dates, so the final delivery day is February first. Actuals are joined by timestamp, filtered to WIND, and averaged only when both half-hours exist. Equal-publication conflicts raise an error. Missing observations remain null and reduce coverage, rather than becoming zero. Timestamps are timezone aware; the entire pilot falls in GMT.

## 8. TECHNICAL REVIEW â€” Metrics you can independently reproduce.

The metric definitions are deliberately simple. Error is forecast minus actual. Mean absolute error measures typical magnitude; root mean squared error gives larger misses more weight. Bias retains the sign. Weighted absolute percentage error uses total actual generation as the denominator, avoiding per-period division by very small values. Zero denominators return null. The ninetieth percentile is an empirical linear-interpolated statistic, not a calibrated prediction interval. Full-day energy sums twenty-four hourly average powers in megawatt hours. Publication time is only an availability proxy: a production system must also store when the desk actually received each record.

## 9. TECHNICAL REVIEW â€” Review the checks, then the tradeoffs.

Thirteen Python tests pass, covering cutoff equality, latest-vintage selection, missing half-hours, fuel filtering, zero denominators, error sign, duplicate conflicts, date validation and CSV output. Snapshot checks confirm seven hundred and forty-four matched hours at all four interface cutoffs, with no selected publication after the decision. Browser checks exercise the actual API, navigation, cutoff changes, hindsight toggle, month boundary and mobile overflow. The production frontend build passes. The multi-stage Dockerfile builds React and serves it from a non-root Python container. The public GitHub continuous integration run has passed, including the Docker image build and a live container health check. This verifies the container in addition to the local application and hosted Vercel deployment.

## 10. TECHNICAL REVIEW â€” A clear handover and next step.

The README maps every directory, explains local and Docker startup, discloses AI assistance and documents the measured results. The technical handover explains the API contract and production limitations. The Vercel production application is deployed and verified. The public GitHub repository contains the code, data, tests and handover documents. Links are included in the README and video description. For review, read the analysis functions first, then their tests, the importer, the API and the React views. The next engineering steps are transactional ingestion, source-arrival timestamps, schema checks, monitoring, longer rolling-origin evaluation and client portfolio integration. The delivered pilot is intentionally focused: a clear forecast decision trail and an honest quantitative evaluation, with no invented savings or unsupported trading recommendation.