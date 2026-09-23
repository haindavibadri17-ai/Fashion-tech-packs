"""Heuristic garment classifier.

Pure-vision garment classification from a single photo is unreliable, so the
agent uses image structure (foreground aspect ratio, row-width profile and
bottom-gap detection) for a best-effort guess, and always lets the user
override it on the form. The confidence and reason are reported
transparently in the generated pack.
"""


def classify(info):
    aspect = info["aspect"]
    prof = info["profile"]
    top_w, mid_w, bot_w = prof["top"], prof["mid"], prof["bottom"]
    bottom_gap = info.get("bottom_gap", False)
    reasons = []

    flare = bot_w / max(top_w, 1e-6)
    sleeves = top_w / max(mid_w, 1e-6)

    # Strong flare (bottom much wider than top) -> dress
    if flare > 1.30:
        reasons.append("strong A-line flare (bottom %d%% wider than top)"
                       % (int((flare - 1) * 100)))
        return "dress", "medium", "; ".join(reasons)

    # Two separate columns at the bottom (legs with a gap between them)
    if bottom_gap:
        if aspect < 0.8:
            reasons.append("paired lower columns with a centre gap, tall silhouette "
                           "(aspect %.2f)" % aspect)
            return "pants", "low", "; ".join(reasons)
        reasons.append("paired lower columns with a centre gap, short silhouette "
                       "(aspect %.2f)" % aspect)
        return "shorts", "low", "; ".join(reasons)

    # Wide shoulder/sleeve band relative to the body -> sleeved top
    if sleeves > 1.12:
        reasons.append("wide shoulder/sleeve band at the top (top %.2f vs mid %.2f)"
                       % (top_w, mid_w))
        if aspect >= 0.95:
            return "top", "low", "; ".join(reasons) + " — tall silhouette suggests long sleeves"
        return "tshirt", "low", "; ".join(reasons) + " — square silhouette suggests short sleeves"

    # Tall narrow silhouette (no leg gap)
    if aspect < 0.75:
        if flare > 1.15:
            reasons.append("tall silhouette flaring at the hem (bottom %d%% wider than "
                           "top, aspect %.2f)" % (int((flare - 1) * 100), aspect))
            return "dress", "low", "; ".join(reasons)
        reasons.append("tall silhouette with constant width and a single continuous hem "
                       "(aspect %.2f) — flat-laid top with sleeves down" % aspect)
        return "tshirt", "low", "; ".join(reasons)

    # Wide bottom, shortish -> skirt
    if aspect < 1.0 and bot_w > top_w * 1.15:
        reasons.append("wider bottom than top in a short silhouette (aspect %.2f)" % aspect)
        return "skirt", "low", "; ".join(reasons)

    # A single continuous wide hem, roughly square -> flat-laid top
    reasons.append("single continuous hem, roughly square silhouette (aspect %.2f)" % aspect)
    return "tshirt", "low", "; ".join(reasons) + " — please confirm garment type"
