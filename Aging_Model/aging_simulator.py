# =====================================================
# SMART APFC AGING SIMULATOR
# Stage 12.1 Intelligent Rotation
# Thermal + Aging Model
# =====================================================


import time

from Aging_Model.capacitor_database import capacitors



# =====================================================
# SETTINGS
# =====================================================


# 1 minute real time = 10 hours operation

TIME_SCALE = 600



# Base degradation

BASE_AGING_RATE = 0.00005



# =====================================================
# THERMAL SETTINGS
# =====================================================


AMBIENT_TEMP = 25


MAX_TEMP = 85



# Slow heating

HEAT_RATE = 0.10



# Cooling 3x faster

COOL_RATE = 0.15



# =====================================================
# MEMORY
# =====================================================


last_update = time.time()



previous_state = {

    "CAP1":"OFF",
    "CAP2":"OFF",
    "CAP3":"OFF",
    "CAP4":"OFF",
    "CAP5":"OFF",
    "CAP6":"OFF"

}




# =====================================================
# TEMPERATURE MODEL
# =====================================================


def update_temperature(
        info,
        is_on,
        reactive_power,
        elapsed
):


    current_temp = info.get(
        "temperature",
        AMBIENT_TEMP
    )


    health = info.get(
        "health",
        100
    )



    # aging effect

    aging_factor = (
        (100-health)
        /
        100
    )



    # reactive stress

    var_stress = min(
        reactive_power / 100,
        1
    )




    if is_on:


        # =========================
        # SLOW HEATING
        # =========================


        temperature_rise = (

            HEAT_RATE

            *

            elapsed

            *

            (
                1
                +
                (var_stress * 0.3)
                +
                (aging_factor * 0.3)
            )

        )


        new_temp = (

            current_temp

            +

            temperature_rise

        )




    else:


        # =========================
        # FAST COOLING
        # =========================


        temperature_drop = (

            COOL_RATE

            *

            elapsed

            *

            (
                current_temp
                -
                AMBIENT_TEMP
            )

        )


        new_temp = (

            current_temp

            -

            temperature_drop

        )





    # limits


    if new_temp < AMBIENT_TEMP:

        new_temp = AMBIENT_TEMP



    if new_temp > MAX_TEMP:

        new_temp = MAX_TEMP




    info["temperature"] = round(
        new_temp,
        2
    )





# =====================================================
# AGING UPDATE
# =====================================================


def update_aging(
        relay_status,
        reactive_power
):


    global last_update
    global previous_state



    now=time.time()


    elapsed = now-last_update



    if elapsed < 1:

        return capacitors




    last_update = now




    for cap,state in relay_status.items():



        info = capacitors[cap]



        # =========================
        # TEMPERATURE UPDATE
        # =========================


        update_temperature(

            info,

            state=="ON",

            reactive_power,

            elapsed

        )





        # =========================
        # SWITCH COUNT
        # =========================


        if (

            state=="ON"

            and

            previous_state[cap]=="OFF"

        ):


            info["switching_count"] += 1


            info["last_switch"] = now






        # =========================
        # AGING
        # =========================


        if state=="ON":



            simulated_seconds = (

                elapsed

                *

                TIME_SCALE

            )



            info["operating_seconds"] += simulated_seconds





            stress_factor = max(

                reactive_power / 100,

                0

            )





            thermal_stress = max(

                info["temperature"]

                -

                25,

                0

            )






            degradation = (

                BASE_AGING_RATE

                *

                simulated_seconds

                *

                (

                    1

                    +

                    stress_factor

                    +

                    (

                        thermal_stress

                        *

                        0.002

                    )

                )

            )






            info["health"] -= degradation





            if info["health"] < 0:

                info["health"]=0






            info["age"] += (

                simulated_seconds

                /

                36000

            )







        # status update


        info["status"]=state





    previous_state = relay_status.copy()



    return capacitors