import re

# 1. CSS brace balance
with open("src/lever_action/static/css/style.css") as f:
    css = f.read()
opens = css.count("{")
closes = css.count("}")
print(
    f"CSS braces: {opens} open, {closes} close - {'PASS' if opens == closes else 'FAIL'}"
)

# 2. Template HTML tag balance
with open("src/lever_action/templates/index.tpl") as f:
    tpl = f.read()
clean = re.sub(r"<style>.*?</style>", "", tpl, flags=re.DOTALL)
clean = re.sub(r"<script.*?src=.*?</script>", "", clean, flags=re.DOTALL)
tags = re.findall(r"<(\/?)(\w+)(?:\s[^>]*)?>", clean)
stack = []
errors = []
for close, tag in tags:
    if tag in ("br", "hr", "img", "input", "meta", "link"):
        continue
    if close == "/":
        if stack and stack[-1] == tag:
            stack.pop()
        else:
            errors.append(
                f"HTML mismatch: </{tag}> but expected </{stack[-1] if stack else 'nothing'}>"
            )
    else:
        stack.append(tag)
if stack:
    errors.append(f"HTML unclosed tags: {stack}")
if not errors:
    print("HTML tags: PASS (all balanced)")
else:
    for e in errors:
        print(e)

# 3. Verify resetChat SVG matches template welcome SVG
with open("src/lever_action/static/js/app.js") as f:
    js = f.read()
tpl_svg = re.search(r'<svg class="welcome-icon".*?</svg>', tpl, re.DOTALL)
js_svg = re.search(r'<svg class="welcome-icon".*?</svg>', js, re.DOTALL)
if tpl_svg and js_svg:
    t = re.sub(r"\s+", " ", tpl_svg.group(0))
    j = re.sub(r"\s+", " ", js_svg.group(0))
    print(f"SVG match: {'PASS' if t == j else 'FAIL'}")
else:
    print(f"SVG match: FAIL (template={tpl_svg is not None}, js={js_svg is not None})")

# 4. Verify all onclick handlers reference existing functions
onclicks = re.findall(r'onclick="([^"]+)"', tpl)
funcs_in_js = set(re.findall(r"^function\s+(\w+)", js, re.MULTILINE))
missing = []
for oc in onclicks:
    fn = oc.split("(")[0]
    if fn not in funcs_in_js:
        missing.append(fn)
if missing:
    print(f"JS missing functions: {missing}")
else:
    print(f"onclick handlers: PASS ({len(onclicks)} all found)")

# 5. Verify all IDs in template have corresponding CSS rules
tpl_ids = set(re.findall(r'id="(\w+)"', tpl))
css_ids = set(re.findall(r"#(\w+)", css))
missing_css = tpl_ids - css_ids
if missing_css:
    print(f"IDs without CSS: {missing_css}")
else:
    print(f"IDs with CSS: PASS ({len(tpl_ids)} all styled)")

# 6. Check for any stray old blue colors
old_colors = [
    "#0078d4",
    "#1a8ae8",
    "#9b6ddf",
    "#b088f5",
    "#d43030",
    "#e84040",
    "#d4942a",
    "#e8ad3a",
]
found_old = []
for c in old_colors:
    if c in css:
        found_old.append(f"{c} in CSS")
    if c in js:
        found_old.append(f"{c} in JS")
if found_old:
    print(f"FAIL: old colors still present: {found_old}")
else:
    print("Old color check: PASS (none found)")

# 7. Check pygments.css exists and has content
with open("src/lever_action/static/css/pygments.css") as f:
    pyg = f.read()
print(f"pygments.css: {'PASS' if len(pyg) > 100 else 'FAIL'} ({len(pyg)} bytes)")

# 8. Verify CSS var cross-reference
defined = set(re.findall(r"--([\w-]+)\s*:", css))
used = set(re.findall(r"var\(--([\w-]+)", css))
missing_var = used - defined - {"dot-color"}  # dot-color is set inline by JS
extra_var = defined - used
if missing_var:
    print(f"FAIL: used but not defined: {missing_var}")
else:
    print("CSS vars: PASS (all used vars defined)")
if extra_var:
    print(f"FAIL: defined but not used: {extra_var}")
else:
    print("CSS vars: PASS (no unused vars)")

# 9. Check for duplicate selectors
selectors = re.findall(r"^([.#\[\w\s>+:*-]+)\s*\{", css, re.MULTILINE)
dupes = {s: selectors.count(s) for s in selectors if selectors.count(s) > 1}
if dupes:
    print(f"FAIL: duplicate selectors: {dupes}")
else:
    print("Duplicate selectors: PASS (none)")

# 10. Check for contain: content
if "contain: content" in css:
    print("FAIL: contain: content found (WebView2 killer)")
else:
    print("contain: content: PASS (not present)")

print("\n=== AUDIT COMPLETE ===")
