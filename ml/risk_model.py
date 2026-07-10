def calculate_risk_score(age, followers, following, posts):

    score = 0

    if age < 30:
        score += 30

    if followers < 50:
        score += 20

    if following > followers * 5:
        score += 25

    if posts < 5:
        score += 25

    return min(score,100)