"""Industry knowledge base used by the tech-pack agent.

All garment measurements are FLAT (garment laid flat, in centimetres),
based on industry-standard base sizes and grading. Values marked "TBC"
must be confirmed against the approved sample before bulk production.
"""

# Order of the full size ladder. User-requested ranges are windows into this.
SIZE_LADDER = ["XS", "S", "M", "L", "XL", "XXL"]

STITCH_SPECS = [
    ["301", "Lockstitch (single/double needle)", "12–14 SPC", "Construction, topstitch, plackets, zips"],
    ["404", "4-thread overlock", "12 SPC, 5 mm edge coverage", "Knit & woven seams (interior)"],
    ["406/407", "2-needle coverstitch (flat / tubular)", "10–12 SPC", "Hems, cuffs, sleeve hems"],
    ["504", "Flatlock (double needle)", "8–10 SPC", "Shoulder & side seams on jersey (optional)"],
    ["69/78", "Bar-tack (double/diamond)", "4×4 min. at stress points", "Pocket corners, belt loops, yokes, zips"],
    ["406 (chain)", "Chainstitch (hem)", "12–14 SPC", "Denim & trouser hems (optional)"],
]

THREAD_SPEC = [
    ["Main thread", "100% polyester core-spun, Tex 70, colour-matched (shade card attached)"],
    ["Bobbin thread", "100% polyester, Tex 40"],
    ["Topstitch thread", "Tex 70, contrast or matching per style (denim: golden)"],
    ["Bartack thread", "Tex 70 × 3 plies, reinforced"],
    ["Tension", "4–6 (balanced), verify per machine at start of run"],
    ["Needle", "Ballpoint 75/11 (knits) · Sharp 90/14 (denim/wovens)"],
]

PACKAGING_BASE = [
    ["Main label", "70D woven, 60 × 30 mm — brand, composition, size", "Centre back neck, 1–2 cm below collar"],
    ["Care label", "60D woven, 40 × 20 mm — ISO 3758 symbols + care text", "Left side seam, 8–10 cm above hem"],
    ["Size label", "Printed on 150 gsm paper, 30 × 15 mm, laminated", "Affixed to main label or left side seam"],
    ["Hangtag", "350 gsm FSC card, 90 × 60 mm, 20 mm string + safety fastener", "Attached to main label"],
    ["Poly bag", "45 × 60 cm, 0.03 mm, matte, air-release holes", "One per garment, hangtag tucked into side seam"],
    ["Carton", "Double-wall, 50 pcs mixed sizes & colourways, max gross 18 kg", "Carton label: style, size, colour, weight, PO ref, country of origin"],
    ["Carton documentation", "MSDS + fabric composition label", "Fixed to outside of carton"],
    ["Sample packaging", "As above + 'SAMPLE' sticker, size run clearly marked", "For approval only"],
]

SAMPLE_FEEDBACK_ROWS = [
    ["1", "Overall fit", "Compare finished sample against size M specifications", "—", "—", "Open"],
    ["2", "Size run", "Verify all sizes (grading) against measurement table before approval", "—", "—", "Open"],
    ["3", "Colour", "Match against approved lab dip / swatch under D65 light", "—", "—", "Open"],
    ["4", "Fabric hand-feel & weight", "Confirm GSM and hand-feel match approved swatch", "—", "—", "Open"],
    ["5", "Trims", "Confirm trims (thread, fasteners, labels) against BOM", "—", "—", "Open"],
]

APPROVALS = [
    ["Merchandiser", "", "", ""],
    ["Technical / Product", "", "", ""],
    ["Production / Factory", "", "", ""],
]

ARTWORK_SPEC = [
    ["Logo — left chest", "Print or embroidery, standard size 10 × 10 cm, 20 cm from shoulder seam, 12 cm below collar (TBC)", "Vector EPS/AI, spot colours"],
    ["Back artwork (if applicable)", "Standard size 25 × 35 cm, centred, 15 cm below collar (TBC)", "Vector EPS/AI"],
    ["All-over / pattern (if applicable)", "Repeat dimensions per artwork file, aligned to centre front", "Repeat chart with registration marks"],
    ["Label & hangtag artwork", "Per label supplier spec", "Vector, 300 dpi min. raster"],
]

ARTWORK_REQUIREMENTS = (
    "Artwork must be supplied as vector (EPS/AI/SVG) with spot colours defined; "
    "raster minimum 300 dpi at final size. Placement measured from centre front, "
    "shoulder seam and hem on the finished garment. Artwork files to be attached — TBC."
)


def size_table(base: float, step: float, sizes, base_size: str = "M"):
    """Build a list of size values (rounded to 0.5) from a base value + step."""
    i_base = SIZE_LADDER.index(base_size)
    vals = []
    for s in sizes:
        i = SIZE_LADDER.index(s)
        v = base + (i - i_base) * step
        # round to nearest 0.5
        v = round(v * 2) / 2
        vals.append(int(v) if v == int(v) else v)
    return vals


CATEGORIES = {
    "tshirt": {
        "label": "T-Shirt (short sleeve, crew neck)",
        "code_prefix": "TS",
        "flat": "tshirt",
        "fabric": {
            "type": "Single jersey knit",
            "composition": "100% combed ring-spun cotton (24/1 single)",
            "weight": "160–180 GSM",
            "finish": "Mercerised, enzyme-washed, pre-shrunk",
            "lining": "None",
            "supplier": "TBC — attach approved swatch & lab dip card",
            "colorfastness": "Grade 4+ to rub & wash (ISO 105-X12, C06)",
            "shrinkage": "≤ 3% after 3 washes",
        },
        "consumption": "1.3 m per piece (size M, 145 cm usable width, est.)",
        "measurements": [
            ("chest", "Chest (armpit to armpit)", 54, 3.0, 0.5, 1.0, "Horizontal, 2.5 cm below armhole seam, garment flat"),
            ("length", "Length (shoulder to hem)", 69, 1.5, 1.0, 1.0, "From high point of shoulder to hem"),
            ("shoulder", "Shoulder (seam to seam)", 46, 1.5, 0.5, 0.5, "Across shoulder seam, centre back to centre front"),
            ("sleeve", "Sleeve (shoulder to hem)", 21, 1.5, 1.0, 1.0, "From shoulder tip to sleeve hem, mid-seam"),
            ("neck_w", "Neck width", 20, 1.0, 0.5, 0.5, "Across neckline opening at shoulder seam"),
            ("neck_d", "Neck depth", 8, 0.5, 0.5, 0.5, "From shoulder seam to lowest neckline point"),
        ],
        "bom": [
            ["Outer fabric", "100% combed ring-spun cotton single jersey, 160–180 GSM", "1.3 m (M)"],
            ["1×1 rib (neckline)", "5.5 cm wide, colour-matched to body", "0.08 m"],
            ["Main thread", "Polyester Tex 70, colour-matched", "1 roll / 30 pcs (shared)"],
            ["Main label", "Woven 70D, 60 × 30 mm", "1"],
            ["Care + size label", "Woven 60D, 40 × 20 mm", "1"],
            ["Hangtag", "350 gsm FSC card 90 × 60 mm + string + fastener", "1"],
            ["Poly bag", "45 × 60 cm, 0.03 mm matte", "1"],
        ],
        "construction": [
            ["Shoulder seam", "406 2-needle coverstitch (or 504 flatlock)", "12 SPC, SA 1.0 cm"],
            ["Side & underarm seams", "406 2-needle coverstitch", "12 SPC, SA 1.0 cm"],
            ["Sleeve hem", "406/407 2-needle coverstitch, 5 mm fold", "10 SPC"],
            ["Body hem", "406/407 2-needle coverstitch, 5 mm fold", "10 SPC"],
            ["Neckline", "1×1 rib binding, overlocked then lockstitched", "301, 14 SPC"],
            ["Bar-tacks", "None required", "—"],
        ],
        "details": [
            "Crew neckline with 1×1 rib binding, folded & stitched",
            "Set-in short sleeve, coverstitched hem",
            "Double-needle (coverstitch) hem on body",
            "No pockets, no closure",
            "Embellishment: none (logo left chest — TBC)",
        ],
    },
    "top": {
        "label": "Top (long sleeve, crew neck)",
        "code_prefix": "TP",
        "flat": "top",
        "fabric": {
            "type": "Single jersey / interlock knit",
            "composition": "95% cotton / 5% elastane",
            "weight": "180–210 GSM",
            "finish": "Soft-washed, pre-shrunk",
            "lining": "None",
            "supplier": "TBC — attach approved swatch & lab dip card",
            "colorfastness": "Grade 4+ to rub & wash (ISO 105-X12, C06)",
            "shrinkage": "≤ 3% after 3 washes",
        },
        "consumption": "1.5 m per piece (size M, 145 cm usable width, est.)",
        "measurements": [
            ("chest", "Chest (armpit to armpit)", 51, 3.0, 0.5, 1.0, "Horizontal, 2.5 cm below armhole seam, garment flat"),
            ("length", "Length (shoulder to hem)", 66, 1.5, 1.0, 1.0, "From high point of shoulder to hem"),
            ("shoulder", "Shoulder (seam to seam)", 41, 1.5, 0.5, 0.5, "Across shoulder seam"),
            ("sleeve", "Sleeve (shoulder to cuff)", 58, 1.5, 1.0, 1.0, "From shoulder tip to cuff, mid-seam"),
            ("neck_w", "Neck width", 19, 1.0, 0.5, 0.5, "Across neckline opening"),
            ("neck_d", "Neck depth", 8, 0.5, 0.5, 0.5, "From shoulder seam to lowest neckline point"),
        ],
        "bom": [
            ["Outer fabric", "95% cotton / 5% elastane jersey, 180–210 GSM", "1.5 m (M)"],
            ["1×1 rib (neckline)", "5.5 cm wide, colour-matched", "0.08 m"],
            ["1×1 rib (cuffs)", "6 cm wide, colour-matched", "0.15 m"],
            ["Main thread", "Polyester Tex 70, colour-matched", "1 roll / 30 pcs (shared)"],
            ["Main label", "Woven 70D, 60 × 30 mm", "1"],
            ["Care + size label", "Woven 60D, 40 × 20 mm", "1"],
            ["Hangtag", "350 gsm FSC card 90 × 60 mm + string + fastener", "1"],
            ["Poly bag", "45 × 60 cm, 0.03 mm matte", "1"],
        ],
        "construction": [
            ["Shoulder seam", "406 2-needle coverstitch", "12 SPC, SA 1.0 cm"],
            ["Side & underarm seams", "406 2-needle coverstitch", "12 SPC, SA 1.0 cm"],
            ["Sleeve seam", "406 2-needle coverstitch", "12 SPC, SA 1.0 cm"],
            ["Cuff & body hem", "406/407 2-needle coverstitch, 5 mm fold", "10 SPC"],
            ["Neckline", "1×1 rib binding, overlocked then lockstitched", "301, 14 SPC"],
            ["Bar-tacks", "None required", "—"],
        ],
        "details": [
            "Crew neckline with 1×1 rib binding",
            "Long set-in sleeve with ribbed cuff",
            "Double-needle (coverstitch) hem",
            "No pockets, no closure",
            "Embellishment: none (logo left chest — TBC)",
        ],
    },
    "shirt": {
        "label": "Shirt (long sleeve, button-down)",
        "code_prefix": "SH",
        "flat": "shirt",
        "fabric": {
            "type": "2/1 cotton twill / poplin",
            "composition": "100% cotton (30/1)",
            "weight": "110–130 GSM",
            "finish": "Sanforised, 100% combed, peached finish (optional)",
            "lining": "None",
            "supplier": "TBC — attach approved swatch & lab dip card",
            "colorfastness": "Grade 4+ to rub & wash (ISO 105-X12, C06)",
            "shrinkage": "≤ 1% (sanforised)",
        },
        "consumption": "1.8 m per piece (size M, 145 cm usable width, est.)",
        "measurements": [
            ("chest", "Chest (armpit to armpit)", 54, 3.0, 0.5, 1.0, "Horizontal, 2.5 cm below armhole seam"),
            ("waist", "Waist (armpit to armpit)", 51, 3.0, 0.5, 1.0, "Horizontal, natural waist line"),
            ("length", "Length (shoulder to hem)", 71, 1.5, 1.0, 1.0, "From high point of shoulder to hem, centre back"),
            ("shoulder", "Shoulder (seam to seam)", 46, 1.5, 0.5, 0.5, "Across shoulder seam"),
            ("sleeve", "Sleeve (shoulder to cuff)", 60, 1.5, 1.0, 1.0, "From shoulder tip to cuff, mid-seam"),
            ("placket", "Placket width", 5.5, 0.0, 0.3, 0.5, "Front placket, finished width"),
            ("collar", "Collar depth", 3.0, 0.0, 0.3, 0.5, "Collar band depth, centre back"),
        ],
        "bom": [
            ["Outer fabric", "100% cotton 2/1 twill / poplin, 110–130 GSM", "1.8 m (M)"],
            ["Buttons", "4-hole, 15 mm, matching or contrast", "6"],
            ["Placket facing", "Self-fabric", "0.5 m"],
            ["Main thread", "Polyester Tex 70, colour-matched", "1 roll / 30 pcs (shared)"],
            ["Main label", "Woven 70D, 60 × 30 mm", "1"],
            ["Care + size label", "Woven 60D, 40 × 20 mm", "1"],
            ["Hangtag", "350 gsm FSC card 90 × 60 mm + string + fastener", "1"],
            ["Poly bag", "45 × 60 cm, 0.03 mm matte", "1"],
        ],
        "construction": [
            ["Body & sleeve seams", "404 4-thread overlock", "12 SPC, SA 1.2 cm"],
            ["Collar & band", "301 lockstitch", "14 SPC"],
            ["Placket & buttonholes", "301 lockstitch", "14 SPC"],
            ["Cuffs", "301 lockstitch", "14 SPC, SA 1.2 cm"],
            ["Hem", "301 lockstitch, 1.5 cm fold", "12 SPC"],
            ["Topstitching", "301 double-needle", "2.5 mm offset, 12 SPC"],
        ],
        "details": [
            "Spread collar, self-fabric under-collar",
            "Full front button placket, 6 buttons",
            "Single-needle button cuff",
            "Chest pocket: none (optional — TBC)",
            "Embellishment: none (logo left chest — TBC)",
        ],
    },
    "hoodie": {
        "label": "Hoodie (long sleeve, zip or pullover)",
        "code_prefix": "HD",
        "flat": "hoodie",
        "fabric": {
            "type": "Fleece (loopback) knit",
            "composition": "80% cotton / 20% polyester",
            "weight": "300–350 GSM",
            "finish": "Inner brushed, garment-dyed option",
            "lining": "None (pocket optional lining)",
            "supplier": "TBC — attach approved swatch & lab dip card",
            "colorfastness": "Grade 4+ to rub & wash (ISO 105-X12, C06)",
            "shrinkage": "≤ 3% after 3 washes",
        },
        "consumption": "1.9 m per piece (size M, 145 cm usable width, est.)",
        "measurements": [
            ("chest", "Chest (armpit to armpit)", 55, 3.5, 0.5, 1.0, "Horizontal, 2.5 cm below armhole seam"),
            ("waist", "Waist (armpit to armpit)", 52, 3.0, 0.5, 1.0, "Horizontal, natural waist line"),
            ("length", "Length (shoulder to hem)", 65, 1.5, 1.0, 1.0, "From high point of shoulder to hem"),
            ("shoulder", "Shoulder (seam to seam)", 45, 1.5, 0.5, 0.5, "Across shoulder seam"),
            ("sleeve", "Sleeve (shoulder to cuff)", 57, 1.5, 1.0, 1.0, "From shoulder tip to cuff, mid-seam"),
            ("pocket", "Kangaroo pocket width", 24, 1.0, 0.5, 1.0, "Pocket opening, top edge"),
            ("hood", "Hood height", 12, 0.5, 0.5, 0.5, "From neckline seam to top of hood, laid flat"),
        ],
        "bom": [
            ["Outer fabric", "80/20 cotton-poly fleece, 300–350 GSM", "1.9 m (M)"],
            ["2×2 rib (cuffs)", "7 cm wide, colour-matched", "0.18 m"],
            ["2×2 rib (hem)", "10 cm wide, colour-matched", "0.22 m"],
            ["Drawcord", "8 mm round, colour-matched, 24 cm each", "2"],
            ["Cord locks", "8 mm, colour-matched", "2"],
            ["Zipper (if zip-up)", "YKK #5, 65 cm, colour-matched", "1"],
            ["Main thread", "Polyester Tex 70, colour-matched", "1 roll / 30 pcs (shared)"],
            ["Main label", "Woven 70D, 60 × 30 mm", "1"],
            ["Care + size label", "Woven 60D, 40 × 20 mm", "1"],
            ["Hangtag", "350 gsm FSC card 90 × 60 mm + string + fastener", "1"],
            ["Poly bag", "45 × 60 cm, 0.03 mm matte", "1"],
        ],
        "construction": [
            ["Body & sleeve seams", "404 4-thread overlock (or 406)", "12 SPC, SA 1.2 cm"],
            ["Hood", "404 overlock + 301 topstitch", "12 SPC, SA 1.0 cm"],
            ["Kangaroo pocket", "301 topstitch × 2 lines", "12 SPC"],
            ["Cuffs & hem (rib)", "406 2-needle coverstitch", "12 SPC"],
            ["Zipper (if zip-up)", "301 lockstitch", "14 SPC, SA 1.0 cm"],
            ["Bar-tacks", "69 at pocket corners & zip ends", "4×4 min."],
        ],
        "details": [
            "Double-layer hood, single layer at back",
            "Kangaroo pocket, 24 cm opening",
            "8 mm round drawcord with cord locks",
            "Ribbed cuffs (7 cm) & hem (10 cm), 2×2 rib",
            "Closure: pullover (zip-up option — TBC)",
        ],
    },
    "jacket": {
        "label": "Jacket / outerwear (zip front)",
        "code_prefix": "JT",
        "flat": "jacket",
        "fabric": {
            "type": "Polyester twill / ripstop",
            "composition": "100% polyester (DWR, PFC-free)",
            "weight": "230–280 GSM",
            "finish": "Durable water repellent (DWR), PFC-free",
            "lining": "100% polyester crepe, 65–75 GSM",
            "supplier": "TBC — attach approved swatch & lab dip card",
            "colorfastness": "Grade 4+ to rub & wash (ISO 105-X12, C06)",
            "shrinkage": "≤ 2%",
        },
        "consumption": "2.2 m per piece (size M, 145 cm usable width, est.)",
        "measurements": [
            ("chest", "Chest (armpit to armpit)", 55, 3.5, 0.5, 1.0, "Horizontal, 2.5 cm below armhole seam"),
            ("waist", "Waist (armpit to armpit)", 52, 3.0, 0.5, 1.0, "Horizontal, natural waist line"),
            ("length", "Length (shoulder to hem)", 64, 1.5, 1.0, 1.0, "From high point of shoulder to hem, centre back"),
            ("shoulder", "Shoulder (seam to seam)", 46, 2.0, 0.5, 0.5, "Across shoulder seam"),
            ("sleeve", "Sleeve (shoulder to cuff)", 61, 2.0, 1.0, 1.5, "From shoulder tip to cuff, mid-seam"),
            ("placket", "Placket width", 6.5, 0.0, 0.5, 0.5, "Front placket, finished width"),
        ],
        "bom": [
            ["Outer fabric", "100% polyester twill/ripstop, 230–280 GSM, DWR", "2.2 m (M)"],
            ["Lining fabric", "100% polyester crepe, 65–75 GSM", "1.6 m (M)"],
            ["Zipper", "YKK #5, 65 cm, 2-way, colour-matched", "1"],
            ["Main thread", "Polyester Tex 70, colour-matched", "1 roll / 30 pcs (shared)"],
            ["Main label", "Woven 70D, 60 × 30 mm", "1"],
            ["Care + size label", "Woven 60D, 40 × 20 mm", "1"],
            ["Hangtag", "350 gsm FSC card 90 × 60 mm + string + fastener", "1"],
            ["Poly bag", "45 × 60 cm, 0.03 mm matte", "1"],
        ],
        "construction": [
            ["Body & sleeve seams", "404 4-thread overlock", "12 SPC, SA 1.2 cm"],
            ["Zipper attachment", "301 lockstitch", "14 SPC, SA 1.0 cm"],
            ["Sleeve head", "301 lockstitch, eased in", "12 SPC"],
            ["Hem", "406 coverstitch, 2 cm fold", "12 SPC"],
            ["Pockets", "301 topstitch + 404 interior", "12 SPC"],
            ["Bar-tacks", "69 at shoulder, pocket corners, zip ends", "4×4 min."],
        ],
        "details": [
            "Stand collar",
            "Full front 2-way zipper, #5 YKK",
            "Angled welt pockets ×2",
            "Lined body & sleeves",
            "Embellishment: none (logo left chest — TBC)",
        ],
    },
    "pants": {
        "label": "Jeans / trousers (button fly)",
        "code_prefix": "JN",
        "flat": "pants",
        "fabric": {
            "type": "Denim, 100% cotton",
            "composition": "100% cotton (14/1 × 7/1 warp, 7/1 fill)",
            "weight": "300–360 GSM (12–13.5 oz)",
            "finish": "Sanforised; garment wash per approved wash recipe",
            "lining": "None",
            "supplier": "TBC — attach approved swatch, wash recipe & lab dip",
            "colorfastness": "Grade 4 to wash, 3–4 to rub (denim standard)",
            "shrinkage": "≤ 3% (sanforised, length)",
        },
        "consumption": "2.3 m per piece (size M, 145 cm usable width, est.)",
        "measurements": [
            ("waist", "Waist (armpit to armpit)", 42, 2.5, 0.5, 1.0, "Across waistband, flat, button up"),
            ("hip", "Hip (armpit to armpit)", 53, 3.0, 0.5, 1.0, "10 cm below waistband, horizontal"),
            ("inseam", "Inseam", 80, 2.0, 1.0, 1.0, "From crotch point to hem, inner seam"),
            ("outseam", "Outseam", 95, 2.0, 1.0, 1.0, "From waist to hem, outer seam"),
            ("rise", "Front rise", 28, 0.5, 1.0, 1.0, "From waist at front centre to crotch point"),
            ("thigh", "Thigh (per leg)", 31, 2.0, 0.5, 1.0, "5 cm below crotch, horizontal, per leg"),
            ("hem", "Hem width", 17.5, 1.0, 0.5, 1.0, "Hem opening, flat"),
        ],
        "bom": [
            ["Denim fabric", "100% cotton denim, 300–360 GSM", "2.3 m (M)"],
            ["Button", "Metal, 38 mm, antique or raw per style", "1"],
            ["Rivets", "3.5 mm, colour-matched", "5"],
            ["Belt loops", "Self-denim, 1.2 cm wide", "4"],
            ["Bartack thread", "Polyester Tex 70 × 3", "Shared"],
            ["Main thread", "Polyester Tex 70, golden/contrast per style", "1 roll / 30 pcs (shared)"],
            ["Main label", "Woven 70D, 60 × 30 mm, back yoke", "1"],
            ["Care + size label", "Woven 60D, 40 × 20 mm, left side seam", "1"],
            ["Hangtag", "350 gsm FSC card 90 × 60 mm + string + fastener", "1"],
            ["Poly bag", "45 × 60 cm, 0.03 mm matte", "1"],
        ],
        "construction": [
            ["Seams", "404 4-thread overlock (interior)", "12 SPC, SA 1.2 cm"],
            ["Topstitching", "301 double-needle, contrast", "12 SPC, 2.5 mm offset"],
            ["Button fly", "301 lockstitch, 4-stitch fly", "14 SPC"],
            ["Bar-tacks", "69 at pocket corners, belt loops, fly end", "4×4 min."],
            ["Rivets", "Set at pocket stress points & fly", "3.5 mm × 5"],
            ["Hem", "301 lockstitch, 1.5 cm fold, double-needle", "12 SPC"],
        ],
        "details": [
            "5-pocket style with curved front pockets + coin pocket",
            "Button closure, 38 mm metal button",
            "4 belt loops, 1.2 cm",
            "Back yoke with centre-back seam",
            "Rivets at all stress points",
        ],
    },
    "shorts": {
        "label": "Shorts",
        "code_prefix": "SHO",
        "flat": "shorts",
        "fabric": {
            "type": "Cotton-polyester twill",
            "composition": "68% cotton / 32% polyester",
            "weight": "220–240 GSM",
            "finish": "Quick-dry finish, pre-shrunk",
            "lining": "None",
            "supplier": "TBC — attach approved swatch & lab dip card",
            "colorfastness": "Grade 4+ to rub & wash (ISO 105-X12, C06)",
            "shrinkage": "≤ 2%",
        },
        "consumption": "1.1 m per piece (size M, 145 cm usable width, est.)",
        "measurements": [
            ("waist", "Waist (armpit to armpit)", 41, 2.5, 0.5, 1.0, "Across waistband, flat"),
            ("hip", "Hip (armpit to armpit)", 51, 3.0, 0.5, 1.0, "10 cm below waistband, horizontal"),
            ("inseam", "Inseam", 23, 1.0, 1.0, 1.0, "From crotch point to hem, inner seam"),
            ("outseam", "Outseam", 40, 1.0, 1.0, 1.0, "From waist to hem, outer seam"),
            ("rise", "Front rise", 27, 0.5, 1.0, 1.0, "From waist at front centre to crotch point"),
            ("hem", "Hem width", 19, 1.0, 0.5, 1.0, "Hem opening, flat"),
        ],
        "bom": [
            ["Outer fabric", "68/32 cotton-poly twill, 220–240 GSM", "1.1 m (M)"],
            ["Button (or drawcord)", "38 mm metal (or 8 mm drawcord ×2)", "1 (or 2)"],
            ["Belt loops", "Self-fabric, 1.2 cm wide", "4 (or none)"],
            ["Main thread", "Polyester Tex 70, colour-matched", "1 roll / 30 pcs (shared)"],
            ["Main label", "Woven 70D, 60 × 30 mm, back waist", "1"],
            ["Care + size label", "Woven 60D, 40 × 20 mm, left side seam", "1"],
            ["Hangtag", "350 gsm FSC card 90 × 60 mm + string + fastener", "1"],
            ["Poly bag", "45 × 60 cm, 0.03 mm matte", "1"],
        ],
        "construction": [
            ["Seams", "404 4-thread overlock", "12 SPC, SA 1.2 cm"],
            ["Waistband", "301 lockstitch", "14 SPC"],
            ["Pockets", "301 topstitch + bar-tack at corners", "12 SPC"],
            ["Hem", "406 2-needle coverstitch, 1.2 cm fold", "12 SPC"],
            ["Bar-tacks", "69 at pocket corners & fly end", "4×4 min."],
            ["Topstitching", "301 double-needle", "2.5 mm offset"],
        ],
        "details": [
            "Side pockets, curved",
            "Button (or drawcord) closure",
            "No back yoke (optional)",
            "Coverstitched hem, 1.2 cm",
            "Embellishment: none (logo left leg — TBC)",
        ],
    },
    "dress": {
        "label": "Dress (A-line, sleeve/cap sleeve)",
        "code_prefix": "DS",
        "flat": "dress",
        "fabric": {
            "type": "Viscose crepe",
            "composition": "95% viscose / 5% elastane",
            "weight": "150–180 GSM",
            "finish": "Mercerised for hand-feel, pre-shrunk",
            "lining": "None (optional: partial bodice lining)",
            "supplier": "TBC — attach approved swatch & lab dip card",
            "colorfastness": "Grade 4+ to rub & wash (ISO 105-X12, C06)",
            "shrinkage": "≤ 3% after 3 washes",
        },
        "consumption": "2.0 m per piece (size M, 145 cm usable width, est.)",
        "measurements": [
            ("chest", "Chest (armpit to armpit)", 45, 3.0, 0.5, 1.0, "Horizontal, 2.5 cm below armhole seam"),
            ("waist", "Waist (armpit to armpit)", 37, 2.5, 0.5, 1.0, "Horizontal, natural waist line"),
            ("hip", "Hip (armpit to armpit)", 49, 3.0, 0.5, 1.0, "10 cm below waist, horizontal"),
            ("length", "Length (shoulder to hem)", 96, 1.5, 1.0, 1.0, "From high point of shoulder to hem, centre back"),
            ("shoulder", "Shoulder (seam to seam)", 35, 1.5, 0.5, 0.5, "Across shoulder seam"),
            ("sleeve", "Sleeve (cap, shoulder to hem)", 19, 1.0, 1.0, 1.0, "From shoulder tip to sleeve hem"),
        ],
        "bom": [
            ["Outer fabric", "95/5 viscose crepe, 150–180 GSM", "2.0 m (M)"],
            ["Invisible zip", "50 cm, #5, colour-matched", "1"],
            ["Zipper foot & placket tape", "Self-fabric", "0.3 m"],
            ["Main thread", "Polyester Tex 70, colour-matched", "1 roll / 30 pcs (shared)"],
            ["Main label", "Woven 70D, 60 × 30 mm, back neck or side", "1"],
            ["Care + size label", "Woven 60D, 40 × 20 mm, left side seam", "1"],
            ["Hangtag", "350 gsm FSC card 90 × 60 mm + string + fastener", "1"],
            ["Poly bag", "60 × 80 cm, 0.03 mm matte (longer for dress)", "1"],
        ],
        "construction": [
            ["Body & sleeve seams", "404 4-thread overlock", "12 SPC, SA 1.0 cm"],
            ["Neckline facing", "301 lockstitch, self-fabric facing", "14 SPC"],
            ["Back zipper", "301 lockstitch, invisible #5", "14 SPC"],
            ["Hem", "406 2-needle coverstitch, 2 cm fold", "12 SPC"],
            ["Bar-tacks", "69 at zip ends", "4×4 min."],
            ["Press & finish", "Steam press, hang-dry finish", "—"],
        ],
        "details": [
            "V neckline with self-fabric facing",
            "A-line silhouette from bust",
            "Back centre invisible zip, 50 cm",
            "Cap sleeve",
            "Embellishment: none (logo left chest — TBC)",
        ],
    },
    "skirt": {
        "label": "Skirt (A-line, knee length)",
        "code_prefix": "SK",
        "flat": "skirt",
        "fabric": {
            "type": "Cotton twill / viscose crepe",
            "composition": "100% cotton",
            "weight": "230 GSM",
            "finish": "Sanforised, pre-shrunk",
            "lining": "None (optional: partial lining)",
            "supplier": "TBC — attach approved swatch & lab dip card",
            "colorfastness": "Grade 4+ to rub & wash (ISO 105-X12, C06)",
            "shrinkage": "≤ 2% (sanforised)",
        },
        "consumption": "1.2 m per piece (size M, 145 cm usable width, est.)",
        "measurements": [
            ("waist", "Waist (armpit to armpit)", 37, 2.5, 0.5, 1.0, "Across waistband, flat"),
            ("hip", "Hip (armpit to armpit)", 47, 3.0, 0.5, 1.0, "10 cm below waistband, horizontal"),
            ("length", "Length (waist to hem)", 45, 1.5, 1.0, 1.0, "From top of waistband to hem, side seam"),
            ("hem", "Hem width", 60, 2.0, 1.0, 1.5, "Hem opening, flat"),
        ],
        "bom": [
            ["Outer fabric", "100% cotton twill, 230 GSM", "1.2 m (M)"],
            ["Invisible zip", "30 cm, #5, colour-matched", "1"],
            ["Main thread", "Polyester Tex 70, colour-matched", "1 roll / 30 pcs (shared)"],
            ["Main label", "Woven 70D, 60 × 30 mm, back waist", "1"],
            ["Care + size label", "Woven 60D, 40 × 20 mm, left side seam", "1"],
            ["Hangtag", "350 gsm FSC card 90 × 60 mm + string + fastener", "1"],
            ["Poly bag", "45 × 60 cm, 0.03 mm matte", "1"],
        ],
        "construction": [
            ["Seams", "404 4-thread overlock", "12 SPC, SA 1.0 cm"],
            ["Waistband", "301 lockstitch", "14 SPC"],
            ["Back zip", "301 lockstitch, invisible #5", "14 SPC"],
            ["Hem", "406 2-needle coverstitch, 2 cm fold", "12 SPC"],
            ["Bar-tacks", "69 at zip ends", "4×4 min."],
            ["Press & finish", "Steam press, hang-dry finish", "—"],
        ],
        "details": [
            "Waistband, 3 cm, with hook or zip closure",
            "A-line drape",
            "Back centre invisible zip, 30 cm",
            "Coverstitched hem",
            "Embellishment: none (logo left hip — TBC)",
        ],
    },
}

DEFAULT_CATEGORY = "tshirt"
