import sqlfluff


def check_syntax(query):
    """
    Check if the SQL query has a valid syntax. If it is the case, return true. Else, return False and the error
    """
    try:
        sqlfluff.parse(query)
        return True, None
    except Exception as err:
        return False, f"Linting Error: {err}"
	

def check_not_too_heavy(query):
    """
    Check that the request is not so heavy that it might make the database crash
    For now, only fordid the usage of the UNION between two tables
    """
    if 'union' in query.lower():
        return False
    else:
        return True


def check_valid_mode(mode):
    """
    Check that the mode passed in the request is one of the 4 modes allowed
    """
    if mode in ['write', 'direct-hit', 'random', 'customized']:
        return True
    else : return False


def sanitize_request(request):
    """
    Sanitize the request by performing some security checks and making sure that we don't send something
    that cant be treated.
    If everything is ok, return True and the request
    Else, returns False and an error message to help understand what went wrong
    """
    print("In sanitize request, request=",request)
    data = request.get_json()
    mode = data.get('mode')
    query = data.get('query')
    if not check_valid_mode(mode):
        return False, f"Invalid mode {mode}"
    res, err = check_syntax(query)
    if not res:
        return False, err
    if not check_not_too_heavy(query):
        return False, "Forbidden request: too heavy"
    return True, request