class PipelineError(Exception):
    """Safe actionable error for the public API."""
    def __init__(self,message,code='processing_failed',retryable=False):
        super().__init__(message)
        self.code=code
        self.retryable=retryable

class FrameUnavailable(PipelineError):
    def __init__(self,message='IRSA could not deliver this observation after bounded retries.',status=None):
        super().__init__(message,'archive_frame_unavailable',True)
        self.status=status
