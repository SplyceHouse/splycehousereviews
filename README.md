# splycehousereviews.com

Customer reviews of SplyceHouse, reproduced from our Google Business Profile.

- `reviews.json` is the source of truth: a tally of every Google rating, plus the written reviews shown on the page (newest first).
- A Zapier workflow adds each new Google review to `reviews.json`.
- `.github/workflows/build.yml` runs `build.py` on every push to `main` and publishes the site to GitHub Pages.
- To rebuild by hand: `python3 build.py`.
