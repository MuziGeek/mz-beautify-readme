# README localization

Use this workflow when a repository has more than one README language or the user requests localized Hero assets.

## Discover locales

- Detect language variants from repository files and navigation, such as `README.md`, `README.zh-CN.md`, `README.ja.md`, or localized documentation roots.
- Treat the language of the primary README as `primaryLocale`. Ask only when the mapping is ambiguous.
- Record every generated language in `localization.outputLocales` and map it to the exact README path in `localization.readmeFiles`.
- Use BCP 47-style tags such as `en`, `zh-CN`, `zh-TW`, `ja`, or `fr`.

## Preserve one design decision

Localization may adapt line breaks, font fallback, spacing, and text size for glyph coverage and reading rhythm. It may not change content claims, proof, composition mode, implementation, the validated visual Brief, Extension participation, or motion.

Keep the project name, commands, API names, versions, and technical identifiers exact unless the repository already localizes them. Translate meaning, not word order. Use repository terminology rather than an unreviewed literal translation.

## Generate localized assets

- Keep exact copy outside generated raster layers. Render language-specific text deterministically.
- Use `heroCopy` for `primaryLocale` and `localizedHeroCopy[locale]` for every other output locale.
- Run `python scripts/plan_localized_assets.py --primary-locale en --locales en zh-CN --extension webp --mobile` to produce stable names.
- Default naming:
  - primary desktop: `hero.webp`
  - primary mobile: `hero.mobile.webp`
  - localized desktop: `hero.<locale>.webp`
  - localized mobile: `hero.<locale>.mobile.webp`
- SVG and PNG use the same naming grammar with their own extension.
- Record `locale` and `viewport` for every published asset and variant in `mz.readme-asset/3`.

## Embed and validate

- Each README must reference only its own locale's desktop/mobile assets and use localized alt text.
- Preserve GitHub-safe `<picture>` routing when a mobile composition is required.
- Verify every locale independently at `900px` and `360px` on light and dark GitHub surroundings.
- Check missing glyphs, fallback-font substitution, clipping, wrapping, proof legibility, translated alt text, and local asset paths.
- Lock every visible string from every locale before `READY_FOR_REVIEW`.
- If one locale fails, the multilingual asset set is not `READY_FOR_REVIEW`.
