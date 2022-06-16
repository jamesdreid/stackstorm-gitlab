import gitlab
from gitlab import GitlabGetError, GitlabListError, exceptions

from st2common.runners.base_action import Action
from st2common import log as logging

LOG = logging.getLogger(__name__)


__all__ = [
    'GitlabBaseAction'
]

class GitlabBaseAction(Action):
    def __init__(self, config):
        super(GitlabBaseAction, self).__init__(config=config)

        # SSL Verify can be disabled in config or will be enabled by default
        self.ssl_verify = self.config.get('ssl_verify', True)

        # Timeout set in config or will default to 15
        self.timeout = self.config.get('timeout', 15)

        # API Version 4 is the only option available since 1.5.0
        self.api_version = self.config.get('api_version', 4)

        self.url = self.config.get('url', None)
        
        # # Only one of the 3 tokens should be defined. If multiple token types are supplied,
        # # a token will be selected using the following precedence:
        # #    Private > OAuth > Job
    
        # self.private_token = self.config.get('private_token', None)
        # self.oauth_token = self.config.get('oauth_token', None)
        # self.job_token = self.config.get('job_token', None)

        # Gitlab API limits per_page value to 100.  If not provided, the default will be 
        # set to 10 items returned per page
        self.per_page = self.config.get('per_page', 10)

        # Whether to retry after 500, 502, 503, 504 or 52x responses.  Defaults to false.
        self.retry_transient_errors = self.config.get('retry_transient_errors', False)

        self.gitlab = self.get_gitlab()

    def get_gitlab(self):
        gitlab_api = gitlab.Gitlab(
            ssl_verify = self.ssl_verify,
            timeout = self.timeout,
            api_version = self.api_version,
            url = self.url,
            private_token = self.private_token,
            oauth_token = self.oauth_token,
            job_token = self.job_token,
            per_page = self.per_page,
            retry_transient_errors = self.retry_transient_errors
        )
        return gitlab_api

    def gitlab_id_search(obj, text):
        """
        Helper function used to use the search option on the list method 
        of a Gitlab object when a text string is used with a get method
        instead of a int
        """
        try:
            call = getattr(obj, 'list')
        except AttributeError as e:
            LOG.debug("Object provided does not support list method."
            "Check source data and try again.")
            raise e
        try:
            response = call(search=text, top_level_only=True)
            if len(response) > 1:
                LOG.debug("Search string too general. Refine input text so it returns only a single value.")
                raise ValueError("Search string returned multiple results.")
            output = response[0].id
            return output
        except GitlabGetError:
            LOG.debug("Gitlab API GET request failed ")
            return output

    def gitlab_list(obj, parameters):
        """
        Function used to execute the list method on a Gitlab object
        and return a list of the objects attributes 
        """
        try:
            call = getattr(obj, 'list')
        except AttributeError as e:
            LOG.debug("Object provided does not support list method."
            "Check source data and try again.")
            raise e
        output = []
        try:
            response = call(**parameters)
            for entry in response:
                output.append(entry.attributes)
            return output
        except GitlabListError:
            LOG.debug("Gitlab API LIST request failed.")
            return output   

    def gitlab_get(obj, objid):
        """
        Function used to execute the get method on a Gitlab object
        and return the specific object requested based upon the objid
        submitted.  If the objid is a text string, a call to the ID search
        helper function will be made to resolve the numeric ID of the
        object requested
        """
        try:
            int(objid)
            call = getattr(obj, 'get')
            try:
                response = call(objid)
                output = response.attributes
                return output
            except GitlabGetError:
                LOG.debug("Gitlab API GET request failed ")
                return output
        except ValueError:
            intid = gitlab_id_search(obj, objid)
            call = getattr(obj, 'get')
            try:
                response = call(intid)
                output = response.attributes
                return output
            except GitlabGetError:
                LOG.debug("Gitlab API GET request failed ")
                return output
