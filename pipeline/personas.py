"""
HMTI persona catalogue — 16 v2 types from RoomieScout meta-v2.ts.
Axes: N/C (Cleanliness), P/O (Social), D/H (Conflict), S/F (Structure).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    bg_from: str
    bg_to: str
    accent: str
    soft: str
    badge: str
    badge_text: str


@dataclass(frozen=True)
class PersonaMeta:
    code: str
    title: str
    emoji: str
    description: str
    animal: str
    scene: str
    expression: str
    props: list[str]
    accessories: str
    character_direction: str
    palette: Palette
    tagline: str
    trait_badges: list[str]
    roommate_superpower: str
    danger_zone: str
    best_matches: list[str]
    household_energy: str


HMTI_AXES = [
    {
        "name": "Cleanliness",
        "a": {"letter": "N", "trait": "Neat", "description": "Keeps shared spaces clean and orderly."},
        "b": {"letter": "C", "trait": "Casual", "description": "Relaxed about mess and chores."},
    },
    {
        "name": "Social intensity",
        "a": {"letter": "P", "trait": "Private", "description": "Home is a retreat — values quiet and personal space."},
        "b": {"letter": "O", "trait": "Open", "description": "Home is a social space — enjoys shared time and guests."},
    },
    {
        "name": "Conflict style",
        "a": {"letter": "D", "trait": "Direct", "description": "Addresses issues promptly and plainly."},
        "b": {"letter": "H", "trait": "Harmonious", "description": "Keeps the peace — absorbs friction rather than names it."},
    },
    {
        "name": "Structure preference",
        "a": {"letter": "S", "trait": "Structured", "description": "Prefers clear agreements, chore charts, and defined expectations."},
        "b": {"letter": "F", "trait": "Flexible", "description": "Figures things out as they go — informal and adaptable."},
    },
]

AXIS_WEIGHTS = [35, 30, 20, 15]  # cleanliness, social, conflict, structure

PERSONAS: dict[str, PersonaMeta] = {
    "NPDS": PersonaMeta(
        code="NPDS", title="The Curator", emoji="🦉",
        description="Runs a calm, orderly home and tells you clearly how it works. Spotless shared spaces, respected closed doors, zero passive aggression.",
        animal="owl",
        scene="Quiet desk — made bed, aligned slippers, color-coded wall calendar",
        expression="Peaceful, focused, slightly proud",
        props=["checklist", "desk lamp", "wall calendar", "tea mug"],
        accessories="matte round glasses, slim tie, clipboard, organized desk setup",
        character_direction="Calm authority: tidy, private, direct. Focused planner energy — proud and peaceful, not bubbly.",
        palette=Palette("#e8f0fa", "#faf6ee", "#6b9fd4", "#d4e4f5", "#eef5fc", "#2d4a6e"),
        tagline="Quiet hours are my love language.",
        trait_badges=["Clean Nest", "Direct & Clear", "Structured"],
        roommate_superpower="Spotless shared spaces, respected closed doors, zero passive aggression — issues raised once, kindly, and solved.",
        danger_zone="Passive-aggressive notes, shared spaces left in chaos, housemates who don't follow through.",
        best_matches=["NPDF", "NPHS", "NODS"],
        household_energy="Spice rack alphabetized. Counter spotless. Issue raised once, kindly, done.",
    ),
    "NPDF": PersonaMeta(
        code="NPDF", title="The Strategist", emoji="🦊",
        description="Clean, self-contained, and capable. No chore chart needed — they just handle things, and if something's off they'll say so plainly.",
        animal="fox",
        scene="Night desk — planner, sticky notes, laptop glow, headphones nearby",
        expression="Alert, capable, self-sufficient",
        props=["laptop", "planner", "sticky notes", "headphones"],
        accessories="over-ear headphones, neon sticky notes, laptop glow, planner",
        character_direction="Sharp independent: organized chaos, night desk, capable loner. Stylish fox energy — clever, not cuddly.",
        palette=Palette("#ede8f5", "#f5ebe8", "#7c6bc4", "#ddd4f0", "#f3f0fa", "#3d3560"),
        tagline="My schedule is chaos, but my space is not.",
        trait_badges=["Clean Chaos", "Direct", "Flexible"],
        roommate_superpower="Handles things without being asked. If something's off, says so plainly and moves on. No charts, no drama.",
        danger_zone="Housemates who mistake directness for coldness or need constant social reassurance.",
        best_matches=["NPDS", "NPHF", "NODF"],
        household_energy="Dishes already done. Hours unknowable. Zero drama, high competence.",
    ),
    "NPHS": PersonaMeta(
        code="NPHS", title="The Minimalist", emoji="🐱",
        description="Quiet, elegant, low-drama. Loves a system precisely because good systems mean nobody ever has to have an awkward conversation.",
        animal="cat",
        scene="Minimal cozy bedroom — clean bed, book, plant by window, closed door",
        expression="Relaxed, content, quietly confident",
        props=["book", "plant", "folded blanket", "do not disturb sign"],
        accessories="minimal wire-frame glasses, single book, clean lines, closed-door energy",
        character_direction="Quiet confidence: minimal, elegant, self-contained. Cool solitude — content alone, not shy-cute.",
        palette=Palette("#e8f0e8", "#f5f2eb", "#7a9e78", "#dce8d8", "#f0f5ee", "#3d5c3a"),
        tagline="Good systems mean no awkward conversations.",
        trait_badges=["Low Drama", "Clean Space", "Structured"],
        roommate_superpower="Creates a calm, orderly home without any drama. Good systems replace the need for uncomfortable chats.",
        danger_zone="Surprise changes to the routine, messy common spaces, and housemates who expect regular emotional processing.",
        best_matches=["NPHF", "NPDS", "NOHS"],
        household_energy="Kitchen sparkling. Door closed. Rota on the wall. No conversation needed.",
    ),
    "NPHF": PersonaMeta(
        code="NPHF", title="The Clean Ghost", emoji="✨",
        description="Rarely seen, never a problem. Keeps shared spaces spotless on their own schedule and creates zero friction.",
        animal="ferret",
        scene="Spotless hallway — quiet figure with laundry basket, sparkle trail, half-open bedroom door",
        expression="Shy, sweet, mysterious",
        props=["laundry basket", "folded towels", "sparkles", "bedroom door"],
        accessories="hoodie half-on, laundry basket, quiet hallway vibe, low-profile cap",
        character_direction="Low-key legend: barely seen, always responsible. Mysterious clean ghost — subtle, not timid.",
        palette=Palette("#e8faf5", "#f0f5fa", "#6bc4b8", "#d4f0ec", "#eefaf8", "#2d5c52"),
        tagline="You'll know I live here because everything is clean.",
        trait_badges=["Invisible", "Tidy", "Harmonious"],
        roommate_superpower="The most frictionless roommate in the system — clean, quiet, completely drama-free.",
        danger_zone="Housemates who need a lot of social energy, expect bonding nights, or interpret silence as coldness.",
        best_matches=["NPHS", "NPDF", "NOHS"],
        household_energy="Sink always empty. Timing unknown. Quiet hello in the hallway.",
    ),
    "NODS": PersonaMeta(
        code="NODS", title="The Captain", emoji="🐕",
        description="Friendly leader who runs the house with warmth and systems — snack runs, chore charts, group chats.",
        animal="golden-retriever",
        scene="Bright kitchen — clipboard, chore chart, freshly baked cookies, matching mugs",
        expression="Confident, welcoming, excited",
        props=["clipboard", "chore chart", "cookies", "fridge magnets"],
        accessories="captain clipboard, bandana, fresh cookies, chore chart — friendly leader not mascot plush",
        character_direction="Friendly captain: runs the house with systems and warmth. Leader energy — welcoming, not hyper.",
        palette=Palette("#fff8e0", "#e8f4ff", "#e8b848", "#ffe8a8", "#fffaf0", "#6e5a20"),
        tagline="I run this house with snacks and systems.",
        trait_badges=["House Leader", "Clean Crew", "Direct"],
        roommate_superpower="Turns the apartment into a clean, connected household with warmth and actual systems.",
        danger_zone="Housemates who ignore the chore chart, avoid the group chat, or treat structure as controlling.",
        best_matches=["NODF", "NOHS", "NPDS"],
        household_energy="Chore chart on the fridge. Group chat active. Movie night confirmed.",
    ),
    "NODF": PersonaMeta(
        code="NODF", title="The Firecracker", emoji="🦜",
        description="Spontaneous plans, full living room, surprisingly clean counters. Names issues warmly and directly, then moves on.",
        animal="parrot",
        scene="Lively kitchen — parrot hosting impromptu dinner, clean counter, music playing",
        expression="Energetic, charismatic, direct",
        props=["speaker", "wine glasses", "clean counter", "fairy lights"],
        accessories="colourful scarf, wine glass, music on — social and vibrant but sharp",
        character_direction="Social and direct: open-door energy, clean spaces, no filter but warm. Parrot energy — vivid, not noisy.",
        palette=Palette("#e8f8ff", "#fff0f5", "#48b8d4", "#d4f0ff", "#f0faff", "#2d5a6e"),
        tagline="Direct, clean, and always up for a plan.",
        trait_badges=["Open Door", "Direct", "Spontaneous"],
        roommate_superpower="Spontaneous plans and surprisingly clean counters. Names issues warmly and directly, then moves on.",
        danger_zone="Housemates who take directness personally or need strict quiet and predictability at home.",
        best_matches=["NODS", "NOHF", "NPDF"],
        household_energy="Dinner party started 10 minutes ago. Counters still clean. Front door open.",
    ),
    "NOHS": PersonaMeta(
        code="NOHS", title="The Sweetheart", emoji="🐶",
        description="Warm, tidy, dependable — the universally liked roommate. Keeps routines, keeps the peace, keeps the kitchen clean.",
        animal="corgi",
        scene="Cozy living room — watering plants, neat couch, snack bowl on table",
        expression="Cheerful, approachable, relaxed",
        props=["watering can", "houseplants", "snack bowl", "throw pillows"],
        accessories="bandana, watering can, neat living room, approachable host energy",
        character_direction="Neighborhood favorite: tidy, social, balanced. Warm host — relaxed smile, not cartoon cheer.",
        palette=Palette("#fff0e8", "#f0f5e8", "#e8a078", "#ffe0d0", "#fff8f2", "#6e4a30"),
        tagline="The apartment is warmer because I'm in it.",
        trait_badges=["Warm", "Tidy", "Peaceful"],
        roommate_superpower="The home genuinely feels nicer with them in it. Warm, tidy, reliable, and zero drama.",
        danger_zone="Direct confrontation, unpredictable messes, and housemates who bring chaotic energy home.",
        best_matches=["NOHF", "NODS", "NPHS"],
        household_energy="Tea on. Your exam remembered. Vibe: soft and safe.",
    ),
    "NOHF": PersonaMeta(
        code="NOHF", title="The Sunshine", emoji="🐼",
        description="Easygoing warmth with clean habits. Up for whatever, allergic to drama, somehow the apartment is always tidy.",
        animal="red-panda",
        scene="Bright apartment — red panda reading, tidy space, sunshine, plants everywhere",
        expression="Warm, easygoing, content",
        props=["book", "plants", "sunshine", "tea"],
        accessories="cozy sweater, warm drink, soft natural light — sunny and relaxed",
        character_direction="Sunshine energy: warm, flexible, clean. Red panda chill — naturally content, not performative.",
        palette=Palette("#ffe8e8", "#e8f5f5", "#e87868", "#ffd4d0", "#fff2f0", "#6e3a30"),
        tagline="Good mood included with the lease.",
        trait_badges=["Good Vibes", "Harmonious", "Spontaneous"],
        roommate_superpower="Easygoing warmth with clean habits. Up for anything, allergic to drama, somehow always tidy.",
        danger_zone="Heavy ongoing drama, rigid routines enforced on others, housemates who hold grudges.",
        best_matches=["NOHS", "NODF", "NPHF"],
        household_energy="Plans: sure. No plans: also great. Apartment somehow always tidy.",
    ),
    "CPDS": PersonaMeta(
        code="CPDS", title="The Anchor", emoji="🐢",
        description="Steady, grounded, unflappable. Relaxed about mess but crystal clear about space and expectations.",
        animal="turtle",
        scene="Calm corner — turtle at desk, steady lamp, clear boundaries",
        expression="Steady, grounded, unflappable",
        props=["desk lamp", "clear boundaries", "coffee", "notebook"],
        accessories="solid jacket, steady posture, grounded energy — reliable not stiff",
        character_direction="Rock-steady: private, direct, structured. Turtle authority — calm confidence, not intimidating.",
        palette=Palette("#e8f0e8", "#f5f0e8", "#5a8a5a", "#d4e8d4", "#f0f5f0", "#2e4a2e"),
        tagline="Clear expectations. Zero surprises.",
        trait_badges=["Steady", "Direct", "Boundaries"],
        roommate_superpower="Crystal clear about space and expectations. You always know exactly where you stand.",
        danger_zone="Housemates who leave shared spaces in chaos, ignore agreements, or don't respect clear boundaries.",
        best_matches=["CPDF", "CPHS", "CODS"],
        household_energy="Steady presence. Clear expectations. Zero performance required.",
    ),
    "CPDF": PersonaMeta(
        code="CPDF", title="The Maverick", emoji="🦔",
        description="Independent, low-maintenance, refreshingly blunt. Lives on their own schedule and tells you straight when something matters.",
        animal="hedgehog",
        scene="Night desk — laptop, odd hours, self-contained setup",
        expression="Alert, self-reliant, no-nonsense",
        props=["laptop", "coffee", "headphones", "dim desk lamp"],
        accessories="casual dark hoodie, messy desk but own system, sharp focus",
        character_direction="Night-owl independent: blunt, capable, minimal social needs. Hedgehog energy — prickly exterior, reliable core.",
        palette=Palette("#ede8f8", "#f5f0e8", "#8a6ab8", "#ddd0f0", "#f5f0fa", "#4a3a5c"),
        tagline="Refreshingly blunt. Impressively low-maintenance.",
        trait_badges=["Independent", "Direct", "Flexible"],
        roommate_superpower="Refreshingly blunt and completely self-sufficient. Won't bother you unless it actually matters.",
        danger_zone="Needy roommates, forced bonding, housemates who over-share or need constant availability.",
        best_matches=["CPDS", "CPHF", "CODF"],
        household_energy="Schedule: unknowable. Rent: cleared. Problems: handled directly.",
    ),
    "CPHS": PersonaMeta(
        code="CPHS", title="The Unbothered", emoji="🐼",
        description="Peak chill with a steady rhythm. No drama, no demands, no surprises — a calm presence who respects your space completely.",
        animal="panda",
        scene="Minimal bedroom — panda meditating, clean space, soft light",
        expression="Serene, unhurried, at peace",
        props=["meditation cushion", "tea", "soft lamp", "plant"],
        accessories="loose comfortable clothes, zero clutter, soft natural light",
        character_direction="Peak chill: private, harmonious, structured. Panda peace — genuinely unbothered, not checked out.",
        palette=Palette("#f0f0f0", "#f5f5eb", "#6e6e6e", "#e0e0e0", "#f8f8f8", "#3a3a3a"),
        tagline="Peak chill. Zero opinions about your life.",
        trait_badges=["Chill", "Harmonious", "Steady"],
        roommate_superpower="Peak chill with a steady rhythm. Nothing rattles them. Completely respects your space and expects the same.",
        danger_zone="Unavoidable conflict situations, forced social time, environments where things escalate.",
        best_matches=["CPHF", "CPDS", "COHS"],
        household_energy="Same routine. Zero opinions about yours. Extremely at peace.",
    ),
    "CPHF": PersonaMeta(
        code="CPHF", title="The Cryptid", emoji="🦇",
        description="Sighted occasionally near the fridge at 2am. Pays rent on time, bothers no one, asks nothing.",
        animal="bat",
        scene="Dark hallway — mysterious figure by fridge, 2am, brief nod exchanged",
        expression="Mysterious, unbothered, barely present",
        props=["fridge", "darkness", "hoodie", "keys"],
        accessories="dark hoodie, minimal presence, late-night kitchen energy",
        character_direction="The cryptid: barely seen, rent paid, no drama. Bat energy — nocturnal myth, not spooky.",
        palette=Palette("#e8e8f5", "#f0f0f8", "#6a6a9e", "#d8d8ec", "#f0f0f8", "#3a3a52"),
        tagline="May or may not be real.",
        trait_badges=["Ghost Mode", "Harmonious", "Flexible"],
        roommate_superpower="Pays rent on time, bothers no one, asks nothing. The ultimate low-friction housemate.",
        danger_zone="Housemates who need connection, check-ins, or want to know where you are at all times.",
        best_matches=["CPHS", "CPDF", "COHF"],
        household_energy="Fridge at 2am. Brief nod. Rent from somewhere. May or may not be real.",
    ),
    "CODS": PersonaMeta(
        code="CODS", title="The Glue", emoji="🫶",
        description="Holds the household together — communal dinners, fair splits, real talk before things fester.",
        animal="capybara",
        scene="Warm kitchen — big table, communal dinner, everyone welcome",
        expression="Warm, inclusive, quietly proud",
        props=["big pot", "dining table", "shared expenses app", "snacks"],
        accessories="apron, communal vibe, open table — welcoming not performative",
        character_direction="Community builder: casual, open, direct. Capybara warmth — inclusive calm, not overly intense.",
        palette=Palette("#fff5e8", "#f0f5e8", "#c49050", "#ffe8c8", "#fffaf2", "#5c4a28"),
        tagline="People matter more than counters.",
        trait_badges=["Community", "Direct", "Fair"],
        roommate_superpower="Holds the household together — communal dinners, fair splits, real talk before things fester.",
        danger_zone="Housemates who shut down, avoid the group dynamic, or let issues quietly build.",
        best_matches=["CODF", "COHS", "CPDS"],
        household_energy="Sunday dinner. Bills split fair. Nobody eats alone unless they want to.",
    ),
    "CODF": PersonaMeta(
        code="CODF", title="The Ringleader", emoji="🦝",
        description="Instigator of the good kind of chaos. Names problems out loud, then turns the house meeting into something everyone laughs about.",
        animal="raccoon",
        scene="Living room with fairy lights — raccoon mid-plan, whiteboard, taco night",
        expression="Mischievous, warm, energetic",
        props=["whiteboard", "fairy lights", "tacos", "group chat"],
        accessories="casual gear, fairy lights, impromptu gathering setup",
        character_direction="Good chaos energy: social, direct, flexible. Raccoon ringleader — clever improviser, not messy.",
        palette=Palette("#e8f0ff", "#fff0e8", "#5090d4", "#d4e8ff", "#f0f8ff", "#2d4a6e"),
        tagline="The chaos you'll miss when you move out.",
        trait_badges=["Instigator", "Direct", "Spontaneous"],
        roommate_superpower="Names the problem, then turns the house meeting into something everyone laughs about.",
        danger_zone="Housemates who find spontaneity exhausting or who are deeply uncomfortable with direct conflict.",
        best_matches=["CODS", "COHF", "CPDF"],
        household_energy="Tuesday became taco night. Hallway has fairy lights. House meeting: actually fun.",
    ),
    "COHS": PersonaMeta(
        code="COHS", title="The Teddy Bear", emoji="🐻",
        description="Cozy, warm, reliable. Makes the apartment feel like home — steady routines and never a harsh word.",
        animal="bear",
        scene="Cozy living room — bear with soup, blankets, comfort show playing",
        expression="Warm, cozy, gently present",
        props=["soup pot", "blanket", "comfort show", "tea mug"],
        accessories="soft sweater, cozy kitchen setup, warm lighting — gentle bear vibes",
        character_direction="Home energy: warm, open, harmonious. Bear comfort — cozy and safe, not sleepy.",
        palette=Palette("#fff5e8", "#ffeef0", "#d4a050", "#ffe8c8", "#fffaf5", "#5c4020"),
        tagline="Living here feels like a hug.",
        trait_badges=["Cozy", "Harmonious", "Reliable"],
        roommate_superpower="Makes the apartment feel like home. Cozy, warm, reliable, and genuinely never a harsh word.",
        danger_zone="Confrontational housemates, cold apartments, and rigid rule-enforcement with no warmth.",
        best_matches=["COHF", "CODS", "CPHS"],
        household_energy="Soup on the stove. Blanket with your name on it. Drama: zero.",
    ),
    "COHF": PersonaMeta(
        code="COHF", title="The Disco Ball", emoji="🦦",
        description="The living room is a lifestyle. Spontaneous, sunny, up for anything, mad at no one.",
        animal="otter",
        scene="Colorful living room — otter on the couch with pizza, speaker blasting, string lights",
        expression="Hyped, sunny, charismatic",
        props=["speaker", "pizza", "disco ball", "string lights"],
        accessories="party shades, pizza slice, mini disco ball, speaker — hype but not childish",
        character_direction="Party-compatible: living room is the vibe. Otter energy — spontaneous fun, cool roommate.",
        palette=Palette("#e8f8ff", "#fff0f8", "#5ab8d4", "#d4f0ff", "#f0faff", "#2d5a6e"),
        tagline="Whatever's happening tonight — I'm in.",
        trait_badges=["Social", "Harmonious", "Spontaneous"],
        roommate_superpower="The living room is a lifestyle. Brings the energy and rolls with absolutely everything.",
        danger_zone="Housemates who need strict quiet, rigid routines, or zero social spontaneity at home.",
        best_matches=["COHS", "CODF", "CPHF"],
        household_energy="Speaker charged. Friends welcome. Never held a grudge longer than a song.",
    ),
}

PERSONA_CODES = list(PERSONAS.keys())

DIMENSION_DESCRIPTIONS = """The 4 dimensions of the HMTI roommate personality type:
1. N (Neat/private) vs C (Casual/communal) — cleanliness and social orientation at home
2. P (Private — home is a retreat) vs O (Open — home is a social space) — social intensity
3. D (Direct — addresses issues plainly) vs H (Harmonious — keeps the peace) — conflict style
4. S (Structured — chore charts, clear agreements) vs F (Flexible — figures it out as they go) — structure preference

Axis weights for compatibility: Cleanliness 35%, Social 30%, Conflict 20%, Structure 15%."""
