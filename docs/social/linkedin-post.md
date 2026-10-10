# BasketLens | LinkedIn post

Publish with the three numbered M6.2 PNG slides once the hosted demo works in a logged-out incognito browser.

A product pairing is interesting. But is it consistent enough to deserve a business experiment?

I built BasketLens to explore that question using UCI Online Retail II, a historical retail dataset collected from 2009 to 2011.

After data-quality checks, I analysed 40,280 eligible invoice baskets. I mined product associations on earlier orders, then checked whether the same relationships appeared in a later holdout.

One example: Jumbo Bag Pink Polkadot and Jumbo Bag Red Retrospot had 63.1% training confidence. In later orders, conditional co-occurrence was 67.1%, or 279 of 416 baskets containing the first bag also containing the second.

That does not prove a bundle or adjacent display would increase sales. It suggests a hypothesis worth testing, after checking inventory and contribution margins.

I built a reproducible Python analysis pipeline, FP-Growth association research with chronological holdout, an interactive Streamlit dashboard, privacy-safe public aggregates, unit tests and browser QA.

Explore: https://basketlens-retail.streamlit.app/
Source and method: https://github.com/Fadhilstat/BasketLens

I would be interested to hear how other analysts evaluate associations before turning them into retail recommendations.

#DataAnalytics #Python #MarketBasketAnalysis

## Short CV bullet

Built BasketLens, a Streamlit market basket research application using UCI Online Retail II. Audited over 1M source lines, analysed 40,280 baskets, mined FP-Growth product associations and checked the results using a chronological holdout. Shipped privacy-safe public aggregates, unit tests, responsive UI and an evidence-based retail case study.
