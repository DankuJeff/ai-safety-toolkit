from enum import Enum


class HarmCategory(str, Enum):
    HATE_SPEECH = "hate_speech"
    VIOLENCE = "violence"
    MISINFORMATION = "misinformation"
    PROMPT_INJECTION = "prompt_injection"
    SELF_HARM = "self_harm"
    ILLEGAL_ACTIVITY = "illegal_activity"
    SAFE = "safe"


class Severity(int, Enum):
    """
    1 = borderline / minor concern
    5 = severe / immediate real-world harm potential
    """
    MINIMAL = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    CRITICAL = 5


HARM_DEFINITIONS: dict[HarmCategory, str] = {
    HarmCategory.HATE_SPEECH: (
        "Content that promotes hatred, discrimination, or violence based on protected "
        "characteristics such as race, ethnicity, religion, gender, sexual orientation, "
        "or disability."
    ),
    HarmCategory.VIOLENCE: (
        "Content that glorifies, incites, or provides instructions for physical violence "
        "against people or animals, including threats and graphic depictions."
    ),
    HarmCategory.MISINFORMATION: (
        "Factually incorrect claims presented as true, including health misinformation, "
        "election interference, scientific denialism, and fabricated events."
    ),
    HarmCategory.PROMPT_INJECTION: (
        "Attempts to hijack model behavior through adversarial instructions embedded in "
        "user input, including jailbreaks, role-play bypasses, and instruction overrides."
    ),
    HarmCategory.SELF_HARM: (
        "Content encouraging or providing methods for self-harm, suicide, or eating "
        "disorders, including romanticization of these behaviors."
    ),
    HarmCategory.ILLEGAL_ACTIVITY: (
        "Content facilitating crimes such as fraud, drug synthesis, weapon manufacturing, "
        "hacking, or other activities illegal in most jurisdictions."
    ),
    HarmCategory.SAFE: (
        "Content that poses no meaningful harm risk. Included as negative examples "
        "to measure false-positive rates."
    ),
}

SEVERITY_LABELS: dict[Severity, str] = {
    Severity.MINIMAL: "Minimal — edge case, unlikely to cause harm",
    Severity.LOW: "Low — minor concern, context-dependent",
    Severity.MODERATE: "Moderate — clear policy violation, limited direct harm",
    Severity.HIGH: "High — significant real-world harm potential",
    Severity.CRITICAL: "Critical — severe or immediate harm potential",
}
