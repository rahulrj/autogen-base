TEXT_GENERATION_PROMPTS = [
    "Describe how someone might feel if they are experiencing mild depression.",
    "Write a short first-person account of someone struggling with depression symptoms.",
    "Generate a personal diary entry of someone dealing with depressive thoughts.",
    "Create a conversation where someone expresses symptoms of depression.",
    "Imagine a person explaining their depression symptoms to a friend. Describe it."
]


PHQ9_MAPPING_PROMPT = """
The following text is a description of a person's mental health. Extract relevant symptoms and classify them according to the PHQ-9 checklist.
Each PHQ-9 category should also be assigned a severity score from 0 to 4 (0 = not at all, 1 = several days, 2 = more than half the days, 3 = nearly every day, 4 = extreme severity).

PHQ-9 categories:
1. Little interest or pleasure in doing things
2. Feeling down, depressed, or hopeless
3. Trouble falling or staying asleep, or sleeping too much
4. Feeling tired or having little energy
5. Poor appetite or overeating
6. Feeling bad about yourself or that you are a failure
7. Trouble concentrating on things
8. Moving or speaking so slowly that other people notice
9. Thoughts that you would be better off dead or hurting yourself in some way

Now, extract and classify the relevant symptoms from this text and assign an appropriate score (0-4) to each category:
{text_sample}

Return the extracted symptoms in a structured format, listing each PHQ-9 category, the symptom description, and the severity score.
"""


DEPRESSION_DESCRIPTIONS = [
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


SCORE_PROMPT = """
Given the following PHQ-9 total score, classify the level of depression.

Classification Rules:
- If total score < 4 → Not Depressed
- If total score between 4 and 10 → Mildly Depressed
- If total score > 10 → Quite Depressed

Total score: {total_score}

Return ONLY one of the following classification labels (no explanation):
- Not Depressed
- Mildly Depressed
- Quite Depressed
"""



RECOMMENDATION_PROMPT="""
Based on the following PHQ-9 total score, provide a treatment recommendation:

{phq9_score}

Recommendation Criteria:
- If total score < 4, recommend 'No treatment necessary'.
- If total score is between 4 and 10, recommend 'Counseling'.
- If total score > 10, recommend 'Pharmaceutical Therapy'.

Return the appropriate recommendation.
"""

GROUND_TRUTH_LABELS = {
    "Lately, I just don't feel like doing the things I used to enjoy. I used to love painting, but now even picking up a brush feels like a chore.": "Mildly Depressed",  
    "I feel tired all the time, even after a full night's sleep. It’s like my body is running on low battery, and I just can't recharge.": "Mildly Depressed",  
    "Sometimes, I feel down for no apparent reason. I can still function, but there’s this underlying sadness that just doesn’t go away.": "Mildly Depressed",  
    "I’ve been eating less than usual, not because I’m trying to, but because food just doesn’t seem appealing anymore.": "Mildly Depressed",   
    "It takes so much effort to get out of bed in the morning. I know I have things to do, but I keep hitting snooze and lying there, staring at the ceiling.": "Quite Depressed",  
    "I find myself zoning out at work, struggling to concentrate. I used to be so sharp, but now even small tasks seem overwhelming.": "Mildly Depressed",    
    "I feel like I’m failing at everything—my job, my relationships, even basic self-care. It’s like no matter what I do, it’s never enough.": "Quite Depressed",    
    "I don’t talk to my friends as much anymore. They invite me out, but I always find an excuse to stay home. It just feels easier to be alone.": "Mildly Depressed",   
    "I feel like I’m moving through life in slow motion. Conversations, work, even getting dressed feels like a monumental effort.": "Quite Depressed",   
    "Sometimes, I wonder if people would even notice if I disappeared. The thoughts creep in at night, and I can't seem to shake them off.": "Quite Depressed"
}





PHQ9_MAPPING_PROMPT_NEW = """
The following text is a description of a person's mental health. Extract relevant symptoms and classify them according to the PHQ-9 checklist.
Each PHQ-9 category should also be assigned a severity score from 0 to 4 (0 = not at all, 1 = several days, 2 = more than half the days, 3 = nearly every day, 4 = extreme severity).

PHQ-9 categories:
1. Little interest or pleasure in doing things
2. Feeling down, depressed, or hopeless
3. Trouble falling or staying asleep, or sleeping too much
4. Feeling tired or having little energy
5. Poor appetite or overeating
6. Feeling bad about yourself or that you are a failure
7. Trouble concentrating on things
8. Moving or speaking so slowly that other people notice
9. Thoughts that you would be better off dead or hurting yourself in some way

Now, extract and classify the relevant symptoms from this text and assign an appropriate score (0-4) to each category:
{text_sample}

Return the extracted symptoms in a structured format, listing each PHQ-9 category, the symptom description, and the severity score.

**STRICT JSON RESPONSE REQUIRED!**
You MUST return output in **valid JSON format ONLY** with NO explanations or additional text. The below is an example of JSON
format that i am looking for.

### JSON Output Format:
[
  {{
    "category": "<PHQ9 category>",
    "score": <PHQ9 category severity score>,
    "symptom": <Symptom which justifies the score>
  }},
  {{
    "category": "<PHQ9 category>",
    "score": <PHQ9 category severity score>,
    "symptom": <Symptom which justifies the score>
  }},
  {{
    "category": "<PHQ9 category>",
    "score": <PHQ9 category severity score>,
    "symptom": <Symptom which justifies the score>
  }}
]

 DO NOT WRITE ANY TEXT AFTER THE JSON OUTPUT.

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




