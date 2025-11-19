# John Asaro and Derin Gezgin 9/15/25
# Example fuzzy agent for Xpilot as a reference.

import libpyAI as ai

SHOT_ALERT_THRESHOLD = 60

def angle_diff(ang1, ang2):
    return ((ang1 - ang2 + 180) % 360) - 180

def trapezoid(x, trapezoid_tuple):
    """Trapezoidal membership function with a tuple of (left_foot, left_shoulder, right_shoulder, right_foot)."""
    left_foot, left_shoulder, right_shoulder, right_foot = trapezoid_tuple
    if x <= left_foot or x >= right_foot:  # If it is outside of the trapezoid, return 0
        return 0.0
    elif left_shoulder <= x <= right_shoulder:
        return 1.0
    elif left_foot < x < left_shoulder:  # If it is between the left foot and left shoulder, return the linear function
        return (x - left_foot) / (left_shoulder - left_foot)
    elif right_shoulder < x < right_foot:  # If it is between the right shoulder and right foot, return the linear function
        return (right_shoulder - x) / (right_shoulder - right_foot)

def fuzzy_and(values):
    """Basic fuzzy AND function that returns the minimum of the input values."""
    return min(values) if values else 0.0

def fuzzy_or(values):
    """Basic fuzzy OR function that returns the maximum of the input values."""
    return max(values) if values else 0.0

def weighted_average(pairs, default_value=0.0):
    """Weighted average for crisp outputs."""
    numerator = 0.0
    denominator = 0.0
    for weight, value in pairs:
        if weight <= 0.0:  # Skip if weight is 0 or negative
            continue
        numerator += weight * value
        denominator += weight
    if denominator == 0.0:
        return default_value
    return numerator / denominator

def normalize(value, range_tuple):
    """Normalize a value to the range [0, 1]."""
    min_value, max_value = range_tuple
    return (value - min_value) / (max_value - min_value)

def normalize_trapezoid(trapezoid_tuple, normalization_range):
    """Normalize a trapezoid tuple from raw values to [0,1] range."""
    return tuple(normalize(val, normalization_range) for val in trapezoid_tuple)

def fuzzify(input_value, fuzzy_functions, labels):
    """
    Fuzzify an input value using the provided fuzzy functions and return a dictionary of labels and their membership values.
    """
    if len(fuzzy_functions) != len(labels):
        raise ValueError("Number of fuzzy functions must match number of labels")
    
    if len(fuzzy_functions) == 0:
        raise ValueError("Must provide at least one fuzzy function and label")
    
    fuzzified_values = {}
    for func_params, label in zip(fuzzy_functions, labels):
        membership_value = trapezoid(input_value, func_params)
        fuzzified_values[label] = membership_value
    
    return fuzzified_values

# NORMALIZATION VALUES
DISTANCE_NORMALIZATION_RANGE = (0, 1500)
SPEED_NORMALIZATION_RANGE = (0, 20)

# FUZZY SETS for LINGUISTIC VARIABLE DISTANCE (raw values 0-1500)
DIST_DANGER_TRAPEZOID = (-0.001, 0, 200, 250)
DIST_SAFE_TRAPEZOID = (240, 400, 500, 600)
DIST_FAR_TRAPEZOID = (550, 650, 1500, 1500.1)
DISTANCE_FUNCTIONS = [normalize_trapezoid(t, DISTANCE_NORMALIZATION_RANGE) for t in [DIST_DANGER_TRAPEZOID, DIST_SAFE_TRAPEZOID, DIST_FAR_TRAPEZOID]]
DISTANCE_LABELS = ["danger", "safe", "far"]

# FUZZY SETS for LINGUISTIC VARIABLE SPEED (raw values 0-20)
SPEED_STOP_TRAPEZOID = (-0.001, 0, 0.7, 1)
SPEED_SLOW_TRAPEZOID = (0.8, 2, 2.5, 3.0)
SPEED_MEDIUM_TRAPEZOID = (2.8, 6.0, 8.0, 10.0)
SPEED_FAST_TRAPEZOID = (8.0, 10.0, 20.0, 20.02)
SPEED_FUNCTIONS = [normalize_trapezoid(trap, SPEED_NORMALIZATION_RANGE) for trap in [SPEED_STOP_TRAPEZOID, SPEED_SLOW_TRAPEZOID, SPEED_MEDIUM_TRAPEZOID, SPEED_FAST_TRAPEZOID]]
SPEED_LABELS = ["stop", "slow", "medium", "fast"]

# FUZZY SETS for LINGUISTIC VARIABLE ENEMY DISTANCE (raw values 0-1500) 
ENEMY_CLOSE_TRAPEZOID = (-0.001, 0, 80, 120)
ENEMY_MEDIUM_TRAPEZOID = (80, 150, 750, 800)
ENEMY_FAR_TRAPEZOID = (775, 850, 1500, 1500.2)
ENEMY_FUNCTIONS = [normalize_trapezoid(trap, DISTANCE_NORMALIZATION_RANGE) for trap in [ENEMY_CLOSE_TRAPEZOID, ENEMY_MEDIUM_TRAPEZOID, ENEMY_FAR_TRAPEZOID]]
ENEMY_LABELS = ["close", "medium", "far"]

# FUZZY SETS for LINGUISTIC VARIABLE AIM ALIGNMENT (raw values 0-180 degrees, magnitude only)
AIM_ALIGNED_TRAPEZOID = (-0.001, 0, 5, 8)
AIM_SLIGHT_MISALIGNED_TRAPEZOID = (7, 15, 20, 25)
AIM_MISALIGNED_TRAPEZOID = (20, 25, 180, 180)
AIM_FUNCTIONS = [normalize_trapezoid(trap, (0, 180)) for trap in [AIM_ALIGNED_TRAPEZOID, AIM_SLIGHT_MISALIGNED_TRAPEZOID, AIM_MISALIGNED_TRAPEZOID]]
AIM_LABELS = ["aligned", "slight_misaligned", "misaligned"]

# FUZZY SETS for LINGUISTIC VARIABLE FURTHEST ALIGNMENT (raw values 0-180 degrees, magnitude only)
FURTHEST_ALIGNED_TRAPEZOID = (-0.001, 0, 10, 15)
FURTHEST_SLIGHT_MISALIGNED_TRAPEZOID = (15, 30, 40, 50)
FURTHEST_MISALIGNED_TRAPEZOID = (50, 80, 180, 180)
FURTHEST_FUNCTIONS = [normalize_trapezoid(trap, (0, 180)) for trap in [FURTHEST_ALIGNED_TRAPEZOID, FURTHEST_SLIGHT_MISALIGNED_TRAPEZOID, FURTHEST_MISALIGNED_TRAPEZOID]]
FURTHEST_LABELS = ["aligned", "slight_misaligned", "misaligned"]

# FUZZY SETS for LINGUISTIC VARIABLE SHOT ALERT (raw values 0-100)
SHOT_NONE_TRAPEZOID = (-0.001, 0, 0, 1)
SHOT_LOW_TRAPEZOID = (1, 10, 30, 40)
SHOT_MEDIUM_TRAPEZOID = (30, 50, 60, 70)
SHOT_HIGH_TRAPEZOID = (60, 80, 100, 100)
SHOT_FUNCTIONS = [normalize_trapezoid(trap, (0, 100)) for trap in [SHOT_NONE_TRAPEZOID, SHOT_LOW_TRAPEZOID, SHOT_MEDIUM_TRAPEZOID, SHOT_HIGH_TRAPEZOID]]
SHOT_LABELS = ["none", "low", "medium", "high"]

# FUZZY SETS for LINGUISTIC VARIABLE GOING BACKWARDS (raw values 0-180 degrees)
BACKWARDS_NO_TRAPEZOID = (-0.001, 0, 60, 80)
BACKWARDS_YES_TRAPEZOID = (80, 100, 180, 180)
BACKWARDS_FUNCTIONS = [normalize_trapezoid(trap, (0, 180)) for trap in [BACKWARDS_NO_TRAPEZOID, BACKWARDS_YES_TRAPEZOID]]
BACKWARDS_LABELS = ["no", "yes"]

def AI_loop():
    # Release keys
    ai.thrust(0)
    ai.turnLeft(0)
    ai.turnRight(0)

    # Standardize turn speed
    ai.setTurnSpeedDeg(20)

    agent_heading = int(ai.selfHeadingDeg())
    agent_tracking = int(ai.selfTrackingDeg())
    agent_speed = int(ai.selfSpeed())
    agent_aim = int(ai.aimdir(0))
    shot_alert = int(ai.shotAlert(0))
    enemy_dist = int(ai.enemyDistance(0))
        
    feelers = []
    for i in range(0, 360, 1): feelers.append(ai.wallFeeler(1500, agent_heading + i))
    
    # Determined feelers
    front_dist = feelers[0]
    back_dist = feelers[180]
    back_left_dist = feelers[175]
    back_right_dist = feelers[185]

    # Identify the closest and furthest distances in the set of feelers
    closest_dist = min(feelers)
    furthest_dist = max(feelers)

    # Identify the closest and furthest angle values which are also indexes
    closest_angle = (agent_heading + feelers.index(closest_dist)) % 360
    furthest_angle = (agent_heading + feelers.index(furthest_dist)) % 360

    heading_tracking_diff = angle_diff(agent_tracking, agent_heading)
    closest_diff = angle_diff(closest_angle, agent_heading)
    furthest_diff = angle_diff(furthest_angle, agent_heading)
    
    # Only calculate aim_diff and aim_feeler if we have a valid target
    if agent_aim != -1:
        aim_diff = angle_diff(agent_aim, agent_heading)
    else:
        aim_diff = 0  # Default value when no target
    
    # Calculate going backwards and back danger
    going_backwards_angle = abs(heading_tracking_diff)

    # Normalize all variables that we are going to use in the fuzzy expert system
    normalized_speed = normalize(agent_speed, SPEED_NORMALIZATION_RANGE)
    normalized_front_dist = normalize(front_dist, DISTANCE_NORMALIZATION_RANGE)
    normalized_back_dist = normalize(back_dist, DISTANCE_NORMALIZATION_RANGE)
    normalized_back_left_dist = normalize(back_left_dist, DISTANCE_NORMALIZATION_RANGE)
    normalized_back_right_dist = normalize(back_right_dist, DISTANCE_NORMALIZATION_RANGE)
    normalized_going_backwards = normalize(going_backwards_angle, (0, 180))

    # Fuzzify all variables that we are going to use in the fuzzy expert system
    fuzzified_speed = fuzzify(normalized_speed, SPEED_FUNCTIONS, SPEED_LABELS)
    fuzzified_front_dist = fuzzify(normalized_front_dist, DISTANCE_FUNCTIONS, DISTANCE_LABELS)
    fuzzified_back_dist = fuzzify(normalized_back_dist, DISTANCE_FUNCTIONS, DISTANCE_LABELS)
    fuzzified_back_left_dist = fuzzify(normalized_back_left_dist, DISTANCE_FUNCTIONS, DISTANCE_LABELS)
    fuzzified_back_right_dist = fuzzify(normalized_back_right_dist, DISTANCE_FUNCTIONS, DISTANCE_LABELS)
    fuzzified_going_backwards = fuzzify(normalized_going_backwards, BACKWARDS_FUNCTIONS, BACKWARDS_LABELS)
    
    # Only fuzzify aim if we have a valid target
    if agent_aim != -1:
        normalized_aim_diff = normalize(abs(aim_diff), (0, 180))
        fuzzified_aim = fuzzify(normalized_aim_diff, AIM_FUNCTIONS, AIM_LABELS)
    else:
        fuzzified_aim = {"aligned": 0.0, "slight_misaligned": 0.0, "misaligned": 0.0}
    
    # Fuzzify furthest alignment (how aligned we are with the safest direction)
    normalized_furthest_diff = normalize(abs(furthest_diff), (0, 180))
    fuzzified_furthest = fuzzify(normalized_furthest_diff, FURTHEST_FUNCTIONS, FURTHEST_LABELS)
    
    # Only fuzzify enemy distance if there's an enemy detected (within reasonable range)
    if enemy_dist != -1 and enemy_dist <= 9000:
        normalized_enemy_dist = normalize(enemy_dist, DISTANCE_NORMALIZATION_RANGE)
        fuzzified_enemy_dist = fuzzify(normalized_enemy_dist, ENEMY_FUNCTIONS, ENEMY_LABELS)
    else:
        fuzzified_enemy_dist = {"close": 0.0, "medium": 0.0, "far": 0.0}
    
    # Only fuzzify shot alert if there's an active shot alert
    if shot_alert != -1:
        normalized_shot_alert = normalize(shot_alert, (0, 100))
        fuzzified_shot_alert = fuzzify(normalized_shot_alert, SHOT_FUNCTIONS, SHOT_LABELS)
    else:
        fuzzified_shot_alert = {"none": 1.0, "low": 0.0, "medium": 0.0, "high": 0.0}
    
    # THRUST FUZZY RULES (based on rule-based agent logic)
    
    # Small rules to use in the main thrust rules
    back_danger_fuzzy = fuzzy_and([fuzzified_back_dist["danger"], fuzzified_back_left_dist["danger"], fuzzified_back_right_dist["danger"]])
    front_clear_fuzzy = fuzzy_or([fuzzified_front_dist["safe"], fuzzified_front_dist["far"]])
    safe_speed_fuzzy = fuzzy_or([fuzzified_speed["stop"], fuzzified_speed["slow"]])
    
    # Thrust when front is clear, speed is low, and aligned with safest direction
    thrust_rule1 = fuzzy_and([front_clear_fuzzy, safe_speed_fuzzy, fuzzified_furthest["aligned"]])
    
    # Thrust when going backwards and in danger from behind
    thrust_rule2 = fuzzy_and([fuzzified_going_backwards["yes"], back_danger_fuzzy])
    
    # Thrust when there's an incoming shot alert
    thrust_rule3 = fuzzy_or([fuzzified_shot_alert["low"], fuzzified_shot_alert["medium"], fuzzified_shot_alert["high"]])
    
    # DEFUZZIFICATION for thrust using weighted average
    NO_THRUST = 0.0
    LOW_THRUST = 0.5
    HIGH_THRUST = 1.0
    
    # Create weight-value pairs for defuzzification
    thrust_pairs = [
        (thrust_rule1, HIGH_THRUST),    # Clear path gets high thrust
        (thrust_rule2, HIGH_THRUST),    # Escape danger gets high thrust  
        (thrust_rule3, LOW_THRUST)      # Shot evasion gets low thrust
    ]
    
    # Calculate crisp thrust output using weighted average
    thrust_output = weighted_average(thrust_pairs, default_value=NO_THRUST)
    
    # Apply thrust based on defuzzified output
    THRUST_THRESHOLD = 0.1  # Minimum output to activate thrust
    if thrust_output > THRUST_THRESHOLD: ai.thrust(1)
    
    # Production system for turning (this is from our original rule-based agent)
    if ai.enemyDistance(0) < 100 and aim_diff > 0 and agent_speed < 2.5: ai.turnLeft(1)
    
    elif ai.enemyDistance(0) < 100 and aim_diff <= 0 and agent_speed < 2.5: ai.turnRight(1) 

    elif closest_dist < 70 and closest_diff > 0 and agent_speed != 0: ai.turnRight(1) 

    elif closest_dist < 70 and closest_diff <= 0 and agent_speed != 0: ai.turnLeft(1) 

    elif closest_dist < 100 and furthest_diff > 0: ai.turnLeft(1) 

    elif closest_dist < 100 and furthest_diff <= 0: ai.turnRight(1) 

    elif 0 < shot_alert < SHOT_ALERT_THRESHOLD and furthest_diff > 0: ai.turnLeft(1)

    elif 0 < shot_alert < SHOT_ALERT_THRESHOLD and furthest_diff <= 0: ai.turnRight(1)

    elif agent_aim != -1 and abs(aim_diff) > 1 and aim_diff > 0: ai.turnLeft(1)

    elif agent_aim != -1 and abs(aim_diff) > 1 and aim_diff <= 0: ai.turnRight(1)

    elif abs(furthest_diff) > 15 and furthest_diff > 0: ai.turnLeft(1)

    elif abs(furthest_diff) > 15 and furthest_diff <= 0: ai.turnRight(1) 

    ### SHOOTING FUZZY RULES ###
    
    # Shoot when aligned with enemy and close
    enemy_close_fuzzy = fuzzy_or([fuzzified_enemy_dist["close"], fuzzified_enemy_dist["medium"]])
    shoot_rule1 = fuzzy_and([fuzzified_aim["aligned"], enemy_close_fuzzy])
    
    shoot_pairs = [(shoot_rule1, 1.0)]  # Full weight for aligned and close

    shoot_activation = weighted_average(shoot_pairs, default_value=0.0)

    SHOOT_THRESHOLD = 0.1  # Minimum activation level to shoot
    if shoot_activation > SHOOT_THRESHOLD:
        ai.fireShot()

ai.start(AI_loop,["-name","JohnDerinFuzzy","-join","localhost"])
