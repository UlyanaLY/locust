from config.config import logger

def check_http_response(response, params_to_check) -> bool:
    result = None

    try:
        assert params_to_check in response.text

    except AssertionError as err:
        response.failure(f"Assertion error: text pattern {params_to_check} was not found in response body!")
        logger.warning(f"Assertion error: text pattern {params_to_check} was not found in response body!")
    else:
        result = True

    finally:
        return result        

