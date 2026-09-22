# =====================================================
# SMART APFC AI
# Stage 13.1
# Remaining Useful Life Calculation
# Output: Hours
# =====================================================


RATED_LIFE_HOURS = 100000



def calculate_rul(capacitor):


    health = capacitor.get(
        "health",
        100
    )


    temperature = capacitor.get(
        "temperature",
        25
    )


    switching_count = capacitor.get(
        "switching_count",
        0
    )


    operating_seconds = capacitor.get(
        "operating_seconds",
        0
    )


    operating_hours = (

        operating_seconds

        /

        3600

    )



    # -----------------------------
    # Health effect
    # -----------------------------

    health_factor = health / 100



    # -----------------------------
    # Temperature effect
    # -----------------------------

    if temperature <= 40:


        temperature_factor = 1



    else:


        temperature_factor = (

            1

            -

            (

                (temperature - 40)

                /

                120

            )

        )



    if temperature_factor < 0.5:

        temperature_factor = 0.5




    # -----------------------------
    # Switching effect
    # -----------------------------


    switching_factor = (

        1

        -

        (

            switching_count

            /

            10000

        )

    )



    if switching_factor < 0.5:

        switching_factor = 0.5





    # -----------------------------
    # Remaining life
    # -----------------------------


    remaining_hours = (

        RATED_LIFE_HOURS

        *

        health_factor

        *

        temperature_factor

        *

        switching_factor

    )



    remaining_hours -= operating_hours



    if remaining_hours < 0:

        remaining_hours = 0



    return round(

        remaining_hours,

        2

    )