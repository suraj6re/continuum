# Layer 9 Configuration

# Ranking weights (must sum to 1.0)
RANKING_WEIGHTS = {
    "cost": 0.6,      # 60% - Cost is most important
    "distance": 0.3,  # 30% - Distance affects logistics
    "lead": 0.1       # 10% - Lead time for planning
}

# Distance filter (in kilometers)
MAX_DISTANCE_KM = 30

# Number of top suppliers to return
TOP_N_SUPPLIERS = 3

# Availability priority
AVAILABILITY_PRIORITY = {
    "in stock": 1.0,
    "limited": 0.8,
    "out of stock": 0.0
}
