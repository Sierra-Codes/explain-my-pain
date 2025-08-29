# taxonomy.py — Bullo taxonomy (cleaned version)
# Used by index.html + tagger_logic.py

taxonomy = {
    "metaphor_types": {
        "violent_action": {
            "hint": "Sudden, forceful, violating actions.",
            "expressions": [
                "attack", "assault", "stabbing", "punching",
                "beating", "slammed", "ripped apart",
                "tearing apart", "violent intrusion"
            ]
        },
        "cutting_tools": {
            "hint": "Knives, razors, glass—sharp implements & edges.",
            "expressions": [
                "knife", "razor", "blade", "scalpel", "glass",
                "cutting", "slicing", "piercing"
            ]
        },
        "internal_machinery": {
            "hint": "Gears, drills, clamps—machinery inside the body.",
            "expressions": [
                "gears grinding", "cogs", "engine", "drill",
                "rusty hinge", "vice", "mechanical grinding"
            ]
        },
        "constriction_pressure": {
            "hint": "Squeezing, clamping, tightening, crushing pressure.",
            "expressions": [
                "tightening", "squeezing", "strangling",
                "constriction", "clamping", "crushing", "compressing"
            ]
        },
        "electric_force": {
            "hint": "Electric shocks, zaps, jolts, buzzing, tingling.",
            "expressions": [
                "electric shock", "zapping", "jolt",
                "buzzing", "tingling", "lightning", "sparks"
            ]
        },
        "weight_burden": {
            "hint": "Heaviness, burden, dragging weight.",
            "expressions": [
                "heaviness", "weight", "weighed down",
                "boulder", "brick", "burden", "dragging"
            ]
        },
        "heat": {
            "hint": "Burning, searing, scalding, fiery heat.",
            "expressions": [
                "burning", "searing", "scalding", "fiery",
                "on fire", "hot", "inflamed"
            ]
        },
        "birth_labour": {
            "hint": "Labour pains, contractions, waves, bearing down.",
            "expressions": [
                "labour", "contractions", "bearing down",
                "waves of pain",
                "birth pains", "surges"
            ]
        },
        "lingering_force": {
            "hint": "Background, persistent, simmering/throbbing ache.",
            "expressions": [
                "throbbing", "dull ache", "nagging",
                "simmering", "lurking", "baseline ache"
            ]
        },
        "predator": {
            "hint": "Lurking creature/monster/animal, invasive & unpredictable.",
            "expressions": [
                "lurking", "stalking", "ready to attack"
            ]
        },
        "entrapment": {
            "hint": "Trapped/locked in a body or cage; no escape.",
            "expressions": [
                "trapped", "locked in", "caged", "imprisoned",
                "stuck in my body"
            ]
        },
        "transformation_distortion": {
            "hint": "Alien/warped body/identity; distortion/dissociation.",
            "expressions": [
                "not myself", "losing myself", "alien",
                "distorted", "warped", "twisted",
                "changing shape", "detached", "dissociated"
            ]
        }
    },

    "graduation_modifiers": [
        "slight", "mild", "moderate", "strong", "severe", "very", "extremely",
        "constant", "intermittent", "sudden", "gradual", "worse at night",
        "comes and goes", "flare", "flare-up"
    ],

    "triggers": [
        "menstruation", "period", "menses", "ovulation", "mid cycle",
        "sex", "intercourse", "penetration",
        "going to the toilet", "urination", "bowel movement", "defecation",
        "daily life", "background", "rest of the month",
        "physical activity", "exercise",
        "sleep", "rest"
    ],

    "life_impact_clues": [
        "dominates my life",
        "affects me socially",
        "affects my productivity",
        "prevents me from carrying out basic chores",
        "affects my mental health",
        "affects my happiness",
        "isolated", "exhausted", "losing myself", "overwhelmed",
        "anxious", "worried", "low mood", "down"
    ],
}
