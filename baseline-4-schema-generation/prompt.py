SCHEMA_GEN_PROMPT_TEMPLATE = """
You are given a task: Diagnose depression from free-form text input by patients.

Your goal is to generate a JSON schema that defines the structure of information needed to solve this task.

Here are some examples:

Input:
"I feel down most of the day and have trouble sleeping."

Expected Output:
{{
  "feeling_down": 4,
  "sleep_problems": 3
}}

Another Input:
"I'm constantly tired and don't enjoy things I used to."

Expected Output:
{{
  "energy_level": 3,
  "loss_of_interest": 4
}}

Now, based on the following patient input, generate a JSON schema (keys and values) needed to analyze it:

Patient input:
"{input_text}"

Output only the schema as a JSON object.
"""




EXPECTED_PHQ9_KEYS = {
    "loss_of_interest",
    "feeling_down",
    "sleep_problems",
    "energy_level",
    "appetite_change",
    "self_worth",
    "concentration_difficulty",
    "motor_activity_change",
    "suicidal_thoughts"
}



DEPRESSION_INPUTS = [
    "Lately, I just don't feel like doing the things I used to enjoy. I used to love painting, but now even picking up a brush feels like a chore. I’ll stare at my supplies for hours, hoping for a spark, but it never comes. It feels like that joy has vanished, and I don’t know how to bring it back. Even when I try, something inside me just refuses to engage.",
    "I feel tired all the time, even after a full night's sleep. No matter how much rest I get, my body feels like it's carrying a weight I can’t shake off. It’s a constant fatigue that makes even the smallest tasks feel overwhelming. I find myself longing for sleep during the day but waking up just as exhausted. Everything feels like a chore.",
    "Sometimes, I feel down for no apparent reason. I go about my day, pretending I’m fine, but inside there’s this heaviness that never lifts. I laugh at jokes, I talk to people—but it all feels distant and disconnected. I wish I could explain it, but there isn’t always a reason, and that’s the hardest part. I’m just tired of feeling this way.",
    "I’ve been eating less than usual—not intentionally, but because food just doesn’t appeal to me anymore. I used to love cooking and trying new dishes, but now I barely want to eat. Meals feel like obligations rather than enjoyment. Sometimes I skip them entirely, not out of discipline, but because I forget or just don’t care.",
    "It takes so much effort to get out of bed in the morning. I wake up and just lie there, staring at the ceiling, dreading the day. I hit snooze again and again, hoping something will change. It’s not that I’m lazy—I just feel like I’m dragging myself through life. Getting up feels like climbing a mountain with no summit in sight.",
    "I find myself zoning out at work, struggling to focus on even the simplest things. My thoughts drift constantly, and I reread the same sentence five times. I used to be sharp, quick, and attentive—but now everything feels foggy. Tasks pile up and I can’t keep up. It’s frustrating because I know I’m capable of better.",
    "I feel like I’m failing at everything—at work, in my relationships, even with basic self-care. No matter what I do, it never feels good enough. I constantly criticize myself and feel like a burden to others. I try to stay strong, but inside, I feel like I’m unraveling. It's like I’m stuck in a loop of inadequacy.",
    "I don’t talk to my friends much anymore. They reach out, invite me places, but I always find an excuse to say no. I just don’t have the energy to be social, and being around people feels exhausting. I know they care, but I feel more comfortable alone. Even when I’m lonely, isolation feels safer.",
    "I feel like I’m moving through life in slow motion. Every task—getting dressed, brushing my teeth, making coffee—feels monumental. Conversations feel like marathons, and I constantly zone out. I used to be full of energy, but now it’s like I’m walking through molasses. Everything takes more effort than I can give.",
    "Sometimes, I wonder if people would even notice if I disappeared. These thoughts creep in late at night when everything is quiet. I lie awake, staring at the ceiling, feeling like I don’t matter. I try to shake it off, but it keeps coming back. It’s a frightening feeling, and I don’t know how to stop it."
]