
from lib.base import GitlabBaseAction
from gitlab.exceptions import GitlabConnectionError

from st2common import log as logging

LOG = logging.getLogger(__name__)

__all__ = [
    'PyGitlabList'
]


class PyGitlabList(GitlabBaseAction):
    """Default Module action class"""

    def run(self, **kwargs):
        """
        Default organization action method.
        :api_module: Python Gitlab base module to use
        :api_submodule: Python Gitlab sub module to use
        :api_payload: Data that will be submitted to Gitlab instance as part of API call
        :moduleID: ID of the module to get if a submodule is provided
        # Only one of the 3 tokens should be defined. If multiple token types are supplied
        # a token will be selected using the following precedence:
        #    Private > OAuth > Job
        # If no tokens are provided an anonymous connection to the Gitlab instance will be
        # established
        :private_token: Specify Private token to use for connection to Gitlab instance
        :oauth_token: Specify OAUTH token to use for connection to Gitlab instance
        :job_token: Specify Job token to use for connection to Gitlab instance
        """

        private_token = kwargs.pop("private_token") or self.config.get('private_token', None)
        oauth_token = kwargs.pop("oauth_token") or self.config.get('oauth_token', None)
        job_token = kwargs.pop("job_token") or self.config.get('job_token', None)
        api_module = kwargs.pop("api_module")
        self.logger.debug(f"Gitlab Module : {api_module}")
        api_submodule = kwargs.pop(api_submodule)
        self.logger.debug(f"Gitlab Method : {api_submodule}")
        api_payload = kwargs.pop("api_payload")
        parameters = {}
        if api_payload:
            parameters = {k: v for k, v in api_payload.items() if v is not None}

        pyglab = self.get_gitlab(
            private_token=private_token,
            oauth_token=oauth_token,
            job_token=job_token
            )
        call = getattr(getattr(pyglab, api_module), list)

        try:
            response = call(**parameters)
            if return_payload:
                response = (response, parameters)
            return (True, response)
        except APIError as err:
            error = {
                "message": err.message,
                "operation": err.operation,
                "reason": err.reason,
                "status": err.status,
                "tag": err.tag,
            }
            if return_payload:
                error = (error, parameters)
            return (False, error)

def do_update(obj, api_module, parameters):


def do_call(obj):

