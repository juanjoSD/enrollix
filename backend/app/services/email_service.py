def send_verification_email(email: str, token: str):
    verification_link = f"http://localhost:8000/confirm-email?token={token}"
    # Remplaçable
    print(f"[EMAIL] To: {email}")
    print(f"[EMAIL] Verification link: {verification_link}")