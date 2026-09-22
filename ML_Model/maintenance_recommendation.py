# =====================================================
# SMART APFC AI
# Stage 13.3
# AI Maintenance Recommendation Engine
# =====================================================



def maintenance_recommendation(
        health,
        rul_hours,
        risk_score,
        risk_level,
        temperature_status,
        temperature
):



    # =================================================
    # CRITICAL CONDITION
    # =================================================


    if (

        health < 50

        or

        risk_level == "HIGH"

        or

        rul_hours < 5000

        or

        temperature_status == "TRIPPED"

    ):


        return {


            "condition":
            "CRITICAL",


            "recommendation":
            "Replace Capacitor",


            "reason":
            "Low health, high failure risk or thermal fault"


        }






    # =================================================
    # WARNING CONDITION
    # =================================================


    elif (

        health < 75

        or

        risk_level == "MEDIUM"

        or

        rul_hours < 20000

        or

        temperature_status == "WARNING"

    ):



        return {


            "condition":
            "WARNING",


            "recommendation":
            "Monitor Closely",


            "reason":
            "Increasing stress detected"


        }







    # =================================================
    # NORMAL CONDITION
    # =================================================


    else:


        return {


            "condition":
            "HEALTHY",


            "recommendation":
            "Continue Operation",


            "reason":
            "Parameters within safe operating range"


        }