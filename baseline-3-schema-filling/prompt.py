# PHQ-9 prompt template
FILL_PHQ9_PROMPT_TEMPLATE = """
You are given a patient's mental health description.

Fill in the following JSON structure with scores from 0 (not at all) to 4 (nearly every day), based on their symptoms.

JSON structure:
{{
    "loss_of_interest": 0,
    "feeling_down": 0,
    "sleep_problems": 0,
    "energy_level": 0,
    "appetite_change": 0,
    "self_worth": 0,
    "concentration_difficulty": 0,
    "motor_activity_change": 0,
    "suicidal_thoughts": 0
}}

Patient description:
{text_sample}

Rules:
- Only output a VALID JSON object.
- DO NOT add any text before or after the JSON.
- If a symptom is not mentioned, score it as 0.
"""


DEPRESSION_TREATMENT_LABELS = {
    "Lately, I just don't feel like doing the things I used to enjoy. I used to love painting, but now even picking up a brush feels like a chore. I’ll stare at my supplies for hours, hoping for a spark, but it never comes. It feels like that joy has vanished, and I don’t know how to bring it back. Even when I try, something inside me just refuses to engage.": "Counseling",
    "I feel tired all the time, even after a full night's sleep. No matter how much rest I get, my body feels like it's carrying a weight I can’t shake off. It’s a constant fatigue that makes even the smallest tasks feel overwhelming. I find myself longing for sleep during the day but waking up just as exhausted. Everything feels like a chore.": "Counseling",
    "Sometimes, I feel down for no apparent reason. I go about my day, pretending I’m fine, but inside there’s this heaviness that never lifts. I laugh at jokes, I talk to people—but it all feels distant and disconnected. I wish I could explain it, but there isn’t always a reason, and that’s the hardest part. I’m just tired of feeling this way.": "Counseling",
    "I’ve been eating less than usual—not intentionally, but because food just doesn’t appeal to me anymore. I used to love cooking and trying new dishes, but now I barely want to eat. Meals feel like obligations rather than enjoyment. Sometimes I skip them entirely, not out of discipline, but because I forget or just don’t care.": "Counseling",
    "It takes so much effort to get out of bed in the morning. I wake up and just lie there, staring at the ceiling, dreading the day. I hit snooze again and again, hoping something will change. It’s not that I’m lazy—I just feel like I’m dragging myself through life. Getting up feels like climbing a mountain with no summit in sight.": "No treatment necessary",
    "I find myself zoning out at work, struggling to focus on even the simplest things. My thoughts drift constantly, and I reread the same sentence five times. I used to be sharp, quick, and attentive—but now everything feels foggy. Tasks pile up and I can’t keep up. It’s frustrating because I know I’m capable of better.": "Counseling",
    "I feel like I’m failing at everything—at work, in my relationships, even with basic self-care. No matter what I do, it never feels good enough. I constantly criticize myself and feel like a burden to others. I try to stay strong, but inside, I feel like I’m unraveling. It's like I’m stuck in a loop of inadequacy.": "Pharmaceutical Therapy",
    "I don’t talk to my friends much anymore. They reach out, invite me places, but I always find an excuse to say no. I just don’t have the energy to be social, and being around people feels exhausting. I know they care, but I feel more comfortable alone. Even when I’m lonely, isolation feels safer.": "Counseling",
    "I feel like I’m moving through life in slow motion. Every task—getting dressed, brushing my teeth, making coffee—feels monumental. Conversations feel like marathons, and I constantly zone out. I used to be full of energy, but now it’s like I’m walking through molasses. Everything takes more effort than I can give.": "Pharmaceutical Therapy",
    "Sometimes, I wonder if people would even notice if I disappeared. These thoughts creep in late at night when everything is quiet. I lie awake, staring at the ceiling, feeling like I don’t matter. I try to shake it off, but it keeps coming back. It’s a frightening feeling, and I don’t know how to stop it.": "Pharmaceutical Therapy"
}