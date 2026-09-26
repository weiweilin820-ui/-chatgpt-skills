---
name: random-portrait-fusion-pro
description: Generate long-form director-card prompts for realistic portraits of an explicitly adult female character, locking identity to a multi-angle reference and varying location, activity, outfit, optional hosiery, artistic finish, light and camera. Use for 随机写真、导演卡、角色一致性、旅行途中做事、画室或舞蹈室、镜前拍摄、花影朦胧或对影成三人、车展、漫展COS、末世僵尸、天庭地府龙宫、精灵城矮人城、职业制服 POV, or continuation of this portrait prompt series.
---

# Random Portrait Fusion Pro

Create production-ready Chinese director cards while preserving the referenced adult character's identity. Treat every depicted person as an adult aged 23 or older. Produce prompts only; do not generate images unless the user separately requests image generation.

## Load the required references

Read these files before composing any card:

1. `references/人物层.md`
2. `references/变量池-形象神态.md`
3. `references/变量池-服装场景.md`
4. `references/变量池-摄影语言.md`
5. `references/变量池-导演路线.md`
6. `references/成像机制原则.md`
7. `references/人物美姿导演.md`
8. `references/场景名词池.md`
9. `references/场景灯光POV池.md`
10. `references/场景抽样机制.md` — large batches and all "truly random" requests

For batches of 10 or more, also use `scripts/select_batch.py` after building a candidate-plan JSON file. The script selects the final plans and reports semantic diversity; it does not write the final director-card prose.

Load the following only when the selected mode needs them:

- COS: `references/cos角色池.md`
- Candid mode: `references/同行者纪实抓拍.md`
- Profession or uniform POV: `references/职业制服POV批产.md`
- Preset packs: `references/主题包.md`

## Interpret the request

- Default to one group if the user does not specify a count.
- Respect explicit constraints first: count, aspect ratio, style, outfit, scene, direct gaze, exposure level, realism, and platform-specific phrasing.
- If reference images are unavailable in the current turn, still write the identity-lock clause so the prompt can be paired with them later; do not invent facial traits.
- Do not sample, infer, or output a facial-expression field. Never create a standalone `表情` heading. If the user explicitly supplies a facial state, preserve only that requested wording as a brief clause inside `场景与动作`; otherwise omit facial-expression language entirely.
- Do not ask follow-up questions when a coherent random card can be generated safely.
- Apply later user rules over older rules. Current hard exclusions: all leather garments, dark green, caramel, and the removed silver reflective bodysuit.
- Draw clothing colors from the complete palette in `references/变量池-服装场景.md`: rainbow pastels, vivid colors, wine red and other clean deep tones, black, white, pure gray, metallics, and color contrasts. Do not treat light-colored tops as a default constraint.
- For this user's portrait batches, sexify ordinary garments as well as special fashion pieces. Do not output an unchanged conservative shirt, sweater, hoodie, suit, sports uniform, historical outfit, or homewear set. Give each outfit one dominant skin-revealing structure plus one secondary structure, chosen from an open neckline, relaxed/off-shoulder line, open back, side-waist cutout, cropped waist, low-rise bottom, or short-skirt/shorts proportion. Keep the result wearable and fashion-led.
- If the user reports the generated bust looks too small, explicitly anchor the adult figure to the reference proportions and visually natural E–F fullness; use correctly fitted seams and drape to preserve its volume. Do not exaggerate anatomy or turn the shot into a chest close-up.
- The user's preferred candid camera language is an ordinary companion or event photographer capturing a natural moment. In generated cards and their negative prompts, omit expressions including “偷拍”“偷摄”“监视”“窥视”; use “同行者随手拍”“自然抓拍”“刚抬起手机记录的一帧” and a plausible camera position instead.

## Randomization algorithm

For each card, independently sample:

`director route × scene domain × spatial archetype × specific location × outfit family × top silhouette × bottom/one-piece silhouette × dominant material × activity × hosiery eligibility × optional leg styling × required artistic finish × lighting × color × camera angle × framing × image quality`

For random batches, actually draw choices using an available random-number generator (for example Python `secrets.SystemRandom`), following `references/场景抽样机制.md`. Do not cycle through a memorized sequence, take one venue from every category in order, or select only familiar example locations. Draw the scene domain, then the spatial archetype, then the specific venue so long lists of modern streets and travel landmarks cannot drown out unusual settings. Draw outfit family, top silhouette, bottom or one-piece silhouette, and dominant material separately before styling them as a coherent set. Follow the aspect-ratio weights in `references/变量池-摄影语言.md`, unless the user specifies a ratio. When the recent batch is visible, exclude its repeated spatial structures, specific venues, venue–activity patterns, and outfit silhouettes before sampling. If prior output is unavailable, say nothing about historical exclusions and only deduplicate what is visible.

### Start-from-zero batch procedure

When the user says “从 0 开始”“重新抽”“完整随机” or reports that a new batch is only a rewrite of the previous one, do not edit, reorder, recolor, or paraphrase old cards. Build a new pool of compact candidate plans before writing any prose:

1. Create at least `max(4 × requested_count, requested_count + 60)` candidates from the reference pools. Each candidate is only a structured combination, not a finished card.
2. Store the fields required by `scripts/select_batch.py`: `scene_domain`, `spatial_archetype`, `venue`, `facility`, `activity`, `pose_family`, `outfit_family`, `top_silhouette`, `bottom_silhouette`, `material`, and `artistic_finish`. Add any optional fields needed for later prose.
3. Do not create candidates by taking a completed card and swapping its city, color, hosiery, prop, or light. Independently draw the scene tuple, activity tuple, outfit tuple, artistic finish, and camera tuple.
4. Run `python3 scripts/select_batch.py --input <candidate.json> --output <selected.json> --count <N>`. Use `--seed` only when the user asks for a reproducible draw.
5. Write cards only from `selected.json`. Treat its `direct_gaze`, `companion_camera`, `cos_mode`, and `aspect_ratio` fields as binding unless they conflict with an explicit user instruction.
6. Read the emitted `audit`. If unique venues or outfit fingerprints are below the requested count, if adjacent fingerprint distance is below four, or if the pose/domain coverage is poor for a general random batch, expand the candidate pool and rerun instead of repairing cards by paraphrase.

For fewer than 10 cards, the script is optional, but the same semantic fingerprint and compatibility rules still apply. Mandatory identity, body, skin, and negative-prompt text is expected to repeat and must be excluded from similarity judgments.

Then run a compatibility pass:

1. Keep identity, anatomy, wardrobe construction, action, and environment physically coherent.
2. Sample scene and outfit independently. Do not require period, occupation, color, or social-setting agreement. Preserve intentional contrast instead of normalizing a surprising but viable pairing into a conventional one.
3. Convert duplicate action aliases to one semantic action before sampling so repeated wording does not overweight it. Use `references/人物美姿导演.md` for the body movement and `references/场景名词池.md` sections 44–45 for its practical purpose; combine them into one believable ongoing event.
4. Remove duplicate venue–activity pairs and near-identical visual events within a batch. Treat renamed corridors, window seats, counters, platforms, and landmark-front poses as repetitions when their spatial archetype, facility, and action remain the same. Apply the rolling cooldown in `references/场景抽样机制.md` rather than following a fixed alternation.
5. In a large batch, have about 60% of the subjects look directly into the lens, often while their hands continue a meaningful task or in the half-second after responding to the photographer. Direct gaze does not require a stationary, front-facing pose. In the remainder, keep the face visible while attention stays on the task or the surroundings. Do not create separate `视线` or `表情` headings; write gaze, head direction, reactions to the photographer, and event context only inside `场景与动作`. Do not invent facial-muscle, eyebrow, eye, or mouth-expression descriptions.
6. Trigger the companion-camera mode in `references/同行者纪实抓拍.md` independently with probability 1/5; its output vocabulary restriction applies to every card, including negative prompts. Softly blurred flowers, leaves, grasses, or other small plants may sit between the camera and the subject when they stay near the frame edges and do not cover the face, torso outline, or main action. A curtain may cross the foreground or part of the figure only when it is thin, translucent, and visibly transmits the person's facial features and body outline. Exclude opaque foreground objects, dense foliage, dirty glass, passing people, and any obstruction that hides the subject.
7. Independently draw outfit silhouettes from the `COS角色服装剪裁池` in `references/变量池-服装场景.md`, including ordinary locations. Trigger complete COS mode separately with probability 1/10 when the selected scene is outside a comic/anime convention. If the scene is 漫展 or 同人展, trigger COS unconditionally, choose one character from `references/cos角色池.md`, and make costume, hairstyle, and props recognizable while preserving the reference face. When combined with the companion-camera mode, use a plausible convention or backstage moment.
8. For 16:9, use a close portrait no wider than seven-tenths body; never use a full-body or large-environment composition.
   For every aspect ratio, reject extreme long shots, distant environmental portraits, tiny landmark poses, and any composition in which the face becomes too small to preserve identity. A full-body subject must occupy about 75–88% of image height; a seven-tenths, knee-up, or half-body subject must remain visually dominant and normally occupy about 70–90% of image height. Keep the face large enough for the reference identity, facial proportions, skin texture, and identifying mole to remain clearly readable. If a landmark or large fantasy environment conflicts with face scale, crop or compress the environment instead of moving the subject farther away.
9. Draw scene and outfit separately; keep their viable contrast. Do not force fixed match/contrast quotas that make successive batches predictable.
10. For travel and everyday scenes, draw a meaningful activity from `references/场景名词池.md` sections 44–46, pair it with one place-specific object, and catch a moment mid-action. Vary boating, picnicking, running, cycling, safely stopping an electric scooter, making art, dancing, cooking, and using mirrors; avoid repeated stationary landmark poses. Let a glance meet the lens without interrupting the action when the sampled gaze is direct. Choose practical shoes and gear when an activity demands them.
11. Finish and approve the clothing silhouette before drawing leg styling. First reject an unchanged midi skirt, ordinary long skirt, wide-leg trousers, loose full-length trousers, or other conservative lower-body silhouette; resample it or convert it into a mini, fitted shorts, a genuinely high-slit fitted long skirt, fitted ripped denim, or another fashion-led silhouette. Then determine hosiery eligibility from outfit, activity, weather, framing and footwear. Use the three-way leg-styling distribution and compatibility matrix in `references/变量池-服装场景.md`; hosiery is optional, never a repair for an unattractive outfit. Draw the hosiery family first and its compatible color second. Gray-purple or lavender hosiery is a low-frequency accent, not a neutral fallback. Do not make hosiery a body-part close-up. Garment shapes and color samples are independent: the loose draped deep-V chiffon top retains its cut and fabric description while its color varies freely.
12. Draw exactly one named artistic finish from `references/变量池-摄影语言.md` for every card. Never omit this step. Make the finish visibly legible in the final image through a physically plausible light, shadow, reflection, projection, window, plant shadow, water reflection, translucent curtain, shallow-depth plant foreground, or localized motion mechanism. Keep the real person's face and figure clearly visible; shadows, paintings, and reflections may echo or visually interact with her but may not become extra physical people. Companion-camera mode may also use `花影朦胧` or `隔帘见人` when blurred plants remain light and peripheral or the curtain is translucent enough to preserve facial features and body contours. Never place opaque fabric, dense foliage, or a large foreground object over the face, torso, or main action.
13. Build the top and bottom as one coordinated outfit rather than two independent random nouns. Run the silhouette-and-material audit, sensuality gate, hosiery audit and outfit fingerprint cooldown in `references/变量池-服装场景.md`: one visual focal point, compatible waist heights, balanced fabric weight, controlled transparency, and no competing all-over lace, metallic shine, print, and chains. Require one dominant skin-revealing structure plus one secondary structure before allowing hosiery to be added. A color, print, hosiery, shoe, or accessory change does not make a repeated silhouette new.
14. Before prose writing, store one internal fingerprint per card: `scene domain｜spatial archetype｜venue/facility｜activity｜outfit family｜top silhouette｜bottom/one-piece silhouette｜dominant material｜artistic finish`. Reject a candidate that is too close to another card in the current batch or the recent visible batch. Adjacent cards must differ in at least four fingerprint fields. If compatibility fails, resample only the conflicting field; never normalize the candidate into the same familiar corridor, short top, mini skirt, or static landmark pose used nearby.

For long batches, sample the scene plan with a real random generator and treat compatibility and exact-duplicate rejection as constraints. Do not claim mathematically uniform complete prompts: the final wording still needs creative writing and physical plausibility.

## Default to the detailed ten-block director-card format

The user's current preference is the long, rich, self-contained ten-block card below, even for large random batches. Give each card its own full identity lock and negative prompt so it can be copied alone. Do not add an expression block. In `场景与动作`, describe the ongoing activity, body movement, head direction, and gaze without inventing facial affect; in `摄影质感` and `光线与色彩`, describe the chosen artistic finish and how its real light or optics work. Keep the subject visually dominant and the referenced face large enough for identity details to remain readable. Use compact records only if the user explicitly requests a short list, overview, table, or simple description.

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
7. `场景与动作` — specific place + pure action + body/head direction + gaze + unforced moment
8. `光线与色彩`
9. `摄影质感` — capture quality + lens + camera angle + explicit subject occupancy + the required named artistic finish with a clearly legible face + refined editorial atmosphere without commercial studio polish
10. `负面提示词`

Do not add a standalone gaze section. Avoid blunt phrases such as “露出……” when describing styling; express visible skin through design language such as “肩颈与锁骨线条清晰”“腰侧线条清晰”“背部线条完整”“腿部比例得到延展”. Do not append stock disclaimers like “完整穿着、不暴露内衣、不走光” unless the user explicitly asks for them; enforce those constraints silently through garment construction and the negative prompt.

Never output a `表情` block and never replace it with an unlabeled expression sentence. Keep direct gaze, looking away, turning the head, and reactions to the photographer inside `场景与动作` because they are action and direction, not an expression category.

## Quality bar

- Keep one clear event, one readable action beat, and one primary interaction object.
- Describe a plausible main light and restrained secondary reflections.
- Prefer real skin, fabric folds, loose hairs, natural weight, localized motion blur, and capture-medium artifacts over polished AI beauty language.
- Keep face visibility and face scale high. Exclude closed eyes, squinting, face-covering, downward poses that hide facial features, extreme long shots, tiny people, and excessive empty environment.
- Never imply nudity, transparent exposure of intimate anatomy, wardrobe malfunction, fetish framing, or a minor. Keep sensuality fashion-led and non-explicit.
- Write each card as a directly usable prompt, not as notes about the randomization process.

## Detailed batch output

When producing detailed cards, number them and give each a short route title. Keep every card self-contained, including the identity lock and negative prompt. Do not replace repeated mandatory identity details with “同上”.
