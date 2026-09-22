# =====================================================
# SMART APFC ALGORITHM
# Stage 12.6
# PF Control + Health + Temperature Rotation
# =====================================================


import math
import time

from Aging_Model.capacitor_database import capacitors
from Aging_Model.thermal_protection import thermal_protection



# =====================================================
# SETTINGS
# =====================================================


TARGET_PF = 0.95

MAX_PF = 0.96


# each capacitor VAR

CAP_VAR = 5



# rotation settings

HEALTH_MARGIN = 10

TEMP_LIMIT = 50

ROTATION_DELAY = 30



# relay protection

MIN_ON_TIME = 30



FAILED_LIMIT = 40





# =====================================================
# MEMORY
# =====================================================


current_selected = []


last_switch_time = 0


last_rotation_time = 0



relay_memory = {


"CAP1":{"state":"OFF","start":0},

"CAP2":{"state":"OFF","start":0},

"CAP3":{"state":"OFF","start":0},

"CAP4":{"state":"OFF","start":0},

"CAP5":{"state":"OFF","start":0},

"CAP6":{"state":"OFF","start":0}

}






# =====================================================
# RELAY
# =====================================================


def all_off():

    return {

        "CAP1":"OFF",
        "CAP2":"OFF",
        "CAP3":"OFF",
        "CAP4":"OFF",
        "CAP5":"OFF",
        "CAP6":"OFF"

    }






# =====================================================
# PF CALCULATION
# =====================================================


def calculate_pf(P,Q):


    S = math.sqrt(

        P*P + Q*Q

    )


    if S == 0:

        return 0



    pf = P/S


    if pf > 1:

        pf = 1



    return round(pf,3)






# =====================================================
# AFTER CAP PF
# =====================================================


def calculate_after_pf(P,Q,var):


    new_Q = Q-var


    if new_Q < 0:

        new_Q = 0



    return calculate_pf(

        P,

        new_Q

    )







# =====================================================
# REQUIRED VAR
# =====================================================


def calculate_required_var(P,Q):


    pf = calculate_pf(P,Q)



    if pf >= TARGET_PF:

        return 0



    phi1 = math.acos(pf)

    phi2 = math.acos(TARGET_PF)



    required = P*(

        math.tan(phi1)

        -

        math.tan(phi2)

    )



    if required < 0:

        required = 0



    return round(required,2)







# =====================================================
# FAILED CAPACITOR
# =====================================================


def failed_capacitors():


    failed=[]


    # health failure

    for cap,data in capacitors.items():


        if data["health"] <= FAILED_LIMIT:

            failed.append(cap)



    # thermal failure

    thermal_status,thermal_failed = thermal_protection(

        capacitors

    )



    for cap in thermal_failed:


        if cap not in failed:

            failed.append(cap)



    return failed






# =====================================================
# CAP SCORE
# =====================================================


def cap_score(cap):


    data = capacitors[cap]



    health = data.get(

        "health",

        100

    )


    temp = data.get(

        "temperature",

        25

    )



    temperature_penalty = max(

        0,

        temp-40

    )



    return (

        health

        -

        temperature_penalty

        -

        data.get(

            "switching_count",

            0

        )*0.2

    )







# =====================================================
# SELECT CAPACITORS
# =====================================================


def select_caps(P,Q):


    failed = failed_capacitors()



    available=[

        c for c in capacitors.keys()

        if c not in failed

    ]



    ranking=sorted(

        available,

        key=cap_score,

        reverse=True

    )



    best=[]

    best_error=999



    for number in range(

        1,

        len(ranking)+1

    ):


        installed = number*CAP_VAR



        pf = calculate_after_pf(

            P,

            Q,

            installed

        )



        if pf > MAX_PF:

            continue



        error = abs(

            TARGET_PF-pf

        )



        if error < best_error:


            best_error = error

            best = ranking[:number]



    return best




# =====================================================
# INTELLIGENT ROTATION
# Health Difference OR Temperature Protection
# =====================================================


def rotate_caps(selected):

    global last_rotation_time


    if len(selected) == 0:

        return selected



    now = time.time()



    # prevent frequent switching

    if now - last_rotation_time < ROTATION_DELAY:

        return selected




    # available OFF capacitors

    available = [

        c for c in capacitors.keys()

        if c not in selected

        and c not in failed_capacitors()

    ]




    if not available:

        return selected





    # find healthiest OFF capacitor

    healthiest_off = max(

        available,

        key=lambda x: capacitors[x]["health"]

    )




    healthiest_health = capacitors[healthiest_off]["health"]




    new_selection = selected.copy()





    # check all running capacitors

    for running_cap in selected:



        running_health = capacitors[running_cap]["health"]



        running_temp = capacitors[running_cap].get(

            "temperature",

            25

        )




        # health difference

        health_difference = (

            healthiest_health

            -

            running_health

        )





        # RULE 1:
        # OFF capacitor is 10% healthier


        health_condition = (

            health_difference >= HEALTH_MARGIN

        )





        # RULE 2:
        # ON capacitor temperature high


        temperature_condition = (

            running_temp >= TEMP_LIMIT

        )





        print(

            "ROTATION CHECK:",

            running_cap,

            "Health:",

            round(running_health,2),

            "Temp:",

            round(running_temp,2),

            "Health Difference:",

            round(health_difference,2)

        )






        if (

            health_condition

            or

            temperature_condition

        ):



            print(

                "ROTATING:",

                running_cap,

                "->",

                healthiest_off

            )




            new_selection.remove(

                running_cap

            )



            new_selection.append(

                healthiest_off

            )



            last_rotation_time = time.time()



            return new_selection





    return selected






# =====================================================
# MEMORY
# =====================================================


def update_memory(relay):


    now=time.time()



    for cap,state in relay.items():


        old = relay_memory[cap]["state"]



        if state=="ON" and old=="OFF":


            relay_memory[cap]["start"]=now



        relay_memory[cap]["state"]=state






# =====================================================
# MAIN APFC
# =====================================================

def smart_apfc(
        real_power,
        reactive_power,
        pf,
        health_data
):

    global current_selected
    global last_switch_time


    relay = all_off()

    now = time.time()


    if real_power < 5:

        current_selected=[]

        return {

            "relay":relay,

            "selected_capacitors":[],

            "after_pf":0,

            "reactive_reduction":0,

            "required_var":0

        }



    required_var = calculate_required_var(
        real_power,
        reactive_power
    )



    # ==============================
    # KEEP EXISTING SELECTION
    # ==============================

    if current_selected:

        selected = current_selected.copy()


    else:

        selected = select_caps(

            real_power,

            reactive_power

        )



    # ==============================
    # 30 SECOND HOLD
    # ==============================

    if current_selected:


        if now-last_switch_time < MIN_ON_TIME:


            selected=current_selected.copy()




    # ==============================
    # ROTATION CHECK
    # ==============================

    selected = rotate_caps(

        selected

    )



    if selected != current_selected:

        last_switch_time=time.time()



    current_selected = selected.copy()



    installed = len(selected)*CAP_VAR



    after = calculate_after_pf(

        real_power,

        reactive_power,

        installed

    )



    # PF protection

    while after > MAX_PF and len(selected)>0:


        selected.pop()


        installed=len(selected)*CAP_VAR


        after=calculate_after_pf(

            real_power,

            reactive_power,

            installed

        )



    current_selected=selected.copy()



    for cap in selected:

        relay[cap]="ON"



    update_memory(relay)



    return {


        "relay":relay,


        "selected_capacitors":selected,


        "after_pf":after,


        "reactive_reduction":installed,


        "required_var":required_var


    }