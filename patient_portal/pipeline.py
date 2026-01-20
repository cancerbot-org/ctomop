def save_profile_info(backend, user, response, *args, **kwargs):
    """
    Custom pipeline to ensure email and profile info from Google is saved
    """
    if backend.name == 'google-oauth2':
        # Get email from Google response
        email = response.get('email')
        print(f"DEBUG: Google email = {email}")  # Debug line
        
        if email:
            user.email = email
        
        # Get first and last name
        given_name = response.get('given_name', '')
        family_name = response.get('family_name', '')
        
        if given_name:
            user.first_name = given_name
        if family_name:
            user.last_name = family_name
        
        user.save()
        print(f"DEBUG: Saved user - email={user.email}, name={user.first_name} {user.last_name}")
    
    return {'user': user}