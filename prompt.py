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
    "Lately, I just don't feel like doing the things I used to enjoy. I used to love painting, but now even picking up a brush feels like a chore.",
    "I feel tired all the time, even after a full night's sleep. It’s like my body is running on low battery, and I just can't recharge.",
    "Sometimes, I feel down for no apparent reason. I can still function, but there’s this underlying sadness that just doesn’t go away.",
    "I’ve been eating less than usual, not because I’m trying to, but because food just doesn’t seem appealing anymore.",
    "It takes so much effort to get out of bed in the morning. I know I have things to do, but I keep hitting snooze and lying there, staring at the ceiling.",
    "I find myself zoning out at work, struggling to concentrate. I used to be so sharp, but now even small tasks seem overwhelming.",
    "I feel like I’m failing at everything—my job, my relationships, even basic self-care. It’s like no matter what I do, it’s never enough.",
    "I don’t talk to my friends as much anymore. They invite me out, but I always find an excuse to stay home. It just feels easier to be alone.",
    "I feel like I’m moving through life in slow motion. Conversations, work, even getting dressed feels like a monumental effort.",
    "Sometimes, I wonder if people would even notice if I disappeared. The thoughts creep in at night, and I can't seem to shake them off."
]


SCORE_PROMPT="""
Given the following PHQ-9 responses with scores from 0-4, compute the total score and classify the severity:

{phq9_responses}

Classification Criteria:
- If total score < 4, classify as 'Not Depressed'.
- If total score is between 4 and 10, classify as 'Mildly Depressed'.
- If total score > 10, classify as 'Quite Depressed'.

Return the total score and the classification label.
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
You MUST return output in **valid JSON format ONLY** with NO explanations or additional text.
Return an array of JSON objects. Each JSON object should have category, score and symptom.

"""


