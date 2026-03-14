def send_status_email(to_email: str, vendor_name: str, event_date: str, new_status: str):
    if new_status == "ACCEPTED":
        print(f"EMAIL SENT TO {to_email}: Great news! {vendor_name} accepted your reservation for {event_date}.")
    elif new_status == "DENIED":
        print(f"EMAIL SENT TO {to_email}: Update: {vendor_name} is unfortunately unable to accommodate your reservation for {event_date}.")