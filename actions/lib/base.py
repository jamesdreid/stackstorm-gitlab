import gitlab

from st2common.runners.base_action import Action

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
        
        # Only one of the 3 tokens should be defined. If multiple token types are supplied,
        # a token will be selected using the following precedence:
        #    Private > OAuth > Job
    
        self.private_token = self.config.get('private_token', None)
        self.oauth_token = self.config.get('oauth_token', None)
        self.job_token = self.config.get('job_token', None)

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


        