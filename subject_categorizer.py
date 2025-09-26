import re
from typing import Optional

# Subject categories and their keywords
SUBJECT_CATEGORIES = {
    "Mathematics": [
        "math", "algebra", "geometry", "calculus", "trigonometry", "arithmetic", "equation", 
        "formula", "theorem", "proof", "derivative", "integral", "matrix", "vector", 
        "probability", "statistics", "graph", "function", "polynomial", "logarithm",
        "sine", "cosine", "tangent", "quadratic", "linear", "exponential"
    ],
    "Science": [
        "physics", "chemistry", "biology", "science", "atom", "molecule", "cell", 
        "organism", "evolution", "genetics", "DNA", "photosynthesis", "respiration",
        "gravity", "force", "energy", "momentum", "wave", "light", "electricity",
        "magnetism", "chemical", "reaction", "element", "compound", "ecosystem"
    ],
    "History": [
        "history", "historical", "ancient", "medieval", "revolution", "war", "empire",
        "civilization", "culture", "democracy", "monarchy", "republic", "treaty",
        "constitution", "independence", "colonial", "renaissance", "reformation"
    ],
    "Geography": [
        "geography", "continent", "country", "capital", "mountain", "river", "ocean",
        "climate", "weather", "latitude", "longitude", "population", "map", "atlas",
        "desert", "forest", "plateau", "valley", "island", "peninsula"
    ],
    "Literature": [
        "literature", "poem", "poetry", "novel", "story", "author", "writer", "book",
        "character", "plot", "theme", "metaphor", "symbolism", "alliteration",
        "shakespeare", "prose", "verse", "narrative", "fiction", "non-fiction"
    ],
    "Computer Science": [
        "programming", "computer", "software", "hardware", "algorithm", "coding", "code",
        "python", "javascript", "java", "data structure", "database", "network",
        "internet", "website", "app", "application", "debugging", "variable",
        "function", "loop", "array", "object", "class"
    ],
    "Language Arts": [
        "grammar", "vocabulary", "spelling", "writing", "reading", "comprehension",
        "sentence", "paragraph", "essay", "verb", "noun", "adjective", "adverb",
        "punctuation", "comma", "period", "question mark", "exclamation"
    ],
    "Social Studies": [
        "government", "politics", "economics", "society", "community", "citizenship",
        "rights", "law", "justice", "democracy", "election", "vote", "tax",
        "economy", "market", "trade", "currency", "inflation"
    ]
}

def categorize_question(question: str) -> Optional[str]:
    """
    Categorize a question based on keywords and context
    Returns the most likely subject category or None if uncertain
    """
    if not question:
        return None
    
    question_lower = question.lower()
    
    # Count matches for each category
    category_scores = {}
    
    for category, keywords in SUBJECT_CATEGORIES.items():
        score = 0
        for keyword in keywords:
            # Count exact word matches (not partial)
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            matches = len(re.findall(pattern, question_lower))
            score += matches
            
            # Give extra weight to longer, more specific keywords
            if len(keyword) > 6 and matches > 0:
                score += 1
        
        if score > 0:
            category_scores[category] = score
    
    if not category_scores:
        return None
    
    # Return the category with the highest score
    best_category = max(category_scores.keys(), key=lambda k: category_scores[k])
    
    # Only return if we have a confident match (score >= 2 or single strong match)
    if category_scores[best_category] >= 2:
        return best_category
    elif category_scores[best_category] == 1:
        # Check if it's a strong single match (longer keyword)
        for keyword in SUBJECT_CATEGORIES[best_category]:
            if len(keyword) > 6 and keyword.lower() in question_lower:
                return best_category
    
    return None

def get_subject_specific_prompt(category: str) -> str:
    """
    Get additional prompt instructions based on the subject category
    """
    prompts = {
        "Mathematics": "Focus on step-by-step solutions, show your work clearly, and explain mathematical concepts with examples.",
        "Science": "Provide scientific explanations with examples from real life, include relevant facts and encourage further exploration.",
        "History": "Provide historical context, dates, and explain cause-and-effect relationships. Include relevant historical figures and events.",
        "Geography": "Include specific locations, geographical features, and relate to maps and spatial understanding.",
        "Literature": "Discuss literary techniques, themes, and provide examples from well-known works when relevant.",
        "Computer Science": "Provide clear code examples when relevant, explain concepts step-by-step, and relate to practical applications.",
        "Language Arts": "Focus on clear explanations of language rules, provide examples, and help with writing improvement.",
        "Social Studies": "Explain social concepts, governmental processes, and relate to current events when appropriate."
    }
    
    return prompts.get(category, "")

# Test function to verify categorization
def test_categorization():
    """Test the categorization function with sample questions"""
    test_questions = [
        "What is the quadratic formula?",
        "Explain photosynthesis",
        "Who was Napoleon Bonaparte?",
        "What is the capital of France?",
        "How do you write a for loop in Python?",
        "What is a metaphor in literature?",
        "How do you solve this math problem?",
        "What causes earthquakes?",
    ]
    
    for question in test_questions:
        category = categorize_question(question)
        print(f"'{question}' -> {category}")

if __name__ == "__main__":
    test_categorization()