import os
import datetime


def lambda_handler(event, context):
    print(event)
    number = os.environ["UserPhoneNumber"]
    escalation_number = number
    onCallScheuld = {
        0:{'TargetContact': number, 'EscalationContact': escalation_number},
        1:{'TargetContact': number, 'EscalationContact': escalation_number},
        2:{'TargetContact': number, 'EscalationContact': escalation_number},
        3:{'TargetContact': number, 'EscalationContact': escalation_number},
        4:{'TargetContact': number, 'EscalationContact': escalation_number},
        5:{'TargetContact': number, 'EscalationContact': escalation_number},
        6:{'TargetContact': number, 'EscalationContact': escalation_number},
    }
    dayOfWeek = datetime.datetime.today().weekday()
    return onCallScheuld[dayOfWeek]