# Function to check for similar interests
def has_similar_interests(user1, user2):
    interests1 = set(user1.interests.split(", "))
    interests2 = set(user2.interests.split(", "))
    return not interests1.isdisjoint(interests2)
