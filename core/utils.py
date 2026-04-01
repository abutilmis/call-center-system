import json

def build_summary(correction):
    """
    Generates a formatted summary string for a ClientCorrection request.
    This string is used for both the Telegram notification and the UI summary display.
    """
    summary = ""
    
    if correction.correction_type == 'name':
        old_name = correction.old_data.get('full_name')
        if not old_name:
            old_fn = correction.old_data.get('first_name', '')
            old_fan = correction.old_data.get('father_name', '')
            old_gn = correction.old_data.get('grandfather_name', '')
            old_name = " ".join(filter(None, [old_fn, old_fan, old_gn]))

        new_name = correction.new_data.get('full_name')
        if not new_name:
            new_fn = correction.new_data.get('first_name', '')
            new_fan = correction.new_data.get('father_name', '')
            new_gn = correction.new_data.get('grandfather_name', '')
            new_name = " ".join(filter(None, [new_fn, new_fan, new_gn]))

        raw_summary = f"❌{old_name}\n✅{new_name}\n{correction.labor_id}\n{correction.phone}"
        summary = "\n".join([line for line in raw_summary.split("\n") if line.strip()])

    elif correction.correction_type == 'dob':
        old_dob = correction.old_data.get('dob', '')
        new_dob = correction.new_data.get('dob', '')
        
        try:
            # Format YYYY-MM-DD to DD-MM-YYYY
            if old_dob and len(old_dob) == 10: 
                old_dob = f"{old_dob[8:10]}-{old_dob[5:7]}-{old_dob[0:4]}"
            if new_dob and len(new_dob) == 10: 
                new_dob = f"{new_dob[8:10]}-{new_dob[5:7]}-{new_dob[0:4]}"
        except:
            pass
            
        lines = [
            correction.client_name,
            f"Phone: {correction.phone}"
        ]
        if correction.labor_id:
            lines.append(f"Labor ID: {correction.labor_id}")
            
        if old_dob: lines.append(f"❌{old_dob}")
        if new_dob: lines.append(f"✅{new_dob}")
        summary = "\n".join(lines)

    elif correction.correction_type == 'sex':
        comment = correction.new_data.get('comment', 'Fixing prefix')
        lines = [
            correction.labor_id,
            correction.client_name,
            correction.phone,
            f"Comment: {comment}"
        ]
        summary = "\n".join([line for line in lines if line.strip()])

    elif correction.correction_type == 'too_many_attempt':
        lines = [
            correction.phone,
            correction.client_name,
            "Too many Attempts"
        ]
        summary = "\n".join([line for line in lines if line.strip()])

    return summary

def build_status_update(correction):
    """
    Generates a notification string for when a supervisor approves or rejects a request.
    """
    status_emoji = "✅" if correction.status == 'approved' else "❌"
    lines = [
        f"{status_emoji} <b>Request {correction.status.upper()}</b>",
        f"<b>Type:</b> {correction.get_correction_type_display()}",
        f"<b>Client:</b> {correction.client_name}",
        f"<b>Phone:</b> {correction.phone}",
    ]
    if correction.supervisor_comment:
        lines.append(f"<b>Comment:</b> {correction.supervisor_comment}")
    
    return "\n".join(lines)
