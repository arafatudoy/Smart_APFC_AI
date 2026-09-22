# =====================================================
# SMART APFC AI
# Stage 13.1
# Capacitor Failure Risk Prediction
# =====================================================



def calculate_risk_score(
        health,
        temperature,
        switching_count,
        operating_hours
):


    risk = 0



    # =================================
    # Health degradation
    # =================================


    if health < 85:

        risk += 20


    if health < 70:

        risk += 30


    if health < 50:

        risk += 30





    # =================================
    # Temperature stress
    # =================================


    if temperature > 50:

        risk += 20


    if temperature > 70:

        risk += 30





    # =================================
    # Switching stress
    # =================================


    if switching_count > 1000:

        risk += 10


    if switching_count > 5000:

        risk += 20






    # =================================
    # Operating hour stress
    # =================================


    if operating_hours > 50000:

        risk += 10


    if operating_hours > 80000:

        risk += 20





    # Limit

    if risk > 100:

        risk = 100



    return risk





# =====================================================
# RISK CATEGORY
# =====================================================


def risk_level(score):


    if score < 30:

        return "LOW"



    elif score < 60:

        return "MEDIUM"



    else:

        return "HIGH"