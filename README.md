# syw-site

Docs sites for [showyourwork](https://github.com/showyourwork/showyourwork) papers: the paper's
numbers, figures and interactive [figpress-apps](https://github.com/nstarman/figpress-apps) webapps, built by the
paper's own pipeline and published at `nstarkman.space/<repo>/` with the website's layout — and
nothing published until the author says so.

```bash
pip install "syw-site @ git+https://github.com/nstarman/syw-site@vYYYY.MM.DD"   # beside showyourwork
syw-site init            # docs/, docs/syw-site.yml (publish: false), a Snakefile include, a workflow
syw-site build           # the paper, its facts, figures and webapps, then the site
syw-site serve           # http://127.0.0.1:8000/<repo>/
```

Pages are MDX that cite the paper by name — `<Var name="forecast/gain" />`, `<Fig label="fig:a" />`
— so the site and the PDF never disagree. The `syw-site` skill (in
[nstarman/skills](https://github.com/nstarman/skills)) walks an agent through it.
