RULES = {
    "domain": {
        "forbidden": ["application", "interfaces", "infrastructure"],
    },
    "application": {
        "forbidden": ["interfaces", "infrastructure"],
    },
    "interfaces": {
        "forbidden": ["infrastructure"],
    },
    "shared": {
        "forbidden": ["application", "interfaces", "infrastructure", "domain"],
    },
    "infrastructure": {
        "forbidden": [],
    },
}