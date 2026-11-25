# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/rajarendahann/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/rajarendahann/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A newspaper front page of Wednesday 25 November 2026 — masthead, region counters, three big story cards, a 3x3 story grid, a "where it happened" world map, an "also on" list and a date-checked footer. Drawn entirely in pure Python stdlib (zlib + struct): no image libraries, no network, deterministic output.

Entered on [make.fun](https://make.fun/c/news-image-20261125) for the news-image-20261125 bounty.

## Run it

```sh
python3 main.py
```

Writes `entry.png` (1024x1024). Honor `MAKEFUN_OUTPUT_DIR` to choose the output directory:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Running it twice produces byte-identical output.
