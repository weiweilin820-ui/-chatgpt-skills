---
name: random-portrait-fusion-pro
description: Generate long-form director-card prompts for realistic portraits of an explicitly adult female character, locking identity to a multi-angle reference and varying location, activity, outfit, optional hosiery, artistic finish, light and camera. Use for 随机写真、导演卡、角色一致性、旅行途中做事、画室或舞蹈室、镜前拍摄、花影朦胧或对影成三人、车展、漫展COS、末世僵尸、天庭地府龙宫、精灵城矮人城、职业制服 POV, or continuation of this portrait prompt series.
---

# Random Portrait Fusion Pro

Create production-ready Chinese director cards while preserving the referenced adult character's identity. Treat every depicted person as an adult aged 23 or older. Produce prompts only; do not generate images unless the user separately requests image generation.

## Rule precedence and non-negotiables

Resolve conflicts in this order: **the user's latest explicit instruction in the current conversation → this section → the rest of `SKILL.md` → reference files → examples**. Examples never override a hard rule. When two references disagree, use the newer/higher-priority rule from this file instead of blending both.

Hard invariants for this skill:
- This is a **prompt-writing skill**. Do not call image generation unless the user explicitly asks to create an image.
- The depicted main character is always an adult aged 23+ and identity consistency has priority over styling novelty.
- All shoulder construction remains bilaterally balanced: no single-shoulder, diagonal-shoulder, one-sleeve-only, or asymmetric shoulder opening.
- All leather / faux-leather garments are excluded. Dark green, caramel, the removed silver reflective bodysuit, and short/ankle hosiery are excluded.
- **Waist/abdomen rule:** waist exposure is **optional, not global**. Only when the sampled macro outfit architecture is an exposed-waist two-piece / cropped construction should the prompt say “腰腹完整呈现，线条流畅自然”. Do not force that phrase onto one-piece dresses, qipao, rompers, tailored dresses, high-slit long dresses, or other architectures whose sensuality comes from neckline, back, hem, slit, or fit. Side-waist cutouts, waist cutout panels, abdominal holes, and small localized waist openings remain forbidden.
- Sexy styling must come from the garment silhouette itself, not from hosiery, heels, color, tightness, or the word “性感”.
- Artistic finishes may layer in a controlled way; identity, face clarity, anatomy, and the main action remain readable.


## Load the required references

Read these files before composing any card:

1. `references/人物层.md`
2. `references/变量池-形象神态.md`
3. `references/变量池-服装场景.md`
4. `references/变量池-摄影语言.md`
5. `references/变量池-导演路线.md`
6. `references/成像机制原则.md`
7. `references/人物美姿导演.md`
8. `references/情绪表达.md`
9. `references/场景名词池.md`
10. `references/场景灯光POV池.md`
11. `references/场景抽样机制.md` — large batches and all "truly random" requests

For batches of 5 or more, also use `scripts/select_batch.py` after building a candidate-plan JSON file. The script selects the final plans and reports semantic diversity; it does not write the final director-card prose.

Load the following only when the selected mode needs them:

- COS: `references/cos角色池.md`
- Candid mode: `references/同行者纪实抓拍.md`
- Profession or uniform POV: `references/职业制服POV批产.md`

## Interpret the request

- Default to one group if the user does not specify a count.
- Prompt-writing is the default and is a hard boundary for this skill. Requests such as “换五组”“随机五组”“来五组”“整个池子随机”“这个主题来几组” mean **write prompt cards only**. Never call an image-generation tool unless the user explicitly asks with wording such as “出图”“生图”“生成图片”“画一张/画几张”.
- Respect explicit constraints first: count, aspect ratio, style, outfit, scene, direct gaze, exposure level, realism, and platform-specific phrasing.
- If reference images are unavailable in the current turn, still write the identity-lock clause so the prompt can be paired with them later; do not invent facial traits.
- Never create a standalone `表情` heading. Treat emotion as an independent creative variable governed by `references/情绪表达.md`. Write only a concise emotion state inside `场景与动作` (for example 开心、惊喜、憔悴、难过、惊慌、困惑、无奈); do not micro-direct facial muscles such as mouth corners, teeth, eyebrow height, eye opening, cheek lift, or exact lip shape. If the user explicitly supplies an emotion, preserve that emotion rather than replacing it with a different one.
- Do not ask follow-up questions when a coherent random card can be generated safely.
- Treat a user-specified theme as a live constraint, **not as a preset pack**. Build it from the same scene/outfit/action/camera pools at generation time. Do not load or emulate deleted theme-package prose.
- “整个池子随机 / 完全随机 / 重新随机” means independently re-draw both the **scene tuple and the outfit tuple**. It is not valid to keep the same garment silhouette and merely change color, hosiery, material wording, or venue.

- Apply later user rules over older rules. Current hard exclusions: all leather garments, dark green, caramel, the removed silver reflective bodysuit, and all short socks / ankle-length hosiery (`短袜`, `短筒袜`, `短筒丝袜`, `船袜`, `踝袜`). If hosiery is used, start from `中筒` or longer.
- Draw clothing colors from the complete palette in `references/变量池-服装场景.md`: rainbow pastels, vivid colors, wine red and other clean deep tones, black, white, pure gray, metallics, and color contrasts. Do not treat light-colored tops as a default constraint.
- For this user's portrait batches, sexify ordinary garments as well as special fashion pieces. Do not output an unchanged conservative shirt, sweater, hoodie, suit, sports uniform, historical outfit, or homewear set. Give each outfit one dominant skin-revealing structure plus one secondary structure, chosen from an open neckline, balanced off-shoulder line, open back, cropped construction with the waist/abdomen fully and continuously visible, low-rise bottom, short-skirt/shorts proportion, or a genuinely high slit. Do not use side-waist cutouts or abdominal cutout panels. Keep the result wearable and fashion-led.
- If the user reports the generated bust looks too small, explicitly anchor the adult figure to the reference proportions and visually natural E–F fullness; use correctly fitted seams and drape to preserve its volume. Do not exaggerate anatomy or turn the shot into a chest close-up.
- The user's preferred candid camera language is an ordinary companion or event photographer capturing a natural moment. In generated cards and their negative prompts, omit expressions including “偷拍”“偷摄”“监视”“窥视”; use “同行者随手拍”“自然抓拍”“刚抬起手机记录的一帧” and a plausible camera position instead.

## Randomization algorithm

For each card, independently sample:

`director route × scene domain × spatial archetype × specific location × **macro outfit architecture** × outfit family × top silhouette × bottom/one-piece silhouette × dominant material × activity × pose family × emotion state × hosiery eligibility × optional leg styling × required artistic finish × lighting × color × camera angle × framing × image quality`

For random batches, actually draw choices using an available random-number generator (for example Python `secrets.SystemRandom`), following `references/场景抽样机制.md`. Do not cycle through a memorized sequence, take one venue from every category in order, or select only familiar example locations. Draw the scene domain, then the spatial archetype, then the specific venue so long lists of modern streets and travel landmarks cannot drown out unusual settings. **Draw the macro outfit architecture first**, then draw outfit family, top silhouette, bottom/one-piece silhouette, dominant material, color and styling inside that architecture. The macro architecture is the visual skeleton and has priority over neckline/color variation. Outfit diversity is structural: changing only neckline, color, material, hosiery, shoes or accessories does not make the same visual skeleton new. General random batches must rotate across genuinely different architectures such as exposed-waist two-piece, one-piece mini dress, short qipao, new-Chinese two-piece, romper/short jumpsuit, sports dress or coordinated sports set, tailored short suit/dress, slip/halter mini dress, fitted high-slit long dress, swimwear/holiday look, and fantasy/COS complete costume. Do **not** let “cropped top + short skirt/shorts” become the compatibility fallback. Follow the aspect-ratio weights in `references/变量池-摄影语言.md`, unless the user specifies a ratio. When the recent batch is visible, exclude its repeated spatial structures, specific venues, venue–activity patterns, and outfit silhouettes before sampling. If prior output is unavailable, say nothing about historical exclusions and only deduplicate what is visible.

### Start-from-zero batch procedure

When the user says “从 0 开始”“重新抽”“完整随机” or reports that a new batch is only a rewrite of the previous one, do not edit, reorder, recolor, or paraphrase old cards. Build a new pool of compact candidate plans before writing any prose:

1. Create at least `max(4 × requested_count, requested_count + 60)` candidates from the reference pools. Each candidate is only a structured combination, not a finished card.
2. Store the fields required by `scripts/select_batch.py`: `scene_domain`, `spatial_archetype`, `venue`, `facility`, `activity`, `pose_family`, `outfit_architecture`, `outfit_family`, `top_silhouette`, `bottom_silhouette`, `material`, and `artistic_finish`. Add any optional fields needed for later prose.
   - Macro outfit architecture is a mandatory first-stage draw. It describes the silhouette skeleton, not a styling adjective.
   - For unthemed batches of 10+, target at least 6 distinct macro architectures; for 20+, at least 8; for 50+, at least 10 when the pool allows.
   - In unthemed batches, the exposed-waist “cropped top + short bottom” architecture should normally stay at or below about 40% of the batch, and no single macro architecture should dominate merely because it is easy to style.

3. Do not create candidates by taking a completed card and swapping its city, color, hosiery, prop, or light. Independently draw the scene tuple, activity tuple, outfit tuple, artistic finish, and camera tuple.
4. Run `python3 scripts/select_batch.py --input <candidate.json> --output <selected.json> --count <N>`. Use `--seed` only when the user asks for a reproducible draw.
5. Write cards only from `selected.json`. Treat its `direct_gaze`, `companion_camera`, `cos_mode`, `aspect_ratio`, and `framing` fields as binding unless they conflict with an explicit user instruction.
6. Read the emitted `audit`. If unique venues or outfit fingerprints are below the requested count, if adjacent fingerprint distance is below four, or if the pose/domain coverage is poor for a general random batch, expand the candidate pool and rerun instead of repairing cards by paraphrase.
7. Run a final hard-rule audit before prose: reject any selected plan containing leather/faux leather, dark green, caramel, forbidden shoulder asymmetry, short/ankle hosiery, side-waist/abdominal cutouts, or a repeated outfit silhouette disguised by color changes. Also reject any plan whose framing/action contradicts the direct-gaze or static-standing limits.


For fewer than 5 cards, the script is optional, but the same semantic fingerprint and compatibility rules still apply. For batches of 5–9 cards, run the same selector/audit so small batches do not collapse into repeated pose-action templates. Mandatory identity, body, skin, and negative-prompt text is expected to repeat and must be excluded from similarity judgments.

Then run a compatibility pass:

1. Keep identity, anatomy, wardrobe construction, action, and environment physically coherent.
2. Sample scene and outfit independently. Do not require period, occupation, color, or social-setting agreement. Preserve intentional contrast instead of normalizing a surprising but viable pairing into a conventional one.
3. Convert duplicate action aliases to one semantic action before sampling so repeated wording does not overweight it. Use `references/人物美姿导演.md` for the body movement and `references/场景名词池.md` sections 44–45 for its practical purpose; combine them into one believable ongoing event.
4. Remove duplicate venue–activity pairs and near-identical visual events within a batch. Treat renamed corridors, window seats, counters, platforms, and landmark-front poses as repetitions when their spatial archetype, facility, and action remain the same. Apply the rolling cooldown in `references/场景抽样机制.md` rather than following a fixed alternation.
5. In a large batch, strongly favor direct gaze: target about 80% of subjects looking into the lens, usually while their hands continue a meaningful task or in the half-second after responding to the photographer. Keep non-camera gaze to roughly 20% or less, avoid placing several non-gaze cards consecutively, and use it only when the scene or action clearly benefits from attention being elsewhere. Direct gaze does not require a stationary, front-facing pose: slight three-quarter angles, seated poses, movement, selfies, candid actions, and fantasy scenes should still preserve clear eye contact whenever physically plausible. In the remainder, keep the face visible while attention stays on the task or surroundings. Independently sample one emotion state from `references/情绪表达.md`, repair it for scene compatibility, and place it as a short clause inside `场景与动作`. Do not create separate `视线` or `表情` headings. Write gaze, head direction, pose/action, event context, and the concise emotion only inside `场景与动作`; never spell out facial-muscle mechanics such as how far the mouth opens, how many teeth show, eyebrow height, eye width, cheek lift, or lip shape.
6. Trigger the companion-camera mode in `references/同行者纪实抓拍.md` independently with probability 1/5; its output vocabulary restriction applies to every card, including negative prompts. Softly blurred flowers, leaves, grasses, or other small plants may sit between the camera and the subject when they stay near the frame edges and do not cover the face, torso outline, or main action. A curtain may cross the foreground or part of the figure only when it is thin, translucent, and visibly transmits the person's facial features and body outline. Exclude opaque foreground objects, dense foliage, dirty glass, passing people, and any obstruction that hides the subject.
7. Independently draw outfit silhouettes from the `COS角色服装剪裁池` in `references/变量池-服装场景.md`, including ordinary locations. Trigger complete COS mode separately with probability 1/10 when the selected scene is outside a comic/anime convention. If the scene is 漫展 or 同人展, trigger COS unconditionally, choose one character from `references/cos角色池.md`, and make costume, hairstyle, and props recognizable while preserving the reference face. When combined with the companion-camera mode, use a plausible convention or backstage moment.
8. For 16:9, use a close portrait no wider than seven-tenths body; never use a full-body or large-environment composition.
   Static standing full-body compositions are a low-frequency exception, not a default. Prefer seated, kneeling, reclining, leaning, crouching, selfie, walking, or task-in-progress structures; if a standing pose is selected without a strong reason to show shoes or a full silhouette, crop it to half-body, knee-up, or seven-tenths framing. For every aspect ratio, reject extreme long shots, distant environmental portraits, tiny landmark poses, and any composition in which the face becomes too small to preserve identity. A full-body subject must occupy about 75–88% of image height; a seven-tenths, knee-up, or half-body subject must remain visually dominant and normally occupy about 70–90% of image height. Keep the face large enough for the reference identity, facial proportions, skin texture, and identifying mole to remain clearly readable. If a landmark or large fantasy environment conflicts with face scale, crop or compress the environment instead of moving the subject farther away.
9. Draw scene and outfit separately; keep their viable contrast. Do not force fixed match/contrast quotas that make successive batches predictable.
10. For travel and everyday scenes, draw a meaningful activity from `references/场景名词池.md` sections 44–46, pair it with one place-specific object, and catch a moment mid-action. Vary boating, picnicking, running, cycling, safely stopping an electric scooter, making art, dancing, cooking, and using mirrors; avoid repeated stationary landmark poses. Let a glance meet the lens without interrupting the action when the sampled gaze is direct. Choose practical shoes and gear when an activity demands them.
11. Finish and approve the clothing silhouette before drawing leg styling. First reject an unchanged midi skirt, ordinary long skirt, wide-leg trousers, loose full-length trousers, or other conservative lower-body silhouette; resample it or convert it into a mini, fitted shorts, a genuinely high-slit fitted long skirt, fitted ripped denim, or another fashion-led silhouette. Then determine hosiery eligibility from outfit, activity, weather, framing and footwear. Use the three-way leg-styling distribution and compatibility matrix in `references/变量池-服装场景.md`; hosiery is optional, never a repair for an unattractive outfit. Draw the hosiery family first and its compatible color second. Gray-purple or lavender hosiery is a low-frequency accent, not a neutral fallback. Do not make hosiery a body-part close-up. Garment shapes and color samples are independent: the loose draped deep-V chiffon top retains its cut and fabric description while its color varies freely.
12. Draw at least one named artistic finish from `references/变量池-摄影语言.md` for every card. Artistic finishes may be layered: normally use **one primary finish plus zero or one secondary finish**, and allow up to three only when the user explicitly requests a denser combination. The primary finish must remain visually dominant; secondary finishes must add a different physical mechanism rather than restating the same bloom, haze, reflection, or projection. Make every selected finish physically legible through plausible light, shadow, reflection, projection, window, plant shadow, water reflection, translucent curtain, shallow-depth foreground, motion, or optical diffusion. Keep the real person's face and figure clearly visible; shadows, paintings, and reflections may echo or visually interact with her but may not become extra physical people. Companion-camera mode may also use `花影朦胧` or `隔帘见人` when blurred plants remain light and peripheral or the curtain is translucent enough to preserve facial features and body contours. Never place opaque fabric, dense foliage, or a large foreground object over the face, torso, or main action.
13. Build the outfit from the selected **macro architecture** rather than defaulting to a top-plus-bottom pair. For one-piece architectures, do not mechanically invent a cropped top or separate short skirt. Run the silhouette-and-material audit, sensuality gate, hosiery audit and outfit fingerprint cooldown in `references/变量池-服装场景.md`: one visual focal point, compatible construction, balanced fabric weight, controlled transparency, and no competing all-over lace, metallic shine, print, and chains. Require one dominant skin-revealing structure plus one secondary structure before hosiery is considered. Waist exposure is only one possible reveal; when the architecture genuinely exposes the waist, use a continuous cropped construction and `腰腹完整呈现，线条流畅自然`. Otherwise use neckline, open back, short hem, slit, shoulder/neckline exposure, or fitted silhouette as appropriate. A color, print, hosiery, shoe, accessory, or minor neckline change does not make a repeated macro silhouette new.
14. Before prose writing, store one internal fingerprint per card: `scene domain｜spatial archetype｜venue/facility｜activity｜outfit architecture｜outfit family｜top silhouette｜bottom/one-piece silhouette｜dominant material｜artistic finish`. Also store a **visual-skeleton fingerprint**: `outfit architecture｜one-piece vs two-piece｜waist treatment｜garment length profile`. Two outfits with different colors or necklines but the same visual skeleton remain near-duplicates. Also store a separate pose/action fingerprint: `pose family｜hand action｜body orientation｜task vs pure pose｜selfie/mirror/candid state`. Reject batches that repeat the same body-and-hand template even when venue and props differ. Reject a candidate that is too close to another card in the current batch or the recent visible batch. Adjacent cards must differ in at least four fingerprint fields. If compatibility fails, resample only the conflicting field; never normalize the candidate into the same familiar corridor, short top, mini skirt, or static landmark pose used nearby.

For long batches, sample the scene plan with a real random generator and treat compatibility and exact-duplicate rejection as constraints. Do not claim mathematically uniform complete prompts: the final wording still needs creative writing and physical plausibility.

## Final validation gate

Before emitting any card, verify all of the following. If one fails, repair the **plan**, not just the prose:

1. Identity lock, age, anatomy and face scale are intact.
2. The scene/activity is physically coherent and not a recent visible near-duplicate.
3. The outfit silhouette is genuinely different from neighboring/recent cards; color-only changes do not count.
4. The macro outfit architecture was sampled before neckline/material/color; a general batch does not collapse into repeated cropped-top + short-bottom silhouettes.
5. No forbidden garment/material/color/hosiery/shoulder structure appears.
6. If—and only if—the sampled architecture exposes the waist, it is continuous and natural: “腰腹完整呈现，线条流畅自然”; do not inject this phrase into one-piece architectures that do not expose the waist.
7. The outfit itself passes the sensuality gate before hosiery/shoes/accessories are considered.
8. Gaze, framing and pose obey the ~80% direct-gaze target and low-frequency static standing full-body rule.
9. Artistic effects have clear primary/secondary physical mechanisms and do not obscure the face or create extra physical people.
10. The ten required headings are present exactly once in detailed cards; no separate expression/gaze heading is added.
11. Prompt-writing requests remain text-only. Never invoke image generation implicitly.

## Default to the detailed ten-block director-card format

The user's current preference is the long, rich, self-contained ten-block card below, even for large random batches. Give each card its own full identity lock and negative prompt so it can be copied alone. For **unthemed/general random requests** where the user does not specify a presentation style, keep all ten sections but serialize each card horizontally in one copy-friendly line using `｜【section】content` separators, inside its own code block, so the user does not need to scroll through ten vertically stacked sections. Theme-specific requests may use the same horizontal layout unless the user asks for vertical sections. Do not add an expression block. In `场景与动作`, describe the ongoing activity, body movement, pose, head direction, gaze, and one concise emotion state. Describe the emotion semantically (such as 开心、悲伤、憔悴、难过、惊慌、好奇、无奈), not through facial-muscle instructions. In `摄影质感` and `光线与色彩`, describe the chosen artistic finish and how its real light or optics work. Keep the subject visually dominant and the referenced face large enough for identity details to remain readable. Use compact records only if the user explicitly requests a short list, overview, table, or simple description.

## Compact format when explicitly requested

When the user explicitly asks for a compact version, keep the scene-specific activity, clothing and color, optional hosiery, hair style and color, shoes and whether they enter the frame, aspect ratio/framing/camera angle, and main light plus capture quality. Use this order:

`编号｜固定人物前缀｜场景＋正在发生的事｜服饰＋配色＋适配的丝袜（可选）｜发型＋发色｜鞋履／是否入镜｜画幅＋景别＋机位｜主光＋命名的艺术成片效果＋画质氛围`

Use the exact short identity prefix in `references/人物层.md` inside every compact record. Do not leave the prefix only above the batch, use `同上`, or require the user to assemble two text pieces. For a planning overview a table is acceptable; when the user asks to copy prompts, output numbered standalone paragraphs or individual code blocks, each containing the full prefix followed by its own scene, activity, outfit, hair, shoes, framing, and light. Preserve the reference proportions with plausible fitted fabric and neckline construction. Name a single recognizable place and a natural activity. Avoid boilerplate negative prompts in compact mode. Do not invent permanent facial traits.

For visible footwear, replace ordinary short boots with slender high heels in a color that fits the outfit. Reserve black sporty ankle boots only for a capable military or police look. Other functional shoes, such as court sneakers for active sport and flat sandals for a beach walk, may remain when they are part of the concept. If footwear is cropped out, write `不入镜` rather than naming a shoe that cannot be seen. Place a high-heel look on stable ground or an indoor walkway when the broader location includes snow, rocks, or a sports court.

## Detailed ten-block format

Use these headings in order:

1. `开头` — aspect ratio + director-route style + scene + framing
2. `人物身份锁定` — long identity lock + refined but natural features + real skin texture + clear face
3. `身材与比例` — 23-year-old adult woman + 170 cm + visually E–F cup + slender waist + defined collarbone + long legs
4. `发型`
5. `妆容`
6. `服装` — high-fashion coordinated look + clearly constructed coverage + smooth shoulder/neck/collarbone lines + clear waistline
7. `场景与动作` — specific place + pure action + body pose/head direction + gaze + concise emotion state + unforced moment
8. `光线与色彩`
9. `摄影质感` — capture quality + lens + camera angle + explicit subject occupancy + the required named artistic finish with a clearly legible face + refined editorial atmosphere without commercial studio polish
10. `负面提示词` — Keep negative prompts compact: include the stable global identity/anatomy/render exclusions plus only the card-specific failure modes. Do not pad them with repeated synonyms or restate the same prohibition three ways.

Do not add a standalone gaze section. Avoid blunt phrases such as “露出……” when describing styling; express visible skin through design language such as “肩颈与锁骨线条清晰”“腰侧线条清晰”“背部线条完整”“腿部比例得到延展”. Do not append stock disclaimers like “完整穿着、不暴露内衣、不走光” unless the user explicitly asks for them; enforce those constraints silently through garment construction and the negative prompt.

Never output a standalone `表情` block. Keep direct gaze, looking away, turning the head, reactions to the photographer, and the sampled emotion inside `场景与动作`. Emotion wording must stay short and semantic; do not translate it into detailed mouth, teeth, eyebrow, eye, cheek, or lip instructions.

## Quality bar

- Keep one clear event, one readable action beat, and one primary interaction object.
- Describe a plausible main light and restrained secondary reflections.
- Prefer real skin, fabric folds, loose hairs, natural weight, localized motion blur, and capture-medium artifacts over polished AI beauty language.
- Keep face visibility and face scale high. Exclude closed eyes, squinting, face-covering, downward poses that hide facial features, extreme long shots, tiny people, and excessive empty environment.
- Never imply nudity, transparent exposure of intimate anatomy, wardrobe malfunction, fetish framing, or a minor. Keep sensuality fashion-led and non-explicit.
- Write each card as a directly usable prompt, not as notes about the randomization process.

## Detailed batch output

When producing detailed cards, number them and give each a short route title. Keep every card self-contained, including the identity lock and negative prompt. Do not replace repeated mandatory identity details with “同上”.


## 2026-09-29 high-priority overrides

These rules override older examples in every reference file:

- Do not use asymmetric one-shoulder, diagonal-shoulder, one-sleeve, or single exposed-shoulder silhouettes. Replace them with symmetric spaghetti straps, halter straps, strapless tube/bandeau structures, symmetric low necklines, or other balanced two-shoulder constructions.
- In general random batches, use only portrait or square aspect ratios: `9:16`, `4:5`, `3:4`, or occasional `1:1`. Do not draw `3:2` or `16:9` unless the user explicitly requests a horizontal image. Default strongly toward 9:16.
- Reduce side-profile look-back poses. For a 100-card general batch, keep side-turn/look-back at no more than 5–10 cards and never place them consecutively. Prefer front-facing, slight three-quarter front, seated front, mid-action front, walking toward camera, crouching, leaning, and task-focused poses.
- Keep the overall wardrobe sensual and skin-revealing through fashion structure. Prefer symmetric spaghetti-strap, halter, strapless, low-neck, open-back, cropped-waist, side-waist cutout, mini-skirt, fitted-short, or high-slit constructions. Do not use hosiery or heels to rescue a conservative silhouette.
- For qipao, modified qipao, new-Chinese and Han-inspired looks, fitted silk, piping, frog buttons or traditional patterning alone do not satisfy the sensuality gate. Require one dominant fashion-opening structure plus one secondary structure. For short qipao, pair a thigh-high mini hem with a symmetric low/open neckline, open back or balanced side-waist cutouts. For long qipao, require clear high slits plus a low/open neckline, open back or waist cutout. For two-piece new-Chinese looks, prefer a symmetric low/open or halter-style cropped top with a mini skirt, split short skirt, fitted shorts or another fashion-led short lower silhouette. Preserve Eastern identifiers while rejecting conservative high-neck long-hem results that rely only on fit, hosiery or heels.
- Long denim trousers are a rare accent, not a default. In a 100-card batch, allow at most 1 long-denim-trouser card and at most 2 full-length-trouser cards of any kind. Prefer denim hot pants, ultra-short denim shorts, ripped denim shorts, denim mini skirts, or side-tie denim mini skirts instead.
- Hosiery must always name its structural length/form, not just color. Valid examples include `黑色薄透连裤袜`, `浅粉中筒丝袜`, `奶白及膝长筒袜`, `黑色过膝长筒袜`, `大腿长筒袜`, and `后缝吊带长筒袜`. Reject vague labels such as `黑丝`, `白丝`, `粉丝`, `黑色丝袜`, or `白色丝袜` when no structural form is stated.
- For the current optical-finish preference, strongly diversify physically plausible soft-obscuration and projection mechanisms: misted or frosted projection, blurred human shadow in the background, flower-shadow haze, candle-shadow layering, glass-sphere refraction, water-glass refraction, translucent-curtain diffusion, prism splitting, rain-on-glass double image, mirror edge echo, leaf-shadow diffusion, and localized moving light. Do not repeat the same finish wording across nearby cards.
- Treat `梦幻柔光溢出` from `references/场景灯光POV池.md` as a fixed reusable lighting module. It is scene-independent and may combine with backlight, mist, window light, sunset edge light, moonlight, water reflection, glass refraction, light strips, or restrained neon bloom. The dreaminess belongs to the light and background: keep the real face, skin texture, identifying mole, hairline, and garment construction sharply readable. Prefer glow on hair edges, shoulders, collarbone, body outline, and background; reject whole-frame milkiness, face-softening bloom, clipped highlights, or HDR shadow lifting.
- The optical effect may soften the scene, foreground, reflection, or projected shadow, but the real subject's face must remain readable and identity-stable. A background human-shaped projection is a light/shadow image, not a second physical person.
