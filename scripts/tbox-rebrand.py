#!/usr/bin/env python3
"""把上游 tvbox-silicon 换成 TBox 的壳：品牌名、配色、bundle id。

在 CI 里跑（checkout 上游之后、xcodegen 之前），也可本地跑。
用法: python3 scripts/tbox-rebrand.py <源码根目录>
"""
import io, os, sys

BRAND = "TBox"
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."


def read(p):
    return io.open(p, encoding="utf-8", errors="surrogateescape").read()


def write(p, s):
    io.open(p, "w", encoding="utf-8", errors="surrogateescape").write(s)


def replace_in(paths, old, new, skip_lower=True):
    n = 0
    for p in paths:
        if not os.path.isfile(p):
            continue
        s = read(p)
        if old not in s:
            continue
        write(p, s.replace(old, new))
        n += s.count(old)
    return n


# ── 1. InfoPlist：应用显示名 ────────────────────────────────
locs = ["en", "zh-Hans", "zh-Hant", "ja"]
n = 0
for loc in locs:
    p = os.path.join(ROOT, "App/Resources", loc + ".lproj/InfoPlist.strings")
    if os.path.isfile(p):
        s = read(p)
        n += s.count("映匣") + s.count("Yingxia")
        write(p, s.replace("映匣", BRAND).replace("Yingxia", BRAND))
print("InfoPlist: %d 处" % n)

# ── 2. 语言表：key 与译文 ───────────────────────────────────
n = 0
for loc in locs:
    p = os.path.join(ROOT, "Sources/TVCore/Resources", loc + ".lproj/Localizable.strings")
    if os.path.isfile(p):
        s = read(p)
        n += s.count("映匣") + s.count("Yingxia")
        write(p, s.replace("映匣", BRAND).replace("Yingxia", BRAND))
print("Localizable: %d 处" % n)

# ── 3. App 下所有 Swift / txt ──────────────────────────────
swift = []
for dp, _, fn in os.walk(os.path.join(ROOT, "App")):
    for f in fn:
        if f.endswith((".swift", ".txt", ".md")):
            swift.append(os.path.join(dp, f))
n = replace_in(swift, "Yingxia", BRAND)
print("App/*.swift: %d 处" % n)

# ── 4. 配色：classic 的深色底对齐 TBox 的灰黑 ─────────────
p = os.path.join(ROOT, "App/ColorThemes.swift")
if os.path.isfile(p):
    s = read(p)
    before = s
    s = s.replace(
        "backdropDark: Color(red: 0.020, green: 0.035, blue: 0.090)",
        "backdropDark: Color(red: 0.055, green: 0.055, blue: 0.065)"
    ).replace(
        "surfaceDark: Color(red: 0.075, green: 0.105, blue: 0.19)",
        "surfaceDark: Color(red: 0.110, green: 0.110, blue: 0.122)"
    ).replace(
        "tvSurface: Color(red: 0.09, green: 0.125, blue: 0.22), tvRaised: Color(red: 0.13, green: 0.175, blue: 0.29)",
        "tvSurface: Color(red: 0.095, green: 0.095, blue: 0.106), tvRaised: Color(red: 0.145, green: 0.145, blue: 0.158)"
    )
    if s != before:
        write(p, s)
        print("ColorThemes: classic 已改为灰黑系")
    else:
        print("ColorThemes: 未匹配（可能上游已变），跳过")

# ── 5. project.yml：显示名 + bundle id ────────────────────
p = os.path.join(ROOT, "project.yml")
if os.path.isfile(p):
    s = read(p)
    before = s
    s = s.replace("INFOPLIST_KEY_CFBundleDisplayName: Yingxia", "INFOPLIST_KEY_CFBundleDisplayName: " + BRAND)
    s = s.replace("CFBundleDisplayName: Yingxia", "CFBundleDisplayName: " + BRAND)
    s = s.replace("com.jo32.yingxia.ios", "com.phouse.tvbox.ios")
    s = s.replace("com.jo32.yingxia.macos", "com.phouse.tvbox.macos")
    if s != before:
        write(p, s)
        print("project.yml: 显示名与 bundle id 已改")
    else:
        print("project.yml: 未匹配，跳过")

# ── 6. 自检 ────────────────────────────────────────────────
left = 0
for dp, _, fn in os.walk(os.path.join(ROOT, "App")):
    for f in fn:
        if f.endswith((".swift", ".strings", ".txt")):
            s = read(os.path.join(dp, f))
            left += s.count("Yingxia") + s.count("映匣")
print("\n残留品牌名（应为 0，yingxia:// 等小写技术标识不计）: %d" % left)
